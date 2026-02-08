interface TaskStatusToggleProps {
  isCompleted: boolean;
  onToggle: () => void;
}

export default function TaskStatusToggle({ isCompleted, onToggle }: TaskStatusToggleProps) {
  return (
    <button
      onClick={onToggle}
      className={`relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 ${
        isCompleted ? 'bg-green-500' : 'bg-gray-300'
      }`}
      role="switch"
      aria-checked={isCompleted}
      aria-label={isCompleted ? 'Mark as incomplete' : 'Mark as complete'}
    >
      <span className="sr-only">{isCompleted ? 'Task completed' : 'Task incomplete'}</span>
      <span
        aria-hidden="true"
        className={`pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out ${
          isCompleted ? 'translate-x-5' : 'translate-x-0'
        }`}
      />
    </button>
  );
}