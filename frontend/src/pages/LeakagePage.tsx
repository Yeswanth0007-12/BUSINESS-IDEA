import { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import { apiClient } from '../services/api';
import toast from 'react-hot-toast';

interface LeakageInsight {
  category: string;
  total_leakage: number;
  product_count: number;
  percentage_of_total: number;
}

const LeakagePage = () => {
  const [insights, setInsights] = useState<LeakageInsight[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    fetchLeakageInsights();
  }, []);

  const fetchLeakageInsights = async () => {
    setIsLoading(true);
    try {
      const data = await apiClient.getLeakage();
      setInsights(data);
    } catch (error: any) {
      console.error('Failed to fetch leakage insights:', error);
      toast.error('Failed to load leakage insights');
    } finally {
      setIsLoading(false);
    }
  };

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(value);
  };

  // Colors for Pareto chart
  const COLORS = ['#3b82f6', '#8b5cf6', '#ec4899', '#f59e0b', '#10b981', '#6366f1'];

  if (isLoading) {
    return (
      <div className="min-h-screen bg-slate-900 flex items-center justify-center">
        <div className="text-center">
          <svg
            className="animate-spin h-12 w-12 text-blue-500 mx-auto mb-4"
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
          >
            <circle
              className="opacity-25"
              cx="12"
              cy="12"
              r="10"
              stroke="currentColor"
              strokeWidth="4"
            ></circle>
            <path
              className="opacity-75"
              fill="currentColor"
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
            ></path>
          </svg>
          <p className="text-slate-400">Loading leakage insights...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-900 p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-slate-100 mb-2">Cost Leakage Analysis</h1>
          <p className="text-slate-400">
            Identify categories with the highest packaging cost inefficiencies
          </p>
        </div>

        {insights.length === 0 ? (
          <div className="bg-slate-800 rounded-lg p-12 border border-slate-700 text-center">
            <svg
              className="w-16 h-16 text-slate-600 mx-auto mb-4"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
              />
            </svg>
            <p className="text-slate-400 text-lg mb-2">No leakage data available</p>
            <p className="text-slate-500 text-sm">
              Run an optimization to see cost leakage by category
            </p>
          </div>
        ) : (
          <div className="space-y-6">
            {/* Pareto Chart */}
            <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
              <h2 className="text-xl font-bold text-slate-100 mb-6">
                Cost Leakage by Category (Pareto Analysis)
              </h2>
              <ResponsiveContainer width="100%" height={400}>
                <BarChart data={insights}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                  <XAxis
                    dataKey="category"
                    stroke="#94a3b8"
                    tick={{ fill: '#94a3b8' }}
                    angle={-45}
                    textAnchor="end"
                    height={100}
                  />
                  <YAxis
                    stroke="#94a3b8"
                    tick={{ fill: '#94a3b8' }}
                    tickFormatter={(value) => `$${value}`}
                  />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: '#1e293b',
                      border: '1px solid #334155',
                      borderRadius: '8px',
                      color: '#f1f5f9',
                    }}
                    formatter={(value: number) => [formatCurrency(value), 'Annual Leakage']}
                  />
                  <Bar dataKey="total_leakage" radius={[8, 8, 0, 0]}>
                    {insights.map((_entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>

            {/* Leakage Table */}
            <div className="bg-slate-800 rounded-lg border border-slate-700 overflow-hidden">
              <div className="p-6 border-b border-slate-700">
                <h2 className="text-xl font-bold text-slate-100">Detailed Breakdown</h2>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-slate-700">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-slate-300 uppercase tracking-wider">
                        Category
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-slate-300 uppercase tracking-wider">
                        Product Count
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-slate-300 uppercase tracking-wider">
                        Annual Leakage
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-slate-300 uppercase tracking-wider">
                        % of Total
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-slate-300 uppercase tracking-wider">
                        Priority
                      </th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-700">
                    {insights.map((insight, index) => (
                      <tr key={insight.category} className="hover:bg-slate-700/50 transition">
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-slate-100">
                          <div className="flex items-center">
                            <div
                              className="w-3 h-3 rounded-full mr-3"
                              style={{ backgroundColor: COLORS[index % COLORS.length] }}
                            ></div>
                            {insight.category}
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-300">
                          {insight.product_count}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-red-400 font-medium">
                          {formatCurrency(insight.total_leakage)}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-300">
                          {insight.percentage_of_total.toFixed(1)}%
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm">
                          {index === 0 && (
                            <span className="px-2 py-1 text-xs font-medium bg-red-500/20 text-red-400 rounded">
                              High
                            </span>
                          )}
                          {index === 1 && (
                            <span className="px-2 py-1 text-xs font-medium bg-orange-500/20 text-orange-400 rounded">
                              Medium
                            </span>
                          )}
                          {index > 1 && (
                            <span className="px-2 py-1 text-xs font-medium bg-blue-500/20 text-blue-400 rounded">
                              Low
                            </span>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Insights Summary */}
            <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
              <h2 className="text-xl font-bold text-slate-100 mb-4">Key Insights</h2>
              <div className="space-y-3">
                {insights.length > 0 && (
                  <>
                    <div className="flex items-start">
                      <svg
                        className="w-5 h-5 text-blue-400 mr-3 mt-0.5 flex-shrink-0"
                        fill="currentColor"
                        viewBox="0 0 20 20"
                      >
                        <path
                          fillRule="evenodd"
                          d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z"
                          clipRule="evenodd"
                        />
                      </svg>
                      <p className="text-slate-300">
                        <span className="font-medium text-slate-100">{insights[0].category}</span>{' '}
                        category has the highest cost leakage at{' '}
                        <span className="font-medium text-red-400">
                          {formatCurrency(insights[0].total_leakage)}
                        </span>{' '}
                        annually ({insights[0].percentage_of_total.toFixed(1)}% of total).
                      </p>
                    </div>
                    {insights.length > 1 && (
                      <div className="flex items-start">
                        <svg
                          className="w-5 h-5 text-blue-400 mr-3 mt-0.5 flex-shrink-0"
                          fill="currentColor"
                          viewBox="0 0 20 20"
                        >
                          <path
                            fillRule="evenodd"
                            d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z"
                            clipRule="evenodd"
                          />
                        </svg>
                        <p className="text-slate-300">
                          Focus optimization efforts on the top{' '}
                          {Math.min(2, insights.length)} categories to capture{' '}
                          <span className="font-medium text-slate-100">
                            {insights
                              .slice(0, Math.min(2, insights.length))
                              .reduce((sum, i) => sum + i.percentage_of_total, 0)
                              .toFixed(1)}
                            %
                          </span>{' '}
                          of potential savings.
                        </p>
                      </div>
                    )}
                    <div className="flex items-start">
                      <svg
                        className="w-5 h-5 text-blue-400 mr-3 mt-0.5 flex-shrink-0"
                        fill="currentColor"
                        viewBox="0 0 20 20"
                      >
                        <path
                          fillRule="evenodd"
                          d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z"
                          clipRule="evenodd"
                        />
                      </svg>
                      <p className="text-slate-300">
                        Total of{' '}
                        <span className="font-medium text-slate-100">
                          {insights.reduce((sum, i) => sum + i.product_count, 0)}
                        </span>{' '}
                        products analyzed across {insights.length} categories.
                      </p>
                    </div>
                  </>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default LeakagePage;
