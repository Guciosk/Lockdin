'use client';

/**
 * Application Context
 * 
 * Provides global state and functionality to the entire application.
 * Combines all hooks into a single context provider.
 */

import React, { createContext, useContext, ReactNode } from 'react';
import useAuth from '@/hooks/useAuth';
import useTasks from '@/hooks/useTasks';
import useFeed from '@/hooks/useFeed';
import useUserStats from '@/hooks/useUserStats';

// Create the context
interface AppContextType {
  auth: ReturnType<typeof useAuth>;
  tasks: ReturnType<typeof useTasks>;
  feed: ReturnType<typeof useFeed>;
  userStats: ReturnType<typeof useUserStats>;
}

const AppContext = createContext<AppContextType | undefined>(undefined);

// Provider component
interface AppProviderProps {
  children: ReactNode;
}

export const AppProvider: React.FC<AppProviderProps> = ({ children }) => {
  const auth = useAuth();
  const tasks = useTasks();
  const feed = useFeed();
  const userStats = useUserStats(auth.user?.id);

  const value = {
    auth,
    tasks,
    feed,
    userStats
  };

  return <AppContext.Provider value={value}>{children}</AppContext.Provider>;
};

// Custom hook to use the context
export const useApp = (): AppContextType => {
  const context = useContext(AppContext);
  if (context === undefined) {
    throw new Error('useApp must be used within an AppProvider');
  }
  return context;
};

// Export individual hooks for direct use when needed
export const useAppAuth = () => useApp().auth;
export const useAppTasks = () => useApp().tasks;
export const useAppFeed = () => useApp().feed;
export const useAppUserStats = () => useApp().userStats; 