/**
 * Tasks Hook
 * 
 * Custom hook for handling task-related functionality.
 * Provides task fetching, creation, updating, and deletion.
 */

import { useState, useEffect } from 'react';
import apiService, { Task } from '@/lib/api';
import { dummyUserGoals } from '@/lib/dummy-data';

interface UseTasksReturn {
  tasks: Task[];
  isLoading: boolean;
  error: string | null;
  createTask: (task: Omit<Task, 'id'>) => Promise<void>;
  updateTask: (taskId: number, task: Partial<Task>) => Promise<void>;
  deleteTask: (taskId: number) => Promise<void>;
  markTaskComplete: (taskId: number) => Promise<void>;
}

export function useTasks(): UseTasksReturn {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Fetch tasks on mount
  useEffect(() => {
    const fetchTasks = async () => {
      try {
        setIsLoading(true);
        
        // In a real app, we would call the API
        // const tasksData = await apiService.tasks.getAllTasks();
        // setTasks(tasksData);
        
        // For development, use dummy data
        // Convert dummyUserGoals to Task type
        const dummyTasks = dummyUserGoals.map(goal => ({
          id: goal.id,
          title: goal.title,
          description: goal.description,
          dueDate: goal.dueDate,
          status: goal.status,
          category: goal.category,
          userId: 1 // Dummy user ID
        }));
        
        setTasks(dummyTasks);
      } catch (err) {
        console.error('Fetch tasks error:', err);
        setError('Failed to fetch tasks');
      } finally {
        setIsLoading(false);
      }
    };

    fetchTasks();
  }, []);

  const createTask = async (task: Omit<Task, 'id'>) => {
    try {
      setIsLoading(true);
      
      // In a real app, we would call the API
      // const newTask = await apiService.tasks.createTask(task);
      
      // For development, simulate API call
      const newTask: Task = {
        ...task,
        id: Math.max(0, ...tasks.map(t => t.id)) + 1
      };
      
      setTasks(prevTasks => [...prevTasks, newTask]);
      
      return newTask;
    } catch (err) {
      console.error('Create task error:', err);
      setError('Failed to create task');
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  const updateTask = async (taskId: number, taskUpdate: Partial<Task>) => {
    try {
      setIsLoading(true);
      
      // In a real app, we would call the API
      // const updatedTask = await apiService.tasks.updateTask(taskId, taskUpdate);
      
      // For development, simulate API call
      setTasks(prevTasks => 
        prevTasks.map(task => 
          task.id === taskId ? { ...task, ...taskUpdate } : task
        )
      );
    } catch (err) {
      console.error(`Update task ${taskId} error:`, err);
      setError('Failed to update task');
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  const deleteTask = async (taskId: number) => {
    try {
      setIsLoading(true);
      
      // In a real app, we would call the API
      // await apiService.tasks.deleteTask(taskId);
      
      // For development, simulate API call
      setTasks(prevTasks => prevTasks.filter(task => task.id !== taskId));
    } catch (err) {
      console.error(`Delete task ${taskId} error:`, err);
      setError('Failed to delete task');
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  const markTaskComplete = async (taskId: number) => {
    try {
      setIsLoading(true);
      
      // In a real app, we would call the API
      // await apiService.tasks.markTaskComplete(taskId);
      
      // For development, simulate API call
      setTasks(prevTasks => 
        prevTasks.map(task => 
          task.id === taskId 
            ? { ...task, status: 'Complete', isComplete: true } 
            : task
        )
      );
    } catch (err) {
      console.error(`Mark task ${taskId} complete error:`, err);
      setError('Failed to mark task as complete');
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  return {
    tasks,
    isLoading,
    error,
    createTask,
    updateTask,
    deleteTask,
    markTaskComplete
  };
}

export default useTasks; 