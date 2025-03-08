/**
 * User Stats Hook
 *
 * Custom hook for handling user statistics functionality.
 * Provides user stats fetching and progress calculation.
 */

import { useState, useEffect } from "react";
import apiService from "@/lib/api";

interface UserStats {
  totalPoints: number;
  tasksCompleted: number;
  currentStreak: number;
  level: number;
  xpToNextLevel: number;
  progressPercentage: number;
  isHealthy: boolean;
}

interface UseUserStatsReturn {
  stats: UserStats;
  isLoading: boolean;
  error: string | null;
  refreshStats: () => Promise<void>;
}

export function useUserStats(userId?: number): UseUserStatsReturn {
  const [stats, setStats] = useState<UserStats>({
    totalPoints: 0,
    tasksCompleted: 0,
    currentStreak: 0,
    level: 1,
    xpToNextLevel: 100,
    progressPercentage: 0,
    isHealthy: true,
  });
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const calculateLevel = (
    points: number
  ): { level: number; xpToNextLevel: number } => {
    // Simple level calculation: level = 1 + floor(points / 100)
    const level = 1 + Math.floor(points / 100);

    // XP needed for next level
    const xpToNextLevel = level * 100 - points;

    return { level, xpToNextLevel };
  };

  const fetchStats = async () => {
    try {
      setIsLoading(true);

      const statsData = await apiService.user.getUserStats(userId);

      const { totalPoints, tasksCompleted, currentStreak } = statsData;

      const { level, xpToNextLevel } = calculateLevel(totalPoints);
      const progressPercentage =
        ((level * 100 - xpToNextLevel) / (level * 100)) * 100;
      const isHealthy = progressPercentage > 20;

      setStats({
        totalPoints,
        tasksCompleted,
        currentStreak,
        level,
        xpToNextLevel,
        progressPercentage,
        isHealthy,
      });
    } catch (err) {
      console.error("Fetch user stats error:", err);
      setError("Failed to fetch user statistics");
    } finally {
      setIsLoading(false);
    }
  };

  // Fetch stats on mount or when userId changes
  useEffect(() => {
    fetchStats();
  }, [userId]);

  const refreshStats = async () => {
    await fetchStats();
  };

  return {
    stats,
    isLoading,
    error,
    refreshStats,
  };
}

export default useUserStats;
