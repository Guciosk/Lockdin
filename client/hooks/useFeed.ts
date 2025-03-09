/**
 * Feed Hook
 * 
 * Custom hook for handling feed-related functionality.
 * Provides feed post fetching, creation, liking, and commenting.
 */

import { useState, useEffect } from 'react';
import { getFeedItems, getRecentImages, FeedItemWithDetails } from '@/lib/supabase-client';
import { dummyNewsFeed } from '@/lib/dummy-data';

interface UseFeedReturn {
  feedPosts: FeedItemWithDetails[];
  recentImages: string[];
  isLoading: boolean;
  error: string | null;
}

export function useFeed(): UseFeedReturn {
  const [feedPosts, setFeedPosts] = useState<FeedItemWithDetails[]>([]);
  const [recentImages, setRecentImages] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Fetch feed posts and recent images on mount
  useEffect(() => {
    const fetchData = async () => {
      try {
        setIsLoading(true);
        
        // Fetch feed posts from Supabase
        const postsData = await getFeedItems();
        setFeedPosts(postsData);
        
        // Fetch recent images from Supabase storage
        const imagesData = await getRecentImages(5);
        setRecentImages(imagesData);
      } catch (err) {
        console.error('Fetch feed data error:', err);
        setError('Failed to fetch feed data');
        
        // Fallback to dummy data if there's an error
        setFeedPosts(dummyNewsFeed as unknown as FeedItemWithDetails[]);
      } finally {
        setIsLoading(false);
      }
    };

    fetchData();
  }, []);

  return {
    feedPosts,
    recentImages,
    isLoading,
    error
  };
}

export default useFeed; 