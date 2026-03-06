import axios, { AxiosInstance } from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Types
interface LoginData {
  email: string;
  password: string;
}

interface RegisterData {
  email: string;
  password: string;
  company_name: string;
}

interface TokenResponse {
  access_token: string;
  token_type: string;
}

class ApiClient {
  private client: AxiosInstance;
  private token: string | null = null;

  constructor() {
    this.client = axios.create({
      baseURL: API_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Load token from localStorage
    this.token = localStorage.getItem('token');

    // Add request interceptor to include token
    this.client.interceptors.request.use((config) => {
      if (this.token) {
        config.headers.Authorization = `Bearer ${this.token}`;
      }
      return config;
    });

    // Add response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          this.clearToken();
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
    );
  }

  // Token management
  setToken(token: string) {
    this.token = token;
    localStorage.setItem('token', token);
  }

  clearToken() {
    this.token = null;
    localStorage.removeItem('token');
  }

  getToken() {
    return this.token;
  }

  // Auth endpoints
  async login(data: LoginData): Promise<TokenResponse> {
    const response = await this.client.post<TokenResponse>('/auth/login', data);
    return response.data;
  }

  async register(data: RegisterData): Promise<TokenResponse> {
    const response = await this.client.post<TokenResponse>('/auth/register', data);
    return response.data;
  }

  // Product endpoints
  async getProducts(skip = 0, limit = 100) {
    const response = await this.client.get('/products', { params: { skip, limit } });
    return response.data;
  }

  async getProduct(id: number) {
    const response = await this.client.get(`/products/${id}`);
    return response.data;
  }

  async createProduct(data: any) {
    const response = await this.client.post('/products', data);
    return response.data;
  }

  async updateProduct(id: number, data: any) {
    const response = await this.client.put(`/products/${id}`, data);
    return response.data;
  }

  async deleteProduct(id: number) {
    await this.client.delete(`/products/${id}`);
  }

  // Product CSV upload
  async uploadProductsCSV(file: File) {
    const formData = new FormData();
    formData.append('file', file);
    const response = await this.client.post('/products/bulk-upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  }

  // Box endpoints
  async getBoxes() {
    const response = await this.client.get('/boxes');
    return response.data;
  }

  async getBox(id: number) {
    const response = await this.client.get(`/boxes/${id}`);
    return response.data;
  }

  async createBox(data: any) {
    const response = await this.client.post('/boxes', data);
    return response.data;
  }

  async updateBox(id: number, data: any) {
    const response = await this.client.put(`/boxes/${id}`, data);
    return response.data;
  }

  async deleteBox(id: number) {
    await this.client.delete(`/boxes/${id}`);
  }

  // Box CSV upload
  async uploadBoxesCSV(file: File) {
    const formData = new FormData();
    formData.append('file', file);
    const response = await this.client.post('/boxes/bulk-upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  }

  // Optimization endpoints
  async runOptimization(productIds?: number[]) {
    const response = await this.client.post('/optimize', { product_ids: productIds });
    return response.data;
  }

  // Analytics endpoints
  async getDashboard() {
    const response = await this.client.get('/analytics/dashboard');
    return response.data;
  }

  async getLeakage() {
    const response = await this.client.get('/analytics/leakage');
    return response.data;
  }

  async getInefficientProducts(limit = 10) {
    const response = await this.client.get('/analytics/inefficient', { params: { limit } });
    return response.data;
  }

  async getTrends(limit = 12) {
    const response = await this.client.get('/analytics/trends', { params: { limit } });
    return response.data;
  }

  // History endpoints
  async getHistory(skip = 0, limit = 50) {
    const response = await this.client.get('/history', { params: { skip, limit } });
    return response.data;
  }

  async getRunDetails(runId: number) {
    const response = await this.client.get(`/history/${runId}`);
    return response.data;
  }

  // Subscription endpoints
  async getSubscriptionPlans() {
    const response = await this.client.get('/subscriptions/plans');
    return response.data;
  }

  async getCurrentSubscription() {
    const response = await this.client.get('/subscriptions/current');
    return response.data;
  }

  async getUsageSummary() {
    const response = await this.client.get('/subscriptions/usage');
    return response.data;
  }

  async upgradeSubscription(planName: string) {
    const response = await this.client.post('/subscriptions/upgrade', { plan_name: planName });
    return response.data;
  }

  // Admin endpoints
  async getCompanyUsers() {
    const response = await this.client.get('/admin/users');
    return response.data;
  }

  async assignUserRole(email: string, role: string) {
    const response = await this.client.post('/admin/users/assign-role', { user_email: email, role });
    return response.data;
  }

  // Export endpoints
  async exportProducts() {
    const response = await this.client.get('/export/products', { responseType: 'blob' });
    return response;
  }

  async exportBoxes() {
    const response = await this.client.get('/export/boxes', { responseType: 'blob' });
    return response;
  }

  async exportOptimizations() {
    const response = await this.client.get('/export/optimizations', { responseType: 'blob' });
    return response;
  }

  // Orders endpoints
  async createOrder(orderData: any) {
    const response = await this.client.post('/orders', orderData);
    return response.data;
  }

  async getOrder(orderId: number) {
    const response = await this.client.get(`/orders/${orderId}`);
    return response.data;
  }

  async listOrders(skip = 0, limit = 100, status?: string) {
    const params: any = { skip, limit };
    if (status) params.status = status;
    const response = await this.client.get('/orders', { params });
    return response.data;
  }

  async optimizeOrder(orderId: number, courierRate = 2.5) {
    const response = await this.client.post(`/orders/${orderId}/optimize`, null, {
      params: { courier_rate: courierRate }
    });
    return response.data;
  }

  // Tasks endpoints
  async getTaskStatus(taskId: string) {
    const response = await this.client.get(`/tasks/${taskId}`);
    return response.data;
  }

  async getTaskResult(taskId: string) {
    const response = await this.client.get(`/tasks/${taskId}/result`);
    return response.data;
  }

  // Bulk Upload endpoints
  async uploadBulkOrders(file: File) {
    const formData = new FormData();
    formData.append('file', file);
    const response = await this.client.post('/api/v1/bulk-upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  }

  async getBulkUploadStatus(uploadId: number) {
    const response = await this.client.get(`/api/v1/bulk-upload/${uploadId}`);
    return response.data;
  }

  async getFailedOrders(uploadId: number) {
    const response = await this.client.get(`/api/v1/bulk-upload/${uploadId}/failed`);
    return response.data;
  }

  // Warehouse API endpoints
  async createApiKey(name: string) {
    const response = await this.client.post('/api/v1/warehouse/api-keys', { name });
    return response.data;
  }

  async listApiKeys() {
    const response = await this.client.get('/api/v1/warehouse/api-keys');
    return response.data;
  }

  async deleteApiKey(keyId: number) {
    await this.client.delete(`/api/v1/warehouse/api-keys/${keyId}`);
  }

  async registerWebhook(webhookData: any) {
    const response = await this.client.post('/api/v1/warehouse/webhooks', webhookData);
    return response.data;
  }

  async listWebhooks() {
    const response = await this.client.get('/api/v1/warehouse/webhooks');
    return response.data;
  }

  async deleteWebhook(webhookId: number) {
    await this.client.delete(`/api/v1/warehouse/webhooks/${webhookId}`);
  }
}

export const apiClient = new ApiClient();
export default apiClient;
