import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { apiClient } from '../services/api';

interface User {
  id: number;
  email: string;
  company_id: number;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, companyName: string) => Promise<void>;
  logout: () => void;
  isAuthenticated: boolean;
  isLoading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Check for existing token on mount
    const storedToken = apiClient.getToken();
    if (storedToken) {
      setToken(storedToken);
      // In a real app, you'd validate the token and fetch user data here
      // For now, we'll just mark as authenticated
    }
    setIsLoading(false);
  }, []);

  const login = async (email: string, password: string) => {
    try {
      const response = await apiClient.login({ email, password });
      const { access_token } = response;
      
      apiClient.setToken(access_token);
      setToken(access_token);
      
      // In a real app, decode JWT to get user info or fetch from /me endpoint
      // For now, we'll set a placeholder
      setUser({ id: 1, email, company_id: 1 });
    } catch (error) {
      console.error('Login failed:', error);
      throw error;
    }
  };

  const register = async (email: string, password: string, companyName: string) => {
    try {
      const response = await apiClient.register({ 
        email, 
        password, 
        company_name: companyName 
      });
      const { access_token } = response;
      
      apiClient.setToken(access_token);
      setToken(access_token);
      
      // Set placeholder user
      setUser({ id: 1, email, company_id: 1 });
    } catch (error) {
      console.error('Registration failed:', error);
      throw error;
    }
  };

  const logout = () => {
    apiClient.clearToken();
    setToken(null);
    setUser(null);
  };

  const value = {
    user,
    token,
    login,
    register,
    logout,
    isAuthenticated: !!token,
    isLoading,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
