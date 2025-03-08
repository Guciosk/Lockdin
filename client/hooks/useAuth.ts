/**
 * Authentication Hook
 * 
 * Custom hook for handling authentication-related functionality.
 * Provides login, logout, and user state management.
 */

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import apiService, { User } from '@/lib/api';

// For development/testing purposes
import { dummyUser, dummyCredentials } from '@/lib/dummy-data';

interface UseAuthReturn {
  user: User | null;
  isLoading: boolean;
  error: string | null;
  login: (username: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
}

export function useAuth(): UseAuthReturn {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  // Check if user is already logged in on mount
  useEffect(() => {
    const checkAuth = async () => {
      try {
        setIsLoading(true);
        
        // In a real app, we would call the API
        // const userData = await apiService.auth.getCurrentUser();
        
        // For development, check localStorage
        const isAuthenticated = localStorage.getItem('isAuthenticated');
        const storedUser = localStorage.getItem('user');
        
        if (isAuthenticated && storedUser) {
          setUser(JSON.parse(storedUser));
        }
      } catch (err) {
        console.error('Auth check error:', err);
        setError('Failed to authenticate user');
      } finally {
        setIsLoading(false);
      }
    };

    checkAuth();
  }, []);

  const login = async (username: string, password: string) => {
    try {
      setIsLoading(true);
      setError(null);
      
      // In a real app, we would call the API
      // const response = await apiService.auth.login(username, password);
      // localStorage.setItem('authToken', response.token);
      // setUser(response.user);
      
      // For development, use dummy data
      if (username === dummyCredentials.username && password === dummyCredentials.password) {
        localStorage.setItem('isAuthenticated', 'true');
        localStorage.setItem('user', JSON.stringify(dummyUser));
        setUser(dummyUser as unknown as User);
        router.push('/dashboard');
      } else {
        throw new Error(`Invalid credentials. Use ${dummyCredentials.username}/${dummyCredentials.password}`);
      }
    } catch (err) {
      console.error('Login error:', err);
      setError(err instanceof Error ? err.message : 'Failed to login');
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  const logout = async () => {
    try {
      setIsLoading(true);
      
      // In a real app, we would call the API
      // await apiService.auth.logout();
      
      // Clear local storage and state
      localStorage.removeItem('isAuthenticated');
      localStorage.removeItem('user');
      localStorage.removeItem('authToken');
      setUser(null);
      
      // Redirect to login page
      router.push('/login');
    } catch (err) {
      console.error('Logout error:', err);
      setError('Failed to logout');
    } finally {
      setIsLoading(false);
    }
  };

  return {
    user,
    isLoading,
    error,
    login,
    logout
  };
}

export default useAuth; 