import { useState } from 'react';

interface Filters {
  status: string;
  priority: string;
  search: string;
}

interface TaskFiltersProps {
  filters: Filters;
  onFilterChange: (filters: { status?: string; priority?: string; search?: string }) => void;
  taskCount: number;
}

export default function TaskFilters({ filters, onFilterChange, taskCount }: TaskFiltersProps) {
  const [searchInput, setSearchInput] = useState(filters.search);

  const handleSearchChange = (value: string) => {
    setSearchInput(value);
    // Update filters after a short delay to avoid excessive API calls
    setTimeout(() => {
      if (value !== searchInput) {
        onFilterChange({ search: value });
      }
    }, 300);
  };

  return (
    <div className="p-4 border-b border-gray-200 bg-violet-500/5">
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div>
          <label htmlFor="search" className="block text-sm font-medium text-gray-400  mb-1">
            Search
          </label>
          <input
            type="text"
            id="search"
            value={searchInput}
            onChange={(e) => handleSearchChange(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 text-gray-200 bg-violet-950/5 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            placeholder="Search tasks..."
          />
        </div>

        <div>
          <label htmlFor="status" className="block text-sm font-medium text-gray-400 mb-1">
            Status
          </label>
          <select
            id="status"
            value={filters.status}
            onChange={(e) => onFilterChange({ status: e.target.value })}
            className="w-full px-3 py-2 border border-gray-300 text-gray-300 bg-violet-950/5 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="all">All Statuses</option>
            <option value="pending">Pending</option>
            <option value="completed">Completed</option>
          </select>
        </div>

        <div>
          <label htmlFor="priority" className="block text-sm font-medium text-gray-400 mb-1">
            Priority
          </label>
          <select
            id="priority"
            value={filters.priority}
            onChange={(e) => onFilterChange({ priority: e.target.value })}
            className="w-full px-3 py-2 border border-gray-300 text-gray-300 bg-violet-950/5 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="all">All Priorities</option>
            <option value="low">Low</option>
            <option value="medium">Medium</option>
            <option value="high">High</option>
          </select>
        </div>

        <div className="flex items-end">
          <div className="text-sm text-gray-500">
            {taskCount} {taskCount === 1 ? 'task' : 'tasks'}
          </div>
        </div>
      </div>
    </div>
  );
}