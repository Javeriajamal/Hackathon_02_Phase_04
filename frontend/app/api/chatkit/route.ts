import { NextRequest } from 'next/server';
import OpenAI from 'openai';

// Create OpenAI client configured for OpenRouter
const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY, // Your OpenRouter API key
  baseURL: process.env.NEXT_PUBLIC_OPENAI_DOMAIN_KEY, // OpenRouter endpoint
});

// Helper function to make authenticated requests to the task API
async function makeTaskApiRequest(url: string, token: string, options: RequestInit = {}) {
  const baseUrl = 'http://127.0.0.1:8001/api/v1';

  const response = await fetch(`${baseUrl}${url}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
      ...options.headers,
    },
  });

  if (!response.ok) {
    throw new Error(`Task API request failed: ${response.statusText}`);
  }

  return response.json();
}

export async function POST(request: NextRequest) {
  try {
    const { messages, userId, authToken } = await request.json();

    // Prepare messages for OpenRouter
    const openRouterMessages = messages.map((msg: any) => ({
      role: msg.role,
      content: msg.content,
    }));

    // Call OpenRouter Chat Completions API to analyze the user request
    const analysisResponse = await openai.chat.completions.create({
      model: 'openai/gpt-3.5-turbo',
      messages: [
        {
          role: 'system',
          content: `You are a helpful assistant that analyzes user requests to determine if they want to perform task operations.
          Respond with a JSON object containing:
          - "intent": the type of operation (add_task, update_task, delete_task, complete_task, get_tasks, other)
          - "task_details": any relevant details like task title, description, or ID
          - "response": what you would normally say to the user

          Examples:
          - User: "Add a task: buy groceries" -> {intent: "add_task", task_details: {title: "buy groceries"}, response: "I've added the task 'buy groceries' for you."}
          - User: "Show my tasks" -> {intent: "get_tasks", task_details: {}, response: "Here are your tasks..."}
          - User: "Complete task 1" -> {intent: "complete_task", task_details: {id: "1"}, response: "I've marked task 1 as complete."}`
        },
        ...openRouterMessages
      ],
      temperature: 0.3,
      response_format: { type: "json_object" }
    });

    let aiAnalysis;
    try {
      aiAnalysis = JSON.parse(analysisResponse.choices[0]?.message?.content || '{}');
    } catch (parseError) {
      // If JSON parsing fails, create a fallback analysis
      const lastMessage = openRouterMessages[openRouterMessages.length - 1]?.content || '';
      aiAnalysis = {
        intent: 'other',
        task_details: {},
        response: "I processed your request."
      };
    }

    let aiResponse = aiAnalysis.response || "I processed your request.";
    let taskOperation = '';

    // Perform the actual task operation based on the AI's analysis
    if (authToken && aiAnalysis.intent !== 'other' && aiAnalysis.intent !== 'get_tasks') {
      try {
        switch (aiAnalysis.intent) {
          case 'add_task':
            if (aiAnalysis.task_details?.title) {
              await makeTaskApiRequest('/tasks', authToken, {
                method: 'POST',
                body: JSON.stringify({
                  title: aiAnalysis.task_details.title,
                  description: aiAnalysis.task_details.description || '',
                  status: aiAnalysis.task_details.status || 'pending',
                  priority: aiAnalysis.task_details.priority || 'medium'
                })
              });
              aiResponse = `I've added the task "${aiAnalysis.task_details.title}" for you.`;
              taskOperation = 'add_task';
            }
            break;

          case 'update_task':
            if (aiAnalysis.task_details?.id || aiAnalysis.task_details?.title) {
              // If no ID provided, find task by title
              let taskId = aiAnalysis.task_details.id;
              if (!taskId) {
                const tasksResponse = await makeTaskApiRequest('/tasks', authToken, { method: 'GET' });
                if (tasksResponse && tasksResponse.tasks && Array.isArray(tasksResponse.tasks)) {
                  const searchTerm = aiAnalysis.task_details.title.toLowerCase().trim();
                  const matchedTask = tasksResponse.tasks.find((task: any) =>
                    task.title.toLowerCase().includes(searchTerm) ||
                    searchTerm.includes(task.title.toLowerCase())
                  );
                  if (matchedTask) {
                    taskId = matchedTask.id;
                  }
                }
              }

              if (taskId) {
                // Construct update payload from AI analysis and user request
                const updatePayload: any = {};

                // Extract update details from the AI analysis and original request
                if (aiAnalysis.task_details.title) {
                  updatePayload.title = aiAnalysis.task_details.title;
                }

                // Try to extract other fields from the original user message
                const lastMessage = openRouterMessages[openRouterMessages.length - 1]?.content || '';

                // Check for priority keywords
                if (lastMessage.toLowerCase().includes('priority') && (lastMessage.toLowerCase().includes('high') || lastMessage.toLowerCase().includes('medium') || lastMessage.toLowerCase().includes('low'))) {
                  if (lastMessage.toLowerCase().includes('high')) updatePayload.priority = 'high';
                  else if (lastMessage.toLowerCase().includes('medium')) updatePayload.priority = 'medium';
                  else if (lastMessage.toLowerCase().includes('low')) updatePayload.priority = 'low';
                  else if (lastMessage.toLowerCase().includes('urgent')) updatePayload.priority = 'urgent';
                }

                // Check for status keywords
                if (lastMessage.toLowerCase().includes('status') && (lastMessage.toLowerCase().includes('pending') || lastMessage.toLowerCase().includes('completed') || lastMessage.toLowerCase().includes('in_progress'))) {
                  if (lastMessage.toLowerCase().includes('completed')) updatePayload.status = 'completed';
                  else if (lastMessage.toLowerCase().includes('in progress') || lastMessage.toLowerCase().includes('in_progress')) updatePayload.status = 'in_progress';
                  else if (lastMessage.toLowerCase().includes('pending')) updatePayload.status = 'pending';
                }

                // Check for description updates
                if (lastMessage.toLowerCase().includes('description') || lastMessage.toLowerCase().includes('to be') || lastMessage.toLowerCase().includes('change to')) {
                  // Extract description after keywords like "to be", "to", "description:"
                  const descMatch = lastMessage.match(/(?:to be|to|description:)\s*(.+)/i);
                  if (descMatch && descMatch[1]) {
                    updatePayload.description = descMatch[1].trim();
                  }
                }

                // If no specific update fields were identified, use whatever is in aiAnalysis.task_details.update
                if (Object.keys(updatePayload).length === 0 && aiAnalysis.task_details.update) {
                  Object.assign(updatePayload, aiAnalysis.task_details.update);
                }

                await makeTaskApiRequest(`/tasks/${taskId}`, authToken, {
                  method: 'PUT',
                  body: JSON.stringify(updatePayload)
                });
                aiResponse = `I've updated task ${aiAnalysis.task_details.title || taskId}.`;
                taskOperation = 'update_task';
              } else {
                aiResponse = `I couldn't find the task "${aiAnalysis.task_details.title}" to update.`;
              }
            }
            break;

          case 'delete_task':
            if (aiAnalysis.task_details?.id || aiAnalysis.task_details?.title) {
              // If no ID provided, find task by title
              let taskId = aiAnalysis.task_details.id;
              if (!taskId) {
                const tasksResponse = await makeTaskApiRequest('/tasks', authToken, { method: 'GET' });
                if (tasksResponse && tasksResponse.tasks && Array.isArray(tasksResponse.tasks)) {
                  const searchTerm = aiAnalysis.task_details.title.toLowerCase().trim();
                  const matchedTask = tasksResponse.tasks.find((task: any) =>
                    task.title.toLowerCase().includes(searchTerm) ||
                    searchTerm.includes(task.title.toLowerCase())
                  );
                  if (matchedTask) {
                    taskId = matchedTask.id;
                  }
                }
              }

              if (taskId) {
                await makeTaskApiRequest(`/tasks/${taskId}`, authToken, {
                  method: 'DELETE'
                });
                aiResponse = `I've deleted task ${aiAnalysis.task_details.title || taskId}.`;
                taskOperation = 'delete_task';
              } else {
                aiResponse = `I couldn't find the task "${aiAnalysis.task_details.title}" to delete.`;
              }
            }
            break;

          case 'complete_task':
            if (aiAnalysis.task_details?.id || aiAnalysis.task_details?.title) {
              // If no ID provided, find task by title
              let taskId = aiAnalysis.task_details.id;
              if (!taskId) {
                const tasksResponse = await makeTaskApiRequest('/tasks', authToken, { method: 'GET' });
                if (tasksResponse && tasksResponse.tasks && Array.isArray(tasksResponse.tasks)) {
                  const searchTerm = aiAnalysis.task_details.title.toLowerCase().trim();
                  const matchedTask = tasksResponse.tasks.find((task: any) =>
                    task.title.toLowerCase().includes(searchTerm) ||
                    searchTerm.includes(task.title.toLowerCase())
                  );
                  if (matchedTask) {
                    taskId = matchedTask.id;
                  }
                }
              }

              if (taskId) {
                await makeTaskApiRequest(`/tasks/${taskId}/toggle-completion`, authToken, {
                  method: 'PATCH'
                });
                aiResponse = `I've marked task ${aiAnalysis.task_details.title || taskId} as complete.`;
                taskOperation = 'complete_task';
              } else {
                aiResponse = `I couldn't find the task "${aiAnalysis.task_details.title}" to complete.`;
              }
            }
            break;
        }
      } catch (taskError) {
        console.error('Task API Error:', taskError);
        aiResponse = `I had trouble processing your task request: ${(taskError as Error).message}. I've processed your request but couldn't update the task system.`;
        taskOperation = ''; // Don't trigger task update on error
      }
    }
    // For get_tasks intent, we don't perform an operation but let the AI handle the response
    else if (authToken && aiAnalysis.intent === 'get_tasks') {
      try {
        // Fetch user's tasks and include them in the response
        const response = await makeTaskApiRequest('/tasks', authToken, {
          method: 'GET'
        });
        if (response && response.tasks && Array.isArray(response.tasks)) {
          const formattedTasks = response.tasks.map((task: any) => {
            // Clean the title by removing prefixes like "a task:", "task:"
            let cleanTitle = task.title.replace(/^(a task:|task:)\s*/i, '');
            return `• ${cleanTitle} — ${task.status}`;
          }).join('\n');
          aiResponse = `Here are your tasks:\n${formattedTasks || 'You have no tasks.'}`;
        }
      } catch (taskError) {
        console.error('Task API Error:', taskError);
        aiResponse = `I had trouble retrieving your tasks: ${(taskError as Error).message}. Here's what I understood from your request.`;
      }
    }

    // Return the response
    const jsonResponse = new Response(
      JSON.stringify({
        id: `ai-${Date.now()}`,
        role: 'assistant',
        content: aiResponse,
        timestamp: new Date().toISOString(),
      }),
      {
        status: 200,
        headers: {
          'Content-Type': 'application/json',
          'x-task-operation': taskOperation // Include task operation in headers for client to detect
        }
      }
    );

    return jsonResponse;
  } catch (error) {
    console.error('OpenRouter API Error:', error);

    // Return an error response that maintains the expected format
    return new Response(
      JSON.stringify({
        id: `ai-${Date.now()}`,
        role: 'assistant',
        content: "I'm having trouble connecting to the AI service. Please try again.",
        timestamp: new Date().toISOString(),
      }),
      {
        status: 500,
        headers: {
          'Content-Type': 'application/json',
          'x-task-operation': '' // No task operation in error case
        }
      }
    );
  }
}