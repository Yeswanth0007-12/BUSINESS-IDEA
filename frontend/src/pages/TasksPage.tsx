import { useState } from 'react';
import api from '../services/api';

interface TaskStatus {
  task_id: string;
  task_type: string;
  status: string;
  progress: number;
  created_at: string;
  started_at?: string;
  completed_at?: string;
  result_id?: number;
  error_message?: string;
}

const TasksPage = () => {
  const [taskId, setTaskId] = useState('');
  const [taskStatus, setTaskStatus] = useState<TaskStatus | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const checkTaskStatus = async () => {
    if (!taskId.trim()) {
      setError('Please enter a task ID');
      return;
    }

    try {
      setLoading(true);
      setError('');
      const data = await api.getTaskStatus(taskId);
      setTaskStatus(data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to fetch task status');
      setTaskStatus(null);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'completed':
        return 'text-green-400 bg-green-400/10';
      case 'processing':
      case 'running':
        return 'text-blue-400 bg-blue-400/10';
      case 'pending':
      case 'queued':
        return 'text-yellow-400 bg-yellow-400/10';
      case 'failed':
        return 'text-red-400 bg-red-400/10';
      default:
        return 'text-slate-400 bg-slate-400/10';
    }
  };

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-slate-100">Task Status</h1>
        <p className="mt-2 text-slate-400">Track asynchronous optimization tasks</p>
      </div>

      {/* Task ID Input */}
      <div className="bg-slate-800 rounded-lg border border-slate-700 p-6">
        <label className="block text-sm font-medium text-slate-300 mb-2">Task ID</label>
        <div className="flex gap-4">
          <input
            type="text"
            value={taskId}
            onChange={(e) => setTaskId(e.target.value)}
            placeholder="Enter task UUID"
            className="flex-1 px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg text-slate-100 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <button
            onClick={checkTaskStatus}
            disabled={loading}
            className="px-6 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-slate-600 text-white font-medium rounded-lg transition-colors"
          >
            {loading ? 'Checking...' : 'Check Status'}
          </button>
        </div>
        {error && (
          <p className="mt-2 text-sm text-red-400">{error}</p>
        )}
      </div>

      {/* Task Status Display */}
      {taskStatus && (
        <div className="bg-slate-800 rounded-lg border border-slate-700 p-6 space-y-4">
          <h2 className="text-xl font-semibold text-slate-100">Task Details</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <p className="text-sm text-slate-400">Task ID</p>
              <p className="text-sm font-mono text-slate-100 break-all">{taskStatus.task_id}</p>
            </div>
            
            <div>
              <p className="text-sm text-slate-400">Task Type</p>
              <p className="text-sm text-slate-100">{taskStatus.task_type}</p>
            </div>
            
            <div>
              <p className="text-sm text-slate-400">Status</p>
              <span className={`inline-block px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(taskStatus.status)}`}>
                {taskStatus.status}
              </span>
            </div>
            
            <div>
              <p className="text-sm text-slate-400">Progress</p>
              <div className="mt-1">
                <div className="w-full bg-slate-700 rounded-full h-2">
                  <div
                    className="bg-blue-500 h-2 rounded-full transition-all"
                    style={{ width: `${taskStatus.progress}%` }}
                  />
                </div>
                <p className="text-xs text-slate-400 mt-1">{taskStatus.progress}%</p>
              </div>
            </div>
            
            <div>
              <p className="text-sm text-slate-400">Created At</p>
              <p className="text-sm text-slate-100">
                {new Date(taskStatus.created_at).toLocaleString()}
              </p>
            </div>
            
            {taskStatus.started_at && (
              <div>
                <p className="text-sm text-slate-400">Started At</p>
                <p className="text-sm text-slate-100">
                  {new Date(taskStatus.started_at).toLocaleString()}
                </p>
              </div>
            )}
            
            {taskStatus.completed_at && (
              <div>
                <p className="text-sm text-slate-400">Completed At</p>
                <p className="text-sm text-slate-100">
                  {new Date(taskStatus.completed_at).toLocaleString()}
                </p>
              </div>
            )}
            
            {taskStatus.result_id && (
              <div>
                <p className="text-sm text-slate-400">Result ID</p>
                <p className="text-sm text-slate-100">{taskStatus.result_id}</p>
              </div>
            )}
          </div>
          
          {taskStatus.error_message && (
            <div className="mt-4 p-4 bg-red-900/20 border border-red-700 rounded-lg">
              <p className="text-sm font-medium text-red-400">Error</p>
              <p className="text-sm text-red-300 mt-1">{taskStatus.error_message}</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default TasksPage;
