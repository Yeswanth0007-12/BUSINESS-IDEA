import { Routes, Route, Navigate } from 'react-router-dom';
import ProtectedRoute from './components/ProtectedRoute';
import Sidebar from './layout/Sidebar';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import DashboardPage from './pages/DashboardPage';
import ProductsPage from './pages/ProductsPage';
import BoxesPage from './pages/BoxesPage';
import OptimizePage from './pages/OptimizePage';
import HistoryPage from './pages/HistoryPage';
import LeakagePage from './pages/LeakagePage';
import OrdersPage from './pages/OrdersPage';
import BulkUploadPage from './pages/BulkUploadPage';
import TasksPage from './pages/TasksPage';
import WarehousePage from './pages/WarehousePage';
import SubscriptionPage from './pages/SubscriptionPage';
import AdminPage from './pages/AdminPage';
import './App.css';

// Layout component for authenticated routes
const AuthenticatedLayout = ({ children }: { children: React.ReactNode }) => {
  return (
    <div className="flex min-h-screen bg-slate-900">
      <Sidebar />
      <div className="flex-1">
        {children}
      </div>
    </div>
  );
};

function App() {
  return (
    <div className="min-h-screen bg-slate-900">
      <Routes>
        {/* Public routes - NO SIDEBAR */}
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />

        {/* Protected routes - WITH SIDEBAR */}
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <AuthenticatedLayout>
                <DashboardPage />
              </AuthenticatedLayout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/products"
          element={
            <ProtectedRoute>
              <AuthenticatedLayout>
                <ProductsPage />
              </AuthenticatedLayout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/boxes"
          element={
            <ProtectedRoute>
              <AuthenticatedLayout>
                <BoxesPage />
              </AuthenticatedLayout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/optimize"
          element={
            <ProtectedRoute>
              <AuthenticatedLayout>
                <OptimizePage />
              </AuthenticatedLayout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/history"
          element={
            <ProtectedRoute>
              <AuthenticatedLayout>
                <HistoryPage />
              </AuthenticatedLayout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/leakage"
          element={
            <ProtectedRoute>
              <AuthenticatedLayout>
                <LeakagePage />
              </AuthenticatedLayout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/orders"
          element={
            <ProtectedRoute>
              <AuthenticatedLayout>
                <OrdersPage />
              </AuthenticatedLayout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/bulk-upload"
          element={
            <ProtectedRoute>
              <AuthenticatedLayout>
                <BulkUploadPage />
              </AuthenticatedLayout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/tasks"
          element={
            <ProtectedRoute>
              <AuthenticatedLayout>
                <TasksPage />
              </AuthenticatedLayout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/warehouse"
          element={
            <ProtectedRoute>
              <AuthenticatedLayout>
                <WarehousePage />
              </AuthenticatedLayout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/subscription"
          element={
            <ProtectedRoute>
              <AuthenticatedLayout>
                <SubscriptionPage />
              </AuthenticatedLayout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/admin"
          element={
            <ProtectedRoute>
              <AuthenticatedLayout>
                <AdminPage />
              </AuthenticatedLayout>
            </ProtectedRoute>
          }
        />

        {/* Default redirect */}
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </div>
  );
}

export default App;
