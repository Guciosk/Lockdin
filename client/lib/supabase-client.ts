import { createClient } from '@/utils/supabase/client';

// Define types based on the Supabase schema
export interface FeedItem {
  id: number;
  created_at: string;
  user_id: number;
  task_id: number;
  image_url: string | null;
  status: string;
  timestamp: string;
  post_content: string | null;
}

export interface Task {
  id: number;
  created_at: string;
  user_id: number;
  description: string;
  due_time: string;
  status: string;
}

export interface User {
  id: number;
  created_at: string;
  username: string;
  phone_number: string | null;
  points: number;
  discord_user_id: string | null;
}

export interface FeedItemWithDetails {
  id: number;
  created_at: string;
  user_id: number;
  task_id: number;
  image_url: string | null;
  status: string;
  timestamp: string;
  post_content: string | null;
  username: string;
  task_description: string;
  due_time: string;
  points: number;
}

// Function to fetch feed items with user and task details
export async function getFeedItems(): Promise<FeedItemWithDetails[]> {
  const supabase = createClient();
  
  // Fetch feed items
  const { data: feedItems, error: feedError } = await supabase
    .from('feed')
    .select('*')
    .order('created_at', { ascending: false })
    .limit(10);
  
  if (feedError) {
    console.error('Error fetching feed items:', feedError);
    return [];
  }
  
  if (!feedItems || feedItems.length === 0) {
    return [];
  }
  
  // Get unique user IDs and task IDs
  const userIds = [...new Set(feedItems.map(item => item.user_id))];
  const taskIds = [...new Set(feedItems.map(item => item.task_id))];
  
  // Fetch users
  const { data: users, error: usersError } = await supabase
    .from('users')
    .select('*')
    .in('id', userIds);
  
  if (usersError) {
    console.error('Error fetching users:', usersError);
    return [];
  }
  
  // Fetch tasks
  const { data: tasks, error: tasksError } = await supabase
    .from('tasks')
    .select('*')
    .in('id', taskIds);
  
  if (tasksError) {
    console.error('Error fetching tasks:', tasksError);
    return [];
  }
  
  // Create a map for quick lookups
  const userMap = new Map(users?.map(user => [user.id, user]));
  const taskMap = new Map(tasks?.map(task => [task.id, task]));
  
  // Combine the data
  const feedItemsWithDetails = feedItems.map(item => {
    const user = userMap.get(item.user_id);
    const task = taskMap.get(item.task_id);
    
    return {
      ...item,
      username: user?.username || 'Unknown User',
      task_description: task?.description || 'Unknown Task',
      due_time: task?.due_time || '',
      points: user?.points || 0
    };
  });
  
  return feedItemsWithDetails;
}

// Function to fetch recent images from the storage bucket
export async function getRecentImages(limit: number = 5): Promise<string[]> {
  const supabase = createClient();
  
  // List files in the 'notes' bucket
  const { data, error } = await supabase
    .storage
    .from('notes')
    .list('', {
      limit,
      sortBy: { column: 'created_at', order: 'desc' }
    });
  
  if (error) {
    console.error('Error fetching images from storage:', error);
    return [];
  }
  
  if (!data || data.length === 0) {
    return [];
  }
  
  // Filter for image files only
  const imageFiles = data.filter(file => 
    file.name.match(/\.(jpeg|jpg|png|gif|svg)$/i)
  );
  
  // Get public URLs for each image
  const imageUrls = await Promise.all(
    imageFiles.map(async (file) => {
      const { data: urlData } = supabase
        .storage
        .from('notes')
        .getPublicUrl(file.name);
      
      return urlData.publicUrl;
    })
  );
  
  return imageUrls;
} 