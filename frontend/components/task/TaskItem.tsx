import { useState } from 'react';
import { Task } from '@/types/task';
import TaskEditForm from '@/components/task/TaskEditForm';
import TaskDeleteDialog from '@/components/task/TaskDeleteDialog';
import TaskStatusToggle from '@/components/task/TaskStatusToggle';
import { updateTask, deleteTask } from '@/services/api/taskService';

interface TaskItemProps {
  task: Task;
  onUpdate: () => void;
}

export default function TaskItem({ task, onUpdate }: TaskItemProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);

  const handleUpdateTask = async (updatedTask: Omit<Task, 'created_at' | 'updated_at' | 'user_id'>) => {
    try {
      await updateTask(task.id, updatedTask);
      setIsEditing(false);
      onUpdate();
    } catch (error) {
      console.error('Error updating task:', error);
      alert('Failed to update task. Please try again.');
    }
  };

  const handleDeleteTask = async () => {
    try {
      await deleteTask(task.id);
      setIsDeleteDialogOpen(false);
      onUpdate();
    } catch (error) {
      console.error('Error deleting task:', error);
      alert('Failed to delete task. Please try again.');
    }
  };

  const handleToggleStatus = async () => {
    try {
      await updateTask(task.id, { ...task, is_completed: !task.is_completed });
      onUpdate();
    } catch (error) {
      console.error('Error toggling task status:', error);
      alert('Failed to update task status. Please try again.');
    }
  };

  // Format due date if it exists
  const formattedDueDate = task.due_date ? new Date(task.due_date).toLocaleDateString() : 'No due date';

  return (
    <div className="p-6 hover:bg-violet-500/10 transition-colors duration-200 border-b border-violet-500/20 last:border-b-0 task-card">
      {isEditing ? (
        <TaskEditForm
          task={task}
          onSubmit={handleUpdateTask}
          onCancel={() => setIsEditing(false)}
        />
      ) : (
        <div className="flex items-start">
          <div className="flex-shrink-0 pt-1">
            <TaskStatusToggle
              isCompleted={task.is_completed}
              onToggle={handleToggleStatus}
            />
          </div>

          <div className="flex-grow min-w-0 ml-4">
            <div className="flex items-start justify-between">
              <div className="flex-1 min-w-0">
                <h3 className={`text-lg font-semibold ${task.is_completed ? 'line-through text-gray-500 dark:text-gray-400' : 'text-gray-900 dark:text-white'}`}>
                  {task.title}
                </h3>

                {task.description && (
                  <p className={`mt-2 text-sm ${task.is_completed ? 'text-gray-400 dark:text-gray-500' : 'text-gray-600 dark:text-gray-300'}`}>
                    {task.description}
                  </p>
                )}

                <div className="mt-3 flex flex-wrap gap-2">
                  <span className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-medium ${
                    task.priority === 'low'
                      ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300'
                      : task.priority === 'medium'
                        ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300'
                        : 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300'
                  }`}>
                    {task.priority}
                  </span>
                  <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300">
                    Due: {formattedDueDate}
                  </span>
                </div>
              </div>

              <div className="flex space-x-3 ml-4">
                <button
                  onClick={() => setIsEditing(true)}
                  className="text-cyan-600 hover:text-cyan-400 p-1 rounded-full hover:bg-cyan-500/10 transition-colors duration-200"
                  title="Edit task"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                    <path d="M13.586 3.586a2 2 0 112.828 2.828l-.793.793-2.828-2.828.793-.793zM11.379 5.793L3 14.172V17h2.828l8.38-8.379-2.83-2.828z" />
                  </svg>
                </button>
                <button
                  onClick={() => setIsDeleteDialogOpen(true)}
                  className="text-pink-600 hover:text-pink-400 p-1 rounded-full hover:bg-pink-500/10 transition-colors duration-200"
                  title="Delete task"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z" clipRule="evenodd" />
                  </svg>
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {isDeleteDialogOpen && (
        <TaskDeleteDialog
          task={task}
          onConfirm={handleDeleteTask}
          onCancel={() => setIsDeleteDialogOpen(false)}
        />
      )}
    </div>
  );
}