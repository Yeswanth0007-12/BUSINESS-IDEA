import { useState } from 'react';
import { apiClient } from '../services/api';
import toast from 'react-hot-toast';

interface OptimizationResult {
  product_id: number;
  product_name: string;
  current_box_name: string;
  recommended_box_name: string;
  current_cost: number;
  recommended_cost: number;
  savings: number;
  savings_percentage: number;
}

interface OptimizationSummary {
  total_products_analyzed: number;
  products_with_savings: number;
  total_monthly_savings: number;
  total_annual_savings: number;
  results: OptimizationResult[];
  run_id: number;
  timestamp: string;
}

const OptimizePage = () => {
  const [isRunning, setIsRunning] = useState(false);
  const [summary, setSummary] = useState<OptimizationSummary | null>(null);

  const handleRunOptimization = async () => {
    setIsRunning(true);
    try {
      const result = await apiClient.runOptimization();
      setSummary(result);
      toast.success('Optimization completed successfully!');
    } catch (error: any) {
      console.error('Optimization failed:', error);
      const errorMessage = error.response?.data?.detail || 'Optimization failed';
      toast.error(errorMessage);
    } finally {
      setIsRunning(false);
    }
  };

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
    }).format(value);
  };

  return (
    <div className="min-h-screen bg-slate-900 p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold text-slate-100 mb-2">Optimize Packaging</h1>
            <p className="text-slate-400">Run optimization to find cost savings</p>
          </div>
          <button
            onClick={handleRunOptimization}
            disabled={isRunning}
            className="bg-blue-600 hover:bg-blue-700 disabled:bg-blue-800 disabled:cursor-not-allowed text-white font-medium py-2 px-6 rounded-lg transition flex items-center"
          >
            {isRunning ? (
              <>
                <svg
                  className="animate-spin -ml-1 mr-3 h-5 w-5 text-white"
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
                Running...
              </>
            ) : (
              'Run Optimization'
            )}
          </button>
        </div>

        {/* Empty State */}
        {!summary && !isRunning && (
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
            <p className="text-slate-400 text-lg mb-2">No optimization results yet</p>
            <p className="text-slate-500 text-sm">
              Click "Run Optimization" to analyze your products and find savings
            </p>
          </div>
        )}

        {/* Loading State */}
        {isRunning && (
          <div className="bg-slate-800 rounded-lg p-12 border border-slate-700 text-center">
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
            <p className="text-slate-400">Analyzing products and calculating savings...</p>
          </div>
        )}

        {/* Results */}
        {summary && !isRunning && (
          <div className="space-y-6">
            {/* Summary Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
                <h3 className="text-slate-400 text-sm font-medium mb-1">Products Analyzed</h3>
                <p className="text-3xl font-bold text-slate-100">
                  {summary.total_products_analyzed}
                </p>
              </div>

              <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
                <h3 className="text-slate-400 text-sm font-medium mb-1">Products with Savings</h3>
                <p className="text-3xl font-bold text-green-400">{summary.products_with_savings}</p>
              </div>

              <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
                <h3 className="text-slate-400 text-sm font-medium mb-1">Monthly Savings</h3>
                <p className="text-3xl font-bold text-blue-400">
                  {formatCurrency(summary.total_monthly_savings)}
                </p>
              </div>

              <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
                <h3 className="text-slate-400 text-sm font-medium mb-1">Annual Savings</h3>
                <p className="text-3xl font-bold text-purple-400">
                  {formatCurrency(summary.total_annual_savings)}
                </p>
              </div>
            </div>

            {/* Results Table */}
            {summary.results.length > 0 ? (
              <div className="bg-slate-800 rounded-lg border border-slate-700 overflow-hidden">
                <div className="p-6 border-b border-slate-700">
                  <h2 className="text-xl font-bold text-slate-100">Optimization Results</h2>
                </div>
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead className="bg-slate-700">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-slate-300 uppercase tracking-wider">
                          Product
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-slate-300 uppercase tracking-wider">
                          Current Box
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-slate-300 uppercase tracking-wider">
                          Recommended Box
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-slate-300 uppercase tracking-wider">
                          Current Cost
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-slate-300 uppercase tracking-wider">
                          New Cost
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-slate-300 uppercase tracking-wider">
                          Savings
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-slate-300 uppercase tracking-wider">
                          Savings %
                        </th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-700">
                      {summary.results.map((result, index) => (
                        <tr key={index} className="hover:bg-slate-700/50 transition">
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-100">
                            {result.product_name}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-300">
                            {result.current_box_name}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-300">
                            {result.recommended_box_name}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-300">
                            {formatCurrency(result.current_cost)}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-300">
                            {formatCurrency(result.recommended_cost)}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-green-400 font-medium">
                            {formatCurrency(result.savings)}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-green-400 font-medium">
                            {result.savings_percentage.toFixed(1)}%
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            ) : (
              <div className="bg-slate-800 rounded-lg p-12 border border-slate-700 text-center">
                <p className="text-slate-400 text-lg">No savings opportunities found</p>
                <p className="text-slate-500 text-sm mt-2">
                  Your current packaging is already optimal
                </p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default OptimizePage;
