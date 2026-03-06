import { useState, useEffect } from 'react';
import { apiClient } from '../services/api';
import toast from 'react-hot-toast';

interface Box {
  id: number;
  name: string;
  length_cm: number;
  width_cm: number;
  height_cm: number;
  cost_per_unit: number;
  usage_count: number;
}

const BoxesPage = () => {
  const [boxes, setBoxes] = useState<Box[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [showCSVModal, setShowCSVModal] = useState(false);
  const [csvFile, setCSVFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [editingBox, setEditingBox] = useState<Box | null>(null);
  const [formData, setFormData] = useState({
    name: '',
    length_cm: '',
    width_cm: '',
    height_cm: '',
    cost_per_unit: '',
  });
  const [formErrors, setFormErrors] = useState<Record<string, string>>({});

  useEffect(() => {
    fetchBoxes();
  }, []);

  const fetchBoxes = async () => {
    setIsLoading(true);
    try {
      const data = await apiClient.getBoxes();
      setBoxes(data);
    } catch (error: any) {
      console.error('Failed to fetch boxes:', error);
      toast.error('Failed to load boxes');
    } finally {
      setIsLoading(false);
    }
  };

  const validateForm = (): boolean => {
    const errors: Record<string, string> = {};

    if (!formData.name.trim()) errors.name = 'Name is required';
    if (!formData.length_cm || parseFloat(formData.length_cm) <= 0) {
      errors.length_cm = 'Length must be greater than 0';
    }
    if (!formData.width_cm || parseFloat(formData.width_cm) <= 0) {
      errors.width_cm = 'Width must be greater than 0';
    }
    if (!formData.height_cm || parseFloat(formData.height_cm) <= 0) {
      errors.height_cm = 'Height must be greater than 0';
    }
    if (!formData.cost_per_unit || parseFloat(formData.cost_per_unit) <= 0) {
      errors.cost_per_unit = 'Cost per unit must be greater than 0';
    }

    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) return;

    try {
      const boxData = {
        name: formData.name,
        length_cm: parseFloat(formData.length_cm),
        width_cm: parseFloat(formData.width_cm),
        height_cm: parseFloat(formData.height_cm),
        cost_per_unit: parseFloat(formData.cost_per_unit),
      };

      if (editingBox) {
        await apiClient.updateBox(editingBox.id, boxData);
        toast.success('Box updated successfully');
      } else {
        await apiClient.createBox(boxData);
        toast.success('Box created successfully');
      }

      setShowModal(false);
      resetForm();
      fetchBoxes();
    } catch (error: any) {
      console.error('Failed to save box:', error);
      const errorMessage = error.response?.data?.detail || 'Failed to save box';
      toast.error(errorMessage);
    }
  };

  const handleEdit = (box: Box) => {
    setEditingBox(box);
    setFormData({
      name: box.name,
      length_cm: box.length_cm.toString(),
      width_cm: box.width_cm.toString(),
      height_cm: box.height_cm.toString(),
      cost_per_unit: box.cost_per_unit.toString(),
    });
    setShowModal(true);
  };

  const handleDelete = async (id: number) => {
    if (!confirm('Are you sure you want to delete this box?')) return;

    try {
      await apiClient.deleteBox(id);
      toast.success('Box deleted successfully');
      fetchBoxes();
    } catch (error: any) {
      console.error('Failed to delete box:', error);
      toast.error('Failed to delete box');
    }
  };

  const resetForm = () => {
    setFormData({
      name: '',
      length_cm: '',
      width_cm: '',
      height_cm: '',
      cost_per_unit: '',
    });
    setFormErrors({});
    setEditingBox(null);
  };

  const handleCloseModal = () => {
    setShowModal(false);
    resetForm();
  };

  const handleCSVUpload = async () => {
    if (!csvFile) {
      toast.error('Please select a CSV file');
      return;
    }

    setIsUploading(true);
    try {
      const result = await apiClient.uploadBoxesCSV(csvFile);
      
      if (result.errors && result.errors.length > 0) {
        toast.success(`${result.created_count} boxes created with ${result.errors.length} errors`);
        console.log('Upload errors:', result.errors);
      } else {
        toast.success(`Successfully uploaded ${result.created_count} boxes`);
      }
      
      setShowCSVModal(false);
      setCSVFile(null);
      fetchBoxes();
    } catch (error: any) {
      console.error('CSV upload failed:', error);
      const errorMessage = error.response?.data?.detail || 'Failed to upload CSV file';
      toast.error(errorMessage);
    } finally {
      setIsUploading(false);
    }
  };

  const downloadCSVTemplate = () => {
    const template = 'name,length_cm,width_cm,height_cm,cost_per_unit\n' +
                    'Small Box,20,15,10,1.50\n' +
                    'Medium Box,35,25,15,2.50\n' +
                    'Large Box,50,40,20,3.50';
    
    const blob = new Blob([template], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'boxes_template.csv';
    a.click();
    window.URL.revokeObjectURL(url);
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
          <p className="text-slate-400">Loading boxes...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-900 p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold text-slate-100 mb-2">Boxes</h1>
            <p className="text-slate-400">Manage your box inventory</p>
          </div>
          <div className="flex gap-3">
            <button
              onClick={() => setShowCSVModal(true)}
              className="bg-green-600 hover:bg-green-700 text-white font-medium py-2 px-4 rounded-lg transition flex items-center gap-2"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
              </svg>
              Bulk Upload CSV
            </button>
            <button
              onClick={() => setShowModal(true)}
              className="bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-lg transition"
            >
              Add Box
            </button>
          </div>
        </div>

        {/* Boxes Table */}
        {boxes.length === 0 ? (
          <div className="bg-slate-800 rounded-lg p-12 border border-slate-700 text-center">
            <p className="text-slate-400 text-lg">No boxes yet</p>
            <p className="text-slate-500 text-sm mt-2">Add your first box to get started</p>
          </div>
        ) : (
          <div className="bg-slate-800 rounded-lg border border-slate-700 overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-slate-700">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-slate-300 uppercase tracking-wider">
                      Name
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-slate-300 uppercase tracking-wider">
                      Dimensions (cm)
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-slate-300 uppercase tracking-wider">
                      Cost Per Unit
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-slate-300 uppercase tracking-wider">
                      Usage Count
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-slate-300 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-700">
                  {boxes.map((box) => (
                    <tr key={box.id} className="hover:bg-slate-700/50 transition">
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-100">
                        {box.name}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-300">
                        {box.length_cm} × {box.width_cm} × {box.height_cm}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-300">
                        ${box.cost_per_unit.toFixed(2)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-300">
                        {box.usage_count}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                        <button
                          onClick={() => handleEdit(box)}
                          className="text-blue-400 hover:text-blue-300 mr-4 transition"
                        >
                          Edit
                        </button>
                        <button
                          onClick={() => handleDelete(box.id)}
                          className="text-red-400 hover:text-red-300 transition"
                        >
                          Delete
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Modal */}
        {showModal && (
          <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4 z-50">
            <div className="bg-slate-800 rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto border border-slate-700">
              <div className="p-6">
                <h2 className="text-2xl font-bold text-slate-100 mb-6">
                  {editingBox ? 'Edit Box' : 'Add Box'}
                </h2>

                <form onSubmit={handleSubmit} className="space-y-4">
                  {/* Name */}
                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-2">
                      Box Name
                    </label>
                    <input
                      type="text"
                      value={formData.name}
                      onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                      className={`w-full px-4 py-2 bg-slate-700 border ${
                        formErrors.name ? 'border-red-500' : 'border-slate-600'
                      } rounded-lg text-slate-100 focus:outline-none focus:ring-2 focus:ring-blue-500`}
                    />
                    {formErrors.name && (
                      <p className="mt-1 text-sm text-red-400">{formErrors.name}</p>
                    )}
                  </div>

                  {/* Dimensions */}
                  <div className="grid grid-cols-3 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-slate-300 mb-2">
                        Length (cm)
                      </label>
                      <input
                        type="number"
                        step="0.01"
                        value={formData.length_cm}
                        onChange={(e) => setFormData({ ...formData, length_cm: e.target.value })}
                        className={`w-full px-4 py-2 bg-slate-700 border ${
                          formErrors.length_cm ? 'border-red-500' : 'border-slate-600'
                        } rounded-lg text-slate-100 focus:outline-none focus:ring-2 focus:ring-blue-500`}
                      />
                      {formErrors.length_cm && (
                        <p className="mt-1 text-sm text-red-400">{formErrors.length_cm}</p>
                      )}
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-slate-300 mb-2">
                        Width (cm)
                      </label>
                      <input
                        type="number"
                        step="0.01"
                        value={formData.width_cm}
                        onChange={(e) => setFormData({ ...formData, width_cm: e.target.value })}
                        className={`w-full px-4 py-2 bg-slate-700 border ${
                          formErrors.width_cm ? 'border-red-500' : 'border-slate-600'
                        } rounded-lg text-slate-100 focus:outline-none focus:ring-2 focus:ring-blue-500`}
                      />
                      {formErrors.width_cm && (
                        <p className="mt-1 text-sm text-red-400">{formErrors.width_cm}</p>
                      )}
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-slate-300 mb-2">
                        Height (cm)
                      </label>
                      <input
                        type="number"
                        step="0.01"
                        value={formData.height_cm}
                        onChange={(e) => setFormData({ ...formData, height_cm: e.target.value })}
                        className={`w-full px-4 py-2 bg-slate-700 border ${
                          formErrors.height_cm ? 'border-red-500' : 'border-slate-600'
                        } rounded-lg text-slate-100 focus:outline-none focus:ring-2 focus:ring-blue-500`}
                      />
                      {formErrors.height_cm && (
                        <p className="mt-1 text-sm text-red-400">{formErrors.height_cm}</p>
                      )}
                    </div>
                  </div>

                  {/* Cost Per Unit */}
                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-2">
                      Cost Per Unit ($)
                    </label>
                    <input
                      type="number"
                      step="0.01"
                      value={formData.cost_per_unit}
                      onChange={(e) => setFormData({ ...formData, cost_per_unit: e.target.value })}
                      className={`w-full px-4 py-2 bg-slate-700 border ${
                        formErrors.cost_per_unit ? 'border-red-500' : 'border-slate-600'
                      } rounded-lg text-slate-100 focus:outline-none focus:ring-2 focus:ring-blue-500`}
                    />
                    {formErrors.cost_per_unit && (
                      <p className="mt-1 text-sm text-red-400">{formErrors.cost_per_unit}</p>
                    )}
                  </div>

                  {/* Buttons */}
                  <div className="flex justify-end gap-4 mt-6">
                    <button
                      type="button"
                      onClick={handleCloseModal}
                      className="px-4 py-2 bg-slate-700 hover:bg-slate-600 text-slate-300 rounded-lg transition"
                    >
                      Cancel
                    </button>
                    <button
                      type="submit"
                      className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition"
                    >
                      {editingBox ? 'Update' : 'Create'}
                    </button>
                  </div>
                </form>
              </div>
            </div>
          </div>
        )}

        {/* CSV Upload Modal */}
        {showCSVModal && (
          <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4 z-50">
            <div className="bg-slate-800 rounded-lg max-w-2xl w-full border border-slate-700">
              <div className="p-6">
                <h2 className="text-2xl font-bold text-slate-100 mb-6">
                  Bulk Upload Boxes
                </h2>

                <div className="space-y-6">
                  {/* Instructions */}
                  <div className="bg-slate-700/50 rounded-lg p-4 border border-slate-600">
                    <h3 className="text-sm font-semibold text-slate-200 mb-2">CSV Format Requirements:</h3>
                    <ul className="text-sm text-slate-300 space-y-1 list-disc list-inside">
                      <li>File must be in CSV format (.csv)</li>
                      <li>Required columns: name, length_cm, width_cm, height_cm, cost_per_unit</li>
                      <li>All dimensions in centimeters (cm)</li>
                      <li>Cost in dollars ($)</li>
                      <li>No header row required (will be auto-detected)</li>
                    </ul>
                  </div>

                  {/* Download Template */}
                  <button
                    onClick={downloadCSVTemplate}
                    className="w-full bg-slate-700 hover:bg-slate-600 text-slate-200 font-medium py-3 px-4 rounded-lg transition flex items-center justify-center gap-2"
                  >
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                    Download CSV Template
                  </button>

                  {/* File Upload */}
                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-2">
                      Select CSV File
                    </label>
                    <input
                      type="file"
                      accept=".csv"
                      onChange={(e) => setCSVFile(e.target.files?.[0] || null)}
                      className="w-full px-4 py-3 bg-slate-700 border border-slate-600 rounded-lg text-slate-100 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-blue-600 file:text-white hover:file:bg-blue-700 file:cursor-pointer"
                    />
                    {csvFile && (
                      <p className="mt-2 text-sm text-green-400">
                        Selected: {csvFile.name}
                      </p>
                    )}
                  </div>

                  {/* Buttons */}
                  <div className="flex justify-end gap-4 mt-6">
                    <button
                      type="button"
                      onClick={() => {
                        setShowCSVModal(false);
                        setCSVFile(null);
                      }}
                      disabled={isUploading}
                      className="px-4 py-2 bg-slate-700 hover:bg-slate-600 text-slate-300 rounded-lg transition disabled:opacity-50"
                    >
                      Cancel
                    </button>
                    <button
                      onClick={handleCSVUpload}
                      disabled={!csvFile || isUploading}
                      className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg transition disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                    >
                      {isUploading ? (
                        <>
                          <svg className="animate-spin h-5 w-5" fill="none" viewBox="0 0 24 24">
                            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                          </svg>
                          Uploading...
                        </>
                      ) : (
                        'Upload'
                      )}
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default BoxesPage;
