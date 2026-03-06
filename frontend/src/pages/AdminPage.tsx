import { useState, useEffect } from 'react';
import api from '../services/api';

interface User {
  id: number;
  email: string;
  company_id: number;
  role: string;
  created_at: string;
}

const AdminPage = () => {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = async () => {
    try {
      setError(null);
      const users = await api.getCompanyUsers();
      setUsers(users);
    } catch (error: any) {
      console.error('Error fetching users:', error);
      if (error.response?.status === 403) {
        setError('You do not have permission to access this page. Admin role required.');
      } else if (error.response?.status === 500) {
        setError('Server error. Please ensure you have been assigned an admin role.');
      } else {
        setError('Failed to load users. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  const exportData = async (type: string) => {
    try {
      let response;
      if (type === 'products') {
        response = await api.exportProducts();
      } else if (type === 'boxes') {
        response = await api.exportBoxes();
      } else if (type === 'optimizations') {
        response = await api.exportOptimizations();
      } else {
        return;
      }
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `${type}_${new Date().toISOString().split('T')[0]}.csv`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (error) {
      console.error(`Error exporting ${type}:`, error);
      alert(`Failed to export ${type}`);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-slate-400">Loading...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold text-slate-100">Admin Panel</h1>
          <p className="mt-2 text-slate-400">Manage users and export data</p>
        </div>
        <div className="bg-red-900/20 border border-red-700 rounded-lg p-6">
          <div className="flex items-center">
            <svg className="w-6 h-6 text-red-400 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
            <div>
              <h3 className="text-lg font-semibold text-red-400">Access Denied</h3>
              <p className="mt-1 text-slate-300">{error}</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-slate-100">Admin Panel</h1>
        <p className="mt-2 text-slate-400">Manage users and export data</p>
      </div>

      {/* Export Section */}
      <div className="bg-slate-800 rounded-lg border border-slate-700 p-6">
        <h2 className="text-xl font-semibold text-slate-100 mb-4">Data Export</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <button
            onClick={() => exportData('products')}
            className="flex items-center justify-center bg-blue-600 hover:bg-blue-700 text-white font-medium py-3 px-4 rounded-lg transition-colors"
          >
            <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M9 19l3 3m0 0l3-3m-3 3V10" />
            </svg>
            Export Products
          </button>
          <button
            onClick={() => exportData('boxes')}
            className="flex items-center justify-center bg-green-600 hover:bg-green-700 text-white font-medium py-3 px-4 rounded-lg transition-colors"
          >
            <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M9 19l3 3m0 0l3-3m-3 3V10" />
            </svg>
            Export Boxes
          </button>
          <button
            onClick={() => exportData('optimizations')}
            className="flex items-center justify-center bg-purple-600 hover:bg-purple-700 text-white font-medium py-3 px-4 rounded-lg transition-colors"
          >
            <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M9 19l3 3m0 0l3-3m-3 3V10" />
            </svg>
            Export Optimizations
          </button>
        </div>
      </div>

      {/* Users Section */}
      <div className="bg-slate-800 rounded-lg border border-slate-700 p-6">
        <h2 className="text-xl font-semibold text-slate-100 mb-4">Company Users</h2>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-slate-700">
                <th className="text-left py-3 px-4 text-sm font-semibold text-slate-300">Email</th>
                <th className="text-left py-3 px-4 text-sm font-semibold text-slate-300">Role</th>
                <th className="text-left py-3 px-4 text-sm font-semibold text-slate-300">Joined</th>
              </tr>
            </thead>
            <tbody>
              {users.map((user) => (
                <tr key={user.id} className="border-b border-slate-700/50 hover:bg-slate-700/30">
                  <td className="py-3 px-4 text-sm text-slate-300">{user.email}</td>
                  <td className="py-3 px-4">
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                      user.role === 'admin' || user.role === 'ADMIN'
                        ? 'bg-red-900/30 text-red-400'
                        : user.role === 'manager' || user.role === 'MANAGER'
                        ? 'bg-blue-900/30 text-blue-400'
                        : user.role === 'editor' || user.role === 'EDITOR'
                        ? 'bg-green-900/30 text-green-400'
                        : 'bg-slate-700 text-slate-300'
                    }`}>
                      {user.role?.toUpperCase() || 'VIEWER'}
                    </span>
                  </td>
                  <td className="py-3 px-4 text-sm text-slate-400">
                    {new Date(user.created_at).toLocaleDateString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default AdminPage;
