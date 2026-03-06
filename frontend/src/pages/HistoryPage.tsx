import { useState, useEffect } from 'react';
import { apiClient } from '../services/api';
import toast from 'react-hot-toast';

interface OptimizationRun {
  id: number;
  timestamp: string;
  products_analyzed: number;
  total_monthly_savings: number;
  total_annual_savings: number;
}

interface OptimizationResult {
  product_name: string;
  current_box_name: string;
  recommended_box_name: string;
  savings: number;
  savings_percentage: number;
}

interface RunDetails {
  run_id: number;
  timestamp: string;
  total_products_analyzed: number;
  products_with_savings: number;
  total_monthly_savings: number;
  total_annual_savings: number;
  results: OptimizationResult[];
}

const HistoryPage = () => {
  const [history, setHistory] = useState<OptimizationRun[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedRun, setSelectedRun] = useState<RunDetails | null>(null);
  const [showModal, setShowModal] = useState(false);

  useEffect(() => {
    fetchHistory();
  }, []);

  const fetchHistory = async () => {
    setIsLoading(true);
    try {
      const data = await apiClient.getHistory();
      setHistory(data);
    } catch (error: any) {
      console.error('Failed to fetch history:', error);
      toast.error('Failed to load optimization history');
    } finally {
      setIsLoading(false);
    }
  };

  const handleViewDetails = async (runId: number) => {
    try {
      const details = await apiClient.getRunDetails(runId);
      setSelectedRun(details);
      setShowModal(true);
    } catch (error: any) {
      console.error('Failed to fetch run details:', error);
      toast.error('Failed to load run details');
    }
  };

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
    }).format(value);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

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
          <p className="text-slate-400">Loading history...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-900 p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-slate-100 mb-2">Optimization History</h1>
          <p className="text-slate-400">View past optimization runs and results</p>
        </div>

        {/* History Table */}
        {history.length === 0 ? (
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
                d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
            <p className="text-slate-400 text-lg mb-2">No optimization history yet</p>
            <p className="text-slate-500 text-sm">
              Run your first optimization to see results here
            </p>
          </div>
        ) : (
          <div className="bg-slate-800 rounded-lg border border-slate-700 overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-slate-700">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-slate-300 uppercase tracking-wider">
                      Date & Time
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-slate-300 uppercase tracking-wider">
                      Products Analyzed
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-slate-300 uppercase tracking-wider">
                      Monthly Savings
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-slate-300 uppercase tracking-wider">
                      Annual Savings
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-slate-300 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-700">
                  {history.map((run) => (
                    <tr key={run.id} className="hover:bg-slate-700/50 transition">
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-100">
                        {formatDate(run.timestamp)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-300">
                        {run.products_analyzed}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-green-400 font-medium">
                        {formatCurrency(run.total_monthly_savings)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-green-400 font-medium">
                        {formatCurrency(run.total_annual_savings)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                        <button
                          onClick={() => handleViewDetails(run.id)}
                          className="text-blue-400 hover:text-blue-300 transition"
                        >
                          View Details
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Details Modal */}
        {showModal && selectedRun && (
          <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4 z-50">
            <div className="bg-slate-800 rounded-lg max-w-6xl w-full max-h-[90vh] overflow-y-auto border border-slate-700">
              <div className="p-6">
                <div className="flex justify-between items-start mb-6">
                  <div>
                    <h2 className="text-2xl font-bold text-slate-100 mb-2">
                      Optimization Run Details
                    </h2>
                    <p className="text-slate-400">{formatDate(selectedRun.timestamp)}</p>
                  </div>
                  <button
                    onClick={() => setShowModal(false)}
                    className="text-slate-400 hover:text-slate-300 transition"
                  >
                    <svg
                      className="w-6 h-6"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M6 18L18 6M6 6l12 12"
                      />
                    </svg>
                  </button>
                </div>

                {/* Summary */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                  <div className="bg-slate-700 rounded-lg p-4">
                    <p className="text-slate-400 text-xs mb-1">Products Analyzed</p>
                    <p className="text-2xl font-bold text-slate-100">
                      {selectedRun.total_products_analyzed}
                    </p>
                  </div>
                  <div className="bg-slate-700 rounded-lg p-4">
                    <p className="text-slate-400 text-xs mb-1">With Savings</p>
                    <p className="text-2xl font-bold text-green-400">
                      {selectedRun.products_with_savings}
                    </p>
                  </div>
                  <div className="bg-slate-700 rounded-lg p-4">
                    <p className="text-slate-400 text-xs mb-1">Monthly Savings</p>
                    <p className="text-2xl font-bold text-blue-400">
                      {formatCurrency(selectedRun.total_monthly_savings)}
                    </p>
                  </div>
                  <div className="bg-slate-700 rounded-lg p-4">
                    <p className="text-slate-400 text-xs mb-1">Annual Savings</p>
                    <p className="text-2xl font-bold text-purple-400">
                      {formatCurrency(selectedRun.total_annual_savings)}
                    </p>
                  </div>
                </div>

                {/* Results Table */}
                {selectedRun.results.length > 0 ? (
                  <div className="overflow-x-auto">
                    <table className="w-full">
                      <thead className="bg-slate-700">
                        <tr>
                          <th className="px-4 py-3 text-left text-xs font-medium text-slate-300 uppercase">
                            Product
                          </th>
                          <th className="px-4 py-3 text-left text-xs font-medium text-slate-300 uppercase">
                            Current Box
                          </th>
                          <th className="px-4 py-3 text-left text-xs font-medium text-slate-300 uppercase">
                            Recommended
                          </th>
                          <th className="px-4 py-3 text-left text-xs font-medium text-slate-300 uppercase">
                            Savings
                          </th>
                          <th className="px-4 py-3 text-left text-xs font-medium text-slate-300 uppercase">
                            %
                          </th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-700">
                        {selectedRun.results.map((result, index) => (
                          <tr key={index}>
                            <td className="px-4 py-3 text-sm text-slate-100">
                              {result.product_name}
                            </td>
                            <td className="px-4 py-3 text-sm text-slate-300">
                              {result.current_box_name}
                            </td>
                            <td className="px-4 py-3 text-sm text-slate-300">
                              {result.recommended_box_name}
                            </td>
                            <td className="px-4 py-3 text-sm text-green-400 font-medium">
                              {formatCurrency(result.savings)}
                            </td>
                            <td className="px-4 py-3 text-sm text-green-400 font-medium">
                              {result.savings_percentage.toFixed(1)}%
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                ) : (
                  <div className="text-center py-8">
                    <p className="text-slate-400">No savings found in this run</p>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default HistoryPage;
