import { useState, useEffect } from 'react';
import { apiClient } from '../services/api';
import toast from 'react-hot-toast';

interface Product {
  id: number;
  name: string;
  sku: string;
  category: string;
  length_cm: number;
  width_cm: number;
  height_cm: number;
  weight_kg: number;
  monthly_order_volume: number;
  current_box_id?: number;
}

const ProductsPage = () => {
  const [products, setProducts] = useState<Product[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [showCSVModal, setShowCSVModal] = useState(false);
  const [csvFile, setCSVFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [editingProduct, setEditingProduct] = useState<Product | null>(null);
  const [formData, setFormData] = useState({
    name: '',
    sku: '',
    category: 'general',
    length_cm: '',
    width_cm: '',
    height_cm: '',
    weight_kg: '',
    monthly_order_volume: '',
  });
  const [formErrors, setFormErrors] = useState<Record<string, string>>({});

  useEffect(() => {
    fetchProducts();
  }, []);

  const fetchProducts = async () => {
    setIsLoading(true);
    try {
      const data = await apiClient.getProducts();
      setProducts(data);
    } catch (error: any) {
      console.error('Failed to fetch products:', error);
      toast.error('Failed to load products');
    } finally {
      setIsLoading(false);
    }
  };

  const validateForm = (): boolean => {
    const errors: Record<string, string> = {};

    if (!formData.name.trim()) errors.name = 'Name is required';
    if (!formData.sku.trim()) errors.sku = 'SKU is required';
    if (!formData.length_cm || parseFloat(formData.length_cm) <= 0) {
      errors.length_cm = 'Length must be greater than 0';
    }
    if (!formData.width_cm || parseFloat(formData.width_cm) <= 0) {
      errors.width_cm = 'Width must be greater than 0';
    }
    if (!formData.height_cm || parseFloat(formData.height_cm) <= 0) {
      errors.height_cm = 'Height must be greater than 0';
    }
    if (!formData.weight_kg || parseFloat(formData.weight_kg) <= 0) {
      errors.weight_kg = 'Weight must be greater than 0';
    }
    if (!formData.monthly_order_volume || parseInt(formData.monthly_order_volume) < 0) {
      errors.monthly_order_volume = 'Monthly order volume must be 0 or greater';
    }

    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) return;

    try {
      const productData = {
        name: formData.name,
        sku: formData.sku,
        category: formData.category,
        length_cm: parseFloat(formData.length_cm),
        width_cm: parseFloat(formData.width_cm),
        height_cm: parseFloat(formData.height_cm),
        weight_kg: parseFloat(formData.weight_kg),
        monthly_order_volume: parseInt(formData.monthly_order_volume),
      };

      if (editingProduct) {
        await apiClient.updateProduct(editingProduct.id, productData);
        toast.success('Product updated successfully');
      } else {
        await apiClient.createProduct(productData);
        toast.success('Product created successfully');
      }

      setShowModal(false);
      resetForm();
      fetchProducts();
    } catch (error: any) {
      console.error('Failed to save product:', error);
      const errorMessage = error.response?.data?.detail || 'Failed to save product';
      toast.error(errorMessage);
    }
  };

  const handleEdit = (product: Product) => {
    setEditingProduct(product);
    setFormData({
      name: product.name,
      sku: product.sku,
      category: product.category,
      length_cm: product.length_cm.toString(),
      width_cm: product.width_cm.toString(),
      height_cm: product.height_cm.toString(),
      weight_kg: product.weight_kg.toString(),
      monthly_order_volume: product.monthly_order_volume.toString(),
    });
    setShowModal(true);
  };

  const handleDelete = async (id: number) => {
    if (!confirm('Are you sure you want to delete this product?')) return;

    try {
      await apiClient.deleteProduct(id);
      toast.success('Product deleted successfully');
      fetchProducts();
    } catch (error: any) {
      console.error('Failed to delete product:', error);
      toast.error('Failed to delete product');
    }
  };

  const resetForm = () => {
    setFormData({
      name: '',
      sku: '',
      category: 'general',
      length_cm: '',
      width_cm: '',
      height_cm: '',
      weight_kg: '',
      monthly_order_volume: '',
    });
    setFormErrors({});
    setEditingProduct(null);
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
      const result = await apiClient.uploadProductsCSV(csvFile);
      
      if (result.errors && result.errors.length > 0) {
        toast.success(`${result.created_count} products created with ${result.errors.length} errors`);
        console.log('Upload errors:', result.errors);
      } else {
        toast.success(`Successfully uploaded ${result.created_count} products`);
      }
      
      setShowCSVModal(false);
      setCSVFile(null);
      fetchProducts();
    } catch (error: any) {
      console.error('CSV upload failed:', error);
      const errorMessage = error.response?.data?.detail || 'Failed to upload CSV file';
      toast.error(errorMessage);
    } finally {
      setIsUploading(false);
    }
  };

  const downloadCSVTemplate = () => {
    const template = 'name,sku,category,length_cm,width_cm,height_cm,weight_kg,monthly_order_volume\n' +
                    'Gaming Laptop,LAPTOP-001,Electronics,40,30,5,3.5,100\n' +
                    'Smartphone,PHONE-001,Electronics,15,8,1,0.2,500';
    
    const blob = new Blob([template], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'products_template.csv';
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
          <p className="text-slate-400">Loading products...</p>
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
            <h1 className="text-3xl font-bold text-slate-100 mb-2">Products</h1>
            <p className="text-slate-400">Manage your product catalog</p>
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
              Add Product
            </button>
          </div>
        </div>

        {/* Products Table */}
        {products.length === 0 ? (
          <div className="bg-slate-800 rounded-lg p-12 border border-slate-700 text-center">
            <p className="text-slate-400 text-lg">No products yet</p>
            <p className="text-slate-500 text-sm mt-2">Add your first product to get started</p>
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
                      SKU
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-slate-300 uppercase tracking-wider">
                      Category
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-slate-300 uppercase tracking-wider">
                      Dimensions (cm)
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-slate-300 uppercase tracking-wider">
                      Weight (kg)
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-slate-300 uppercase tracking-wider">
                      Monthly Volume
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-slate-300 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-700">
                  {products.map((product) => (
                    <tr key={product.id} className="hover:bg-slate-700/50 transition">
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-100">
                        {product.name}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-300">
                        {product.sku}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-300">
                        {product.category}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-300">
                        {product.length_cm} × {product.width_cm} × {product.height_cm}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-300">
                        {product.weight_kg}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-300">
                        {product.monthly_order_volume}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                        <button
                          onClick={() => handleEdit(product)}
                          className="text-blue-400 hover:text-blue-300 mr-4 transition"
                        >
                          Edit
                        </button>
                        <button
                          onClick={() => handleDelete(product.id)}
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
                  {editingProduct ? 'Edit Product' : 'Add Product'}
                </h2>

                <form onSubmit={handleSubmit} className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    {/* Name */}
                    <div>
                      <label className="block text-sm font-medium text-slate-300 mb-2">
                        Product Name
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

                    {/* SKU */}
                    <div>
                      <label className="block text-sm font-medium text-slate-300 mb-2">
                        SKU
                      </label>
                      <input
                        type="text"
                        value={formData.sku}
                        onChange={(e) => setFormData({ ...formData, sku: e.target.value })}
                        className={`w-full px-4 py-2 bg-slate-700 border ${
                          formErrors.sku ? 'border-red-500' : 'border-slate-600'
                        } rounded-lg text-slate-100 focus:outline-none focus:ring-2 focus:ring-blue-500`}
                      />
                      {formErrors.sku && (
                        <p className="mt-1 text-sm text-red-400">{formErrors.sku}</p>
                      )}
                    </div>
                  </div>

                  {/* Category */}
                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-2">
                      Category
                    </label>
                    <select
                      value={formData.category}
                      onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                      className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg text-slate-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="general">General</option>
                      <option value="electronics">Electronics</option>
                      <option value="fragile">Fragile</option>
                      <option value="clothing">Clothing</option>
                      <option value="books">Books</option>
                      <option value="toys">Toys</option>
                    </select>
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

                  {/* Weight and Monthly Volume */}
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-slate-300 mb-2">
                        Weight (kg)
                      </label>
                      <input
                        type="number"
                        step="0.01"
                        value={formData.weight_kg}
                        onChange={(e) => setFormData({ ...formData, weight_kg: e.target.value })}
                        className={`w-full px-4 py-2 bg-slate-700 border ${
                          formErrors.weight_kg ? 'border-red-500' : 'border-slate-600'
                        } rounded-lg text-slate-100 focus:outline-none focus:ring-2 focus:ring-blue-500`}
                      />
                      {formErrors.weight_kg && (
                        <p className="mt-1 text-sm text-red-400">{formErrors.weight_kg}</p>
                      )}
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-slate-300 mb-2">
                        Monthly Order Volume
                      </label>
                      <input
                        type="number"
                        step="1"
                        value={formData.monthly_order_volume}
                        onChange={(e) =>
                          setFormData({ ...formData, monthly_order_volume: e.target.value })
                        }
                        className={`w-full px-4 py-2 bg-slate-700 border ${
                          formErrors.monthly_order_volume ? 'border-red-500' : 'border-slate-600'
                        } rounded-lg text-slate-100 focus:outline-none focus:ring-2 focus:ring-blue-500`}
                      />
                      {formErrors.monthly_order_volume && (
                        <p className="mt-1 text-sm text-red-400">{formErrors.monthly_order_volume}</p>
                      )}
                    </div>
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
                      {editingProduct ? 'Update' : 'Create'}
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
                  Bulk Upload Products
                </h2>

                <div className="space-y-6">
                  {/* Instructions */}
                  <div className="bg-slate-700/50 rounded-lg p-4 border border-slate-600">
                    <h3 className="text-sm font-semibold text-slate-200 mb-2">CSV Format Requirements:</h3>
                    <ul className="text-sm text-slate-300 space-y-1 list-disc list-inside">
                      <li>File must be in CSV format (.csv)</li>
                      <li>Required columns: name, sku, category, length_cm, width_cm, height_cm, weight_kg, monthly_order_volume</li>
                      <li>All dimensions in centimeters (cm)</li>
                      <li>Weight in kilograms (kg)</li>
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

export default ProductsPage;
