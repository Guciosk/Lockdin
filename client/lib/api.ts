/**
 * API Service
 *
 * This file contains all API calls to the backend server.
 * It uses Axios for HTTP requests and provides a centralized place for API endpoints.
 */

import axios from "axios";

// Create an axios instance with default config
const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000",
  headers: {
    "Content-Type": "application/json",
  },
  timeout: 10000, // 10 seconds
});

// Add request interceptor for authentication
api.interceptors.request.use(
  (config) => {
    // Get token from localStorage if it exists
    const token =
      typeof window !== "undefined" ? localStorage.getItem("authToken") : null;

    // If token exists, add it to the headers
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    return config;
  },
  (error) => Promise.reject(error)
);

// Types
export interface User {
  id: number;
  username: string;
  email: string;
  fullName: string;
  image: string;
}

export interface Task {
  id: number;
  title: string;
  description: string;
  dueDate: string;
  status: string;
  category: string;
  userId: number;
}

export interface FeedPost {
  id: number;
  title: string;
  description: string;
  username: string;
  userImage: string;
  goalImage: string;
  dueDate: string;
  status: string;
  isComplete: boolean;
  createdAt: string;
  likes?: number;
  comments?: number;
}

// Authentication API
export const authAPI = {
  login: async (username: string, password: string) => {
    try {
      const response = await api.post("/auth/login", { username, password });
      return response.data;
    } catch (error) {
      console.error("Login error:", error);
      throw error;
    }
  },

  logout: async () => {
    try {
      const response = await api.post("/auth/logout");
      return response.data;
    } catch (error) {
      console.error("Logout error:", error);
      throw error;
    }
  },

  getCurrentUser: async () => {
    try {
      const response = await api.get("/auth/me");
      return response.data;
    } catch (error) {
      console.error("Get current user error:", error);
      throw error;
    }
  },
};

// Tasks API
export const tasksAPI = {
  getAllTasks: async () => {
    try {
      const response = await api.get("/tasks");
      return response.data;
    } catch (error) {
      console.error("Get all tasks error:", error);
      throw error;
    }
  },

  getTaskById: async (taskId: number) => {
    try {
      const response = await api.get(`/tasks/${taskId}`);
      return response.data;
    } catch (error) {
      console.error(`Get task ${taskId} error:`, error);
      throw error;
    }
  },

  createTask: async (task: Omit<Task, "id">) => {
    try {
      const response = await api.post("/tasks", task);
      return response.data;
    } catch (error) {
      console.error("Create task error:", error);
      throw error;
    }
  },

  updateTask: async (taskId: number, task: Partial<Task>) => {
    try {
      const response = await api.put(`/tasks/${taskId}`, task);
      return response.data;
    } catch (error) {
      console.error(`Update task ${taskId} error:`, error);
      throw error;
    }
  },

  deleteTask: async (taskId: number) => {
    try {
      const response = await api.delete(`/tasks/${taskId}`);
      return response.data;
    } catch (error) {
      console.error(`Delete task ${taskId} error:`, error);
      throw error;
    }
  },

  markTaskComplete: async (taskId: number) => {
    try {
      const response = await api.patch(`/tasks/${taskId}/complete`, {
        status: "Complete",
        isComplete: true,
      });
      return response.data;
    } catch (error) {
      console.error(`Mark task ${taskId} complete error:`, error);
      throw error;
    }
  },
};

// Feed API
export const feedAPI = {
  getFeedPosts: async () => {
    try {
      const response = await api.get("/feed");
      return response.data;
    } catch (error) {
      console.error("Get feed posts error:", error);
      throw error;
    }
  },

  createFeedPost: async (post: Omit<FeedPost, "id" | "createdAt">) => {
    try {
      const response = await api.post("/feed", post);
      return response.data;
    } catch (error) {
      console.error("Create feed post error:", error);
      throw error;
    }
  },

  likePost: async (postId: number) => {
    try {
      const response = await api.post(`/feed/${postId}/like`);
      return response.data;
    } catch (error) {
      console.error(`Like post ${postId} error:`, error);
      throw error;
    }
  },

  commentOnPost: async (postId: number, comment: string) => {
    try {
      const response = await api.post(`/feed/${postId}/comment`, { comment });
      return response.data;
    } catch (error) {
      console.error(`Comment on post ${postId} error:`, error);
      throw error;
    }
  },
};

// User API
export const userAPI = {
  getUserStats: async (userId: number) => {
    try {
      const response = await api.get(`/users/${userId}/stats`);
      return response.data;
    } catch (error) {
      console.error(`Get user ${userId} stats error:`, error);
      throw error;
    }
  },

  updateUserProfile: async (userId: number, profileData: Partial<User>) => {
    try {
      const response = await api.put(`/users/${userId}`, profileData);
      return response.data;
    } catch (error) {
      console.error(`Update user ${userId} profile error:`, error);
      throw error;
    }
  },
};

// Export a default object with all APIs
const apiService = {
  auth: authAPI,
  tasks: tasksAPI,
  feed: feedAPI,
  user: userAPI,
};

export default apiService;
