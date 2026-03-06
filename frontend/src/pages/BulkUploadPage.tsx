import { useState } from 'react';
import api from '../services/api';

interface UploadResult {
  upload_id: number;
  total_orders: number;
  successful: number;
  failed: number;
  task_ids: string[];
  status: string;
  message: string;
  failed_details?: Array<{
    order_number: string;
    error: string;
    missing_skus: string[];
  }>;
}

const BulkUploadPage = () => {
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [result, setResult] = useState<UploadResult | null>(null);
  const [error, setError] = useState('');

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setError('');
      setResult(null);
    }
  };

  const handleUpload = async () => {
    if (!file) {
      setError('Please select a CSV file');
      return;
    }

    if (!file.name.endsWith('.csv')) {
      setError('File must be a CSV file');
      return;
    }

    try {
      setUploading(true);
      setError('');
      const data = await api.uploadBulkOrders(file);
      setResult(data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to upload file');
      setResult(null);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-slate-100">Bulk Order Upload</h1>
        <p className="mt-2 text-slate-400">Upload CSV files with multiple orders for batch processing</p>
      </div>

      {/* CSV Format Guide */}
      <div className="bg-slate-800 rounded-lg border border-slate-700 p-6">
        <h2 className="text-lg font-semibold text-slate-100 mb-3">CSV Format Requirements</h2>
        <div className="space-y-2 text-sm text-slate-300">
          <p><span className="font-medium text-blue-400">Required columns:</span> order_number, customer_name, product_sku, quantity</p>
          <p><span className="font-medium text-blue-400">Maximum file size:</span> 10 MB</p>
          <p><span className="font-medium text-blue-400">Maximum rows:</span> 10,000</p>
        </div>
        <div className="mt-4 p-3 bg-slate-700/50 rounded font-mono text-xs text-slate-300">
          order_number,customer_name,product_sku,quantity<br />
          ORD-001,John Doe,PROD-123,2<br />
          ORD-001,John Doe,PROD-456,1<br />
          ORD-002,Jane Smith,PROD-789,3
        </div>
      </div>

      {/* File Upload */}
      <div className="bg-slate-800 rounded-lg border border-slate-700 p-6">
        <label className="block text-sm font-medium text-slate-300 mb-3">Select CSV File</label>
        <div className="flex flex-col gap-4">
          <input
            type="file"
            accept=".csv"
            onChange={handleFileChange}
            className="block w-full text-sm text-slate-300
              file:mr-4 file:py-2 file:px-4
              file:rounded-lg file:border-0
              file:text-sm file:font-medium
              file:bg-blue-600 file:text-white
              hover:file:bg-blue-700
              file:cursor-pointer cursor-pointer"
          />
          {file && (
            <p className="text-sm text-slate-400">
              Selected: <span className="text-slate-200">{file.name}</span> ({(file.size / 1024).toFixed(2)} KB)
            </p>
          )}
          <button
            onClick={handleUpload}
            disabled={!file || uploading}
            className="w-full md:w-auto px-6 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-slate-600 text-white font-medium rounded-lg transition-colors"
          >
            {uploading ? 'Uploading...' : 'Upload and Process'}
          </button>
        </div>
        {error && (
          <div className="mt-4 p-3 bg-red-900/20 border border-red-700 rounded-lg">
            <p className="text-sm text-red-400">{error}</p>
          </div>
        )}
      </div>

      {/* Upload Result */}
      {result && (
        <div className="bg-slate-800 rounded-lg border border-slate-700 p-6 space-y-4">
          <h2 className="text-xl font-semibold text-slate-100">Upload Result</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="bg-slate-700/50 rounded-lg p-4">
              <div className="text-sm text-slate-400">Upload ID</div>
              <div className="text-2xl font-bold text-blue-400">{result.upload_id}</div>
            </div>
            <div className="bg-slate-700/50 rounded-lg p-4">
              <div className="text-sm text-slate-400">Total Orders</div>
              <div className="text-2xl font-bold text-slate-100">{result.total_orders}</div>
            </div>
            <div className="bg-slate-700/50 rounded-lg p-4">
              <div className="text-sm text-slate-400">Successful</div>
              <div className="text-2xl font-bold text-green-400">{result.successful}</div>
            </div>
            <div className="bg-slate-700/50 rounded-lg p-4">
              <div className="text-sm text-slate-400">Failed</div>
              <div className="text-2xl font-bold text-red-400">{result.failed}</div>
            </div>
          </div>

          <div className="p-4 bg-blue-900/20 border border-blue-700 rounded-lg">
            <p className="text-sm font-medium text-blue-400">Status</p>
            <p className="text-sm text-blue-300 mt-1">{result.message}</p>
          </div>

          {result.task_ids.length > 0 && (
            <div>
              <p className="text-sm font-medium text-slate-300 mb-2">Task IDs (for tracking):</p>
              <div className="max-h-40 overflow-y-auto space-y-1">
                {result.task_ids.map((taskId, idx) => (
                  <div key={idx} className="p-2 bg-slate-700/50 rounded text-xs font-mono text-slate-300">
                    {taskId}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Detailed Error Messages */}
          {result.failed_details && result.failed_details.length > 0 && (
            <div className="mt-4">
              <h3 className="text-lg font-semibold text-red-400 mb-3">Failed Orders Details</h3>
              <div className="max-h-96 overflow-y-auto space-y-3">
                {result.failed_details.map((failure, idx) => (
                  <div key={idx} className="p-4 bg-red-900/20 border border-red-700 rounded-lg">
                    <div className="flex items-start justify-between mb-2">
                      <span className="font-medium text-red-300">Order: {failure.order_number}</span>
                    </div>
                    <p className="text-sm text-red-400 mb-2">{failure.error}</p>
                    {failure.missing_skus && failure.missing_skus.length > 0 && (
                      <div className="mt-2">
                        <p className="text-xs font-medium text-red-300 mb-1">Missing SKUs:</p>
                        <div className="flex flex-wrap gap-1">
                          {failure.missing_skus.map((sku, skuIdx) => (
                            <span key={skuIdx} className="px-2 py-1 bg-red-800/30 rounded text-xs font-mono text-red-200">
                              {sku}
                            </span>
                          ))}
                        </div>
                        <p className="text-xs text-red-300 mt-2">
                          💡 Add these products to your Products catalog first, then try uploading again.
                        </p>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default BulkUploadPage;
