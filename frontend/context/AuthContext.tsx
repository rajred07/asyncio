'use client';

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { UserResponse } from '@/lib/api/models/UserResponse';
import { UsersService } from '@/lib/api/services/UsersService';
import { OpenAPI } from '@/lib/api/core/OpenAPI';

interface AuthContextType {
  user: UserResponse | null;
  loading: boolean;
  login: (token: string) => Promise<void>;
  logout: () => void;
  isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [user, setUser] = useState<UserResponse | null>(null);
  const [loading, setLoading] = useState(true);

  // Configure API Base URL
  OpenAPI.BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

  useEffect(() => {
    const initAuth = async () => {
      const token = localStorage.getItem('accessToken');
      if (token) {
        OpenAPI.TOKEN = token;
        try {
          const userProfile = await UsersService.getCurrentUserProfileApiUsersMeGet();
          setUser(userProfile);
        } catch (error) {
          console.error('Failed to fetch user profile:', error);
          logout();
        }
      }
      setLoading(false);
    };

    initAuth();
  }, []);

  const login = async (token: string) => {
    localStorage.setItem('accessToken', token);
    OpenAPI.TOKEN = token;
    try {
      const userProfile = await UsersService.getCurrentUserProfileApiUsersMeGet();
      setUser(userProfile);
    } catch (error) {
      console.error('Login failed to fetch profile:', error);
      throw error;
    }
  };

  const logout = () => {
    localStorage.removeItem('accessToken');
    OpenAPI.TOKEN = undefined;
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, logout, isAuthenticated: !!user }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
