import { Task } from '@/types/task';
import TaskItem from '@/components/task/TaskItem';
import TaskFilters from '@/components/task/TaskFilters';
import Pagination from '@/components/task/Pagination';
import { useState, useEffect } from 'react';

interface TaskListProps {
  tasks: Task[];
  onUpdate: () => void;
}

export default function TaskList({ tasks, onUpdate }: TaskListProps) {
  const [filteredTasks, setFilteredTasks] = useState<Task[]>(tasks);
  const [currentPage, setCurrentPage] = useState(1);
  const [tasksPerPage] = useState(10);
  const [filters, setFilters] = useState({
    status: 'all',
    priority: 'all',
    search: ''
  });

  useEffect(() => {
    let result = [...tasks];

    // Apply search filter
    if (filters.search) {
      result = result.filter(task =>
        task.title.toLowerCase().includes(filters.search.toLowerCase()) ||
        (task.description && task.description.toLowerCase().includes(filters.search.toLowerCase()))
      );
    }

    // Apply status filter
    if (filters.status !== 'all') {
      result = result.filter(task =>
        filters.status === 'completed' ? task.is_completed : !task.is_completed
      );
    }

    // Apply priority filter
    if (filters.priority !== 'all') {
      result = result.filter(task => task.priority === filters.priority);
    }

    setFilteredTasks(result);
    setCurrentPage(1); // Reset to first page when filters change
  }, [filters, tasks]);

  // Pagination calculations
  const indexOfLastTask = currentPage * tasksPerPage;
  const indexOfFirstTask = indexOfLastTask - tasksPerPage;
  const currentTasks = filteredTasks.slice(indexOfFirstTask, indexOfLastTask);
  const totalPages = Math.ceil(filteredTasks.length / tasksPerPage);

  const handleFilterChange = (newFilters: { status?: string; priority?: string; search?: string }) => {
    setFilters(prev => ({ ...prev, ...newFilters }));
  };

  const handlePageChange = (page: number) => {
    setCurrentPage(page);
  };

  return (
    <div className="glass backdrop-blur-lg rounded-xl overflow-hidden border border-violet-500/30 shadow-lg shadow-violet-500/20 dark:shadow-violet-500/30">
      <TaskFilters
        filters={filters}
        onFilterChange={handleFilterChange}
        taskCount={filteredTasks.length}
      />

      <div className="divide-y divide-violet-500/20 dark:divide-violet-500/30">
        {currentTasks.length > 0 ? (
          currentTasks.map(task => (
            <TaskItem
              key={task.id}
              task={task}
              onUpdate={onUpdate}
            />
          ))
        ) : (
          <div className="text-center py-12">
            <div className="mx-auto flex items-center justify-center h-12 w-12 rounded-full glass backdrop-blur-md">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-cyan-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
              </svg>
            </div>
            <h3 className="mt-4 text-lg font-medium text-gray-900 dark:text-white">No tasks</h3>
            <p className="mt-2 text-gray-500 dark:text-gray-400">
              {tasks.length === 0
                ? 'Get started by creating your first task.'
                : 'No tasks match your current filters. Try adjusting your search or filters.'}
            </p>
          </div>
        )}
      </div>

      {totalPages > 1 && (
        <div className="border-t border-violet-500/20 dark:border-violet-500/30 glass backdrop-blur-md px-4 py-3 sm:px-6">
          <Pagination
            currentPage={currentPage}
            totalPages={totalPages}
            onPageChange={handlePageChange}
          />
        </div>
      )}
    </div>
  );
}