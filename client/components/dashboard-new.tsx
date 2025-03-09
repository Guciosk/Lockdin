"use client"

/**
 * Dashboard Component
 * 
 * This is the main dashboard component for the LOCKDIN application.
 * It displays the user's goals, community feed, and provides functionality
 * for adding new goals and tracking progress.
 */

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { X, Plus, Trophy, Calendar, Clock, Heart, Brain, Zap } from "lucide-react";

import { createClient } from "@/utils/supabase/client";

// Import dummy data and interfaces from the dedicated file
import { 
    Goal, 
    UserStats, 
    UserGoal,
    dummyNewsFeed, 
    dummyUserGoals,
    calculatePoints, 
    generateUserStats 
} from "@/lib/dummy-data";

/**
 * AddTaskModal Component
 * 
 * A modal dialog for adding new tasks with an Instagram/game-like feel.
 * Includes animations and a more engaging UI.
 */
const AddTaskModal = ({ isOpen, onClose, onAddTask }: { 
    isOpen: boolean; 
    onClose: () => void;
    onAddTask: (title: string, description: string, dueDate: string) => void;
}) => {
    const [title, setTitle] = useState("");
    const [description, setDescription] = useState("");
    const [dueDate, setDueDate] = useState("");
    const [dueTime, setDueTime] = useState("23:59"); // Default to end of day
    
    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        // Combine date and time for the due date
        const combinedDueDate = `${dueDate}T${dueTime}`;
        onAddTask(title, description, combinedDueDate);
        // Reset form
        setTitle("");
        setDescription("");
        setDueDate("");
        setDueTime("23:59");
        onClose();
    };
    
    if (!isOpen) return null;
    
    return (
        <AnimatePresence>
            {isOpen && (
                <motion.div 
                    className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4 backdrop-blur-sm"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    onClick={onClose}
                >
                    <motion.div 
                        className="bg-white rounded-xl shadow-xl w-full max-w-md overflow-hidden"
                        initial={{ scale: 0.9, opacity: 0 }}
                        animate={{ scale: 1, opacity: 1 }}
                        exit={{ scale: 0.9, opacity: 0 }}
                        transition={{ type: "spring", damping: 25, stiffness: 300 }}
                        onClick={(e) => e.stopPropagation()}
                    >
                        <div className="flex items-center justify-between p-4 border-b bg-[#60a5fa] text-white">
                            <h2 className="text-xl font-bold">Add New Task</h2>
                            <button 
                                onClick={onClose}
                                className="p-1 rounded-full hover:bg-white/20 transition-colors text-white"
                            >
                                <X className="h-6 w-6" />
                            </button>
                        </div>
                        
                        <form onSubmit={handleSubmit} className="p-4 space-y-4">
                            <div className="space-y-2">
                                <Label htmlFor="title" className="text-sm font-medium flex items-center gap-2">
                                    <Zap className="h-4 w-4 text-[#f87171]" /> Task Title
                                </Label>
                                <Input
                                    id="title"
                                    value={title}
                                    onChange={(e) => setTitle(e.target.value)}
                                    placeholder="What do you want to achieve?"
                                    className="border-[#60a5fa] focus:ring-[#60a5fa] focus:border-[#60a5fa]"
                                    required
                                />
                            </div>
                            
                            <div className="space-y-2">
                                <Label htmlFor="description" className="text-sm font-medium flex items-center gap-2">
                                    <Brain className="h-4 w-4 text-[#f87171]" /> Description
                                </Label>
                                <Input
                                    id="description"
                                    value={description}
                                    onChange={(e) => setDescription(e.target.value)}
                                    placeholder="Add more details about your task"
                                    className="border-[#60a5fa] focus:ring-[#60a5fa] focus:border-[#60a5fa]"
                                />
                            </div>
                            
                            <div className="space-y-2">
                                <Label htmlFor="dueDate" className="text-sm font-medium flex items-center gap-2">
                                    <Calendar className="h-4 w-4 text-[#f87171]" /> Due Date
                                </Label>
                                <Input
                                    id="dueDate"
                                    type="date"
                                    value={dueDate}
                                    onChange={(e) => setDueDate(e.target.value)}
                                    className="border-[#60a5fa] focus:ring-[#60a5fa] focus:border-[#60a5fa]"
                                    required
                                />
                            </div>
                            
                            <div className="space-y-2">
                                <Label htmlFor="dueTime" className="text-sm font-medium flex items-center gap-2">
                                    <Clock className="h-4 w-4 text-[#f87171]" /> Due Time
                                </Label>
                                <Input
                                    id="dueTime"
                                    type="time"
                                    value={dueTime}
                                    onChange={(e) => setDueTime(e.target.value)}
                                    className="border-[#60a5fa] focus:ring-[#60a5fa] focus:border-[#60a5fa]"
                                    required
                                />
                            </div>
                            
                            <div className="pt-2">
                                <Button 
                                    type="submit" 
                                    className="w-full bg-[#f87171] hover:bg-[#ef4444] text-white font-medium py-2 px-4 rounded-lg shadow-md hover:shadow-lg transition-all duration-200"
                                >
                                    Add Task (+25 XP)
                                </Button>
                            </div>
                            
                            <div className="text-center text-xs text-gray-500 pt-2">
                                Complete this task to earn points and level up!
                            </div>
                        </form>
                    </motion.div>
                </motion.div>
            )}
        </AnimatePresence>
    );
};

/**
 * FloatingActionButton Component
 * 
 * A floating button that follows the user as they scroll,
 * used to open the add task modal.
 */
const FloatingActionButton = ({ onClick }: { onClick: () => void }) => {
    return (
        <motion.button
            onClick={onClick}
            className="fixed bottom-8 right-8 w-14 h-14 bg-[#f87171] rounded-full shadow-lg flex items-center justify-center text-white hover:shadow-xl transition-all duration-200 z-40"
            aria-label="Add new task"
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.95 }}
        >
            <Plus className="h-6 w-6" />
        </motion.button>
    );
};

/**
 * UpcomingGoals Component
 * 
 * Displays the user's upcoming goals sorted by urgency level and due date.
 * Goals are color-coded based on their urgency:
 * - High (red): Due within 2 days
 * - Medium (yellow): Due within 7 days
 * - Low (green): Due beyond 7 days
 */
const UpcomingGoals = () => {
    // Sort goals by urgency (high -> medium -> low) and then by due date
    const sortedGoals = [...dummyUserGoals].sort((a, b) => {
        // First sort by urgency priority
        const urgencyPriority = { high: 0, medium: 1, low: 2 };
        const urgencyDiff = urgencyPriority[a.urgency] - urgencyPriority[b.urgency];
        
        if (urgencyDiff !== 0) return urgencyDiff;
        
        // If same urgency, sort by due date
        return new Date(a.dueDate).getTime() - new Date(b.dueDate).getTime();
    });

    return (
        <Card className="h-full border-[#60a5fa] bg-white shadow-md">
            <CardHeader className="bg-[#60a5fa] text-white">
                <CardTitle className="flex items-center gap-2">
                    <Clock className="h-5 w-5" /> Your Upcoming Tasks
                </CardTitle>
            </CardHeader>
            <CardContent>
                <div className="space-y-4 max-h-[600px] overflow-y-auto pr-2 pt-4">
                    {sortedGoals.map((goal, index) => (
                        <motion.div
                            key={goal.id}
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: index * 0.05, duration: 0.3 }}
                        >
                            <Card className="overflow-hidden border-l-4 border-l-[#60a5fa] hover:shadow-md transition-shadow duration-200">
                                <CardContent className="p-4">
                                    <div className="flex items-start justify-between">
                                        <div className="space-y-1">
                                            <div className="flex items-center gap-2">
                                                <h3 className="font-semibold">{goal.title}</h3>
                                                {goal.urgency === 'high' && (
                                                    <span className="px-2 py-1 text-xs font-medium rounded-full bg-[#fee2e2] text-[#ef4444]">
                                                        Urgent
                                                    </span>
                                                )}
                                                {goal.urgency === 'medium' && (
                                                    <span className="px-2 py-1 text-xs font-medium rounded-full bg-[#fef3c7] text-[#d97706]">
                                                        Soon
                                                    </span>
                                                )}
                                                {goal.urgency === 'low' && (
                                                    <span className="px-2 py-1 text-xs font-medium rounded-full bg-[#dcfce7] text-[#16a34a]">
                                                        Upcoming
                                                    </span>
                                                )}
                                            </div>
                                            <p className="text-sm text-gray-600">{goal.description}</p>
                                            <div className="flex items-center gap-4 text-xs text-gray-500">
                                                <span>Due: {new Date(goal.dueDate).toLocaleDateString()}</span>
                                                <span>Status: {goal.status}</span>
                                                <span>Category: {goal.category}</span>
                                            </div>
                                        </div>
                                        <div className="flex items-center gap-2">
                                            <Button 
                                                variant="outline" 
                                                size="sm"
                                                className="border-[#60a5fa] text-[#60a5fa] hover:bg-[#dbeafe] hover:text-[#2563eb] hover:border-[#2563eb] transition-colors"
                                            >
                                                Mark Complete
                                            </Button>
                                        </div>
                                    </div>
                                </CardContent>
                            </Card>
                        </motion.div>
                    ))}
                </div>
            </CardContent>
        </Card>
    );
};

/**
 * NewsFeed Component
 * 
 * Displays a social feed of goals from the community.
 * Includes a leaderboard showing top users ranked by points.
 */
const NewsFeed = () => {
    // Use the imported functions for calculating points and generating user stats
    const userStats = generateUserStats(dummyNewsFeed);

    return (
        <div className="space-y-6">
            {/* Community Leaderboard */}
            <Card className="border-[#60a5fa] bg-white shadow-md">
                <CardHeader className="bg-[#60a5fa] text-white">
                    <CardTitle className="flex items-center gap-2">
                        <Trophy className="h-5 w-5" /> Community Leaderboard
                    </CardTitle>
                </CardHeader>
                <CardContent className="pt-6">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {Object.entries(userStats)
                            .sort(([,a], [,b]) => b.points - a.points) // Sort by points
                            .map(([username, data], index) => (
                            <motion.div
                                key={username}
                                initial={{ opacity: 0, scale: 0.95 }}
                                animate={{ opacity: 1, scale: 1 }}
                                transition={{ delay: index * 0.1, duration: 0.3 }}
                            >
                                <Card key={username} className={`bg-white ${index === 0 ? 'border-2 border-[#fbbf24]' : 'border-[#e5e7eb]'} hover:shadow-md transition-shadow duration-200`}>
                                    <CardContent className="pt-4">
                                        <div className="flex items-center gap-4">
                                            <div className={`relative ${index === 0 ? 'ring-2 ring-[#fbbf24] ring-offset-2' : ''} rounded-full`}>
                                                <img 
                                                    src={data.userImage} 
                                                    alt={username} 
                                                    className="w-12 h-12 rounded-full"
                                                />
                                                {index < 3 && (
                                                    <span className={`absolute -top-2 -right-2 w-6 h-6 flex items-center justify-center rounded-full ${index === 0 ? 'bg-[#fbbf24]' : index === 1 ? 'bg-[#94a3b8]' : 'bg-[#b45309]'} text-white text-sm font-bold`}>
                                                        {index + 1}
                                                    </span>
                                                )}
                                            </div>
                                            <div>
                                                <h3 className="font-bold">{username}</h3>
                                                <p className="text-sm text-[#60a5fa]">
                                                    🏆 {data.points} points • {data.goals.length} tasks
                                                </p>
                                            </div>
                                        </div>
                                    </CardContent>
                                </Card>
                            </motion.div>
                        ))}
                    </div>
                </CardContent>
            </Card>

            {/* Community Feed Posts */}
            <div className="space-y-6">
                {dummyNewsFeed.map((item, index) => (
                    <motion.div
                        key={item.id}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: index * 0.1, duration: 0.3 }}
                    >
                        <Card className="overflow-hidden hover:shadow-md transition-shadow duration-200 border-[#e5e7eb] bg-white">
                            {/* Post Header */}
                            <div className="p-4 border-b border-gray-100">
                                <div className="flex items-center gap-3">
                                    <img 
                                        src={item.userImage} 
                                        alt={item.username} 
                                        className="w-8 h-8 rounded-full"
                                    />
                                    <div className="flex-1">
                                        <h3 className="font-semibold">{item.username}</h3>
                                        <p className="text-xs text-gray-500">
                                            {item.status} • {new Date(item.createdAt).toLocaleDateString()}
                                        </p>
                                    </div>
                                    <div className="text-sm font-medium text-[#f87171]">
                                        +{item.status === "Complete" ? "50" : "25"} pts
                                    </div>
                                </div>
                            </div>
                            
                            {/* Post Image */}
                            <div className="aspect-square relative">
                                <img 
                                    src={item.goalImage} 
                                    alt={item.title}
                                    className="w-full h-full object-cover"
                                />
                                <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/60 to-transparent p-4">
                                    <h4 className="text-white font-bold">{item.title}</h4>
                                    <p className="text-white/90 text-sm">Due: {new Date(item.dueDate).toLocaleDateString()}</p>
                                </div>
                            </div>

                            {/* Post Interactions */}
                            <CardContent className="pt-4">
                                <div className="flex items-center gap-4 mb-3">
                                    <motion.button 
                                        className="text-gray-500 hover:text-[#f87171] transition-colors"
                                        whileHover={{ scale: 1.1 }}
                                        whileTap={{ scale: 0.95 }}
                                    >
                                        <Heart className="h-6 w-6" />
                                    </motion.button>
                                    <motion.button 
                                        className="text-gray-500 hover:text-[#60a5fa] transition-colors"
                                        whileHover={{ scale: 1.1 }}
                                        whileTap={{ scale: 0.95 }}
                                    >
                                        <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                                        </svg>
                                    </motion.button>
                                </div>
                                <div className="space-y-2">
                                    <p className="text-sm">
                                        <span className="font-bold">{item.likes} likes</span> • <span className="text-gray-500">{item.comments} comments</span>
                                    </p>
                                    <p className="text-sm">
                                        <span className="font-bold">{item.username}</span> {item.description}
                                    </p>
                                </div>
                            </CardContent>
                        </Card>
                    </motion.div>
                ))}
            </div>
        </div>
    );
};

/**
 * Dashboard Component
 * 
 * The main dashboard page that combines all dashboard elements:
 * - Header with user info and logout button
 * - Floating action button for adding new tasks
 * - Upcoming goals list
 * - Community feed
 * - User statistics
 */
const Dashboard = () => {
    const router = useRouter();
    const supabase = createClient();
    
    // State for task modal
    const [isAddTaskModalOpen, setIsAddTaskModalOpen] = useState(false);
    const [user, setUser] = useState<any>(null);
    const appName = "LOCKDIN";
    
    // Progress calculation
    const totalXP = 350;
    const xpToNextLevel = 500;
    const progressPercentage = (totalXP / xpToNextLevel) * 100;
    const isHealthy = progressPercentage > 20;

    /**
     * Check authentication status on component mount
     * Redirects to login page if user is not authenticated
     */
    useEffect(() => {
        // Check authentication
        const isAuthenticated = localStorage.getItem("isAuthenticated");
        const storedUser = localStorage.getItem("user");

        if (!isAuthenticated || !storedUser) {
            router.push("/login");
            return;
        }

        setUser(JSON.parse(storedUser));
    }, [router]);

    /**
     * Handle user logout
     * Clears authentication data and redirects to login page
     */
    const handleLogout = () => {
        localStorage.removeItem("isAuthenticated");
        localStorage.removeItem("user");
        router.push("/login");
    };

    /**
     * Adds a new task to the database
     * @param title - The title of the task
     * @param description - The detailed description of the task
     * @param dueDate - The due date for task completion (format: YYYY-MM-DDThh:mm)
     * @returns Promise that resolves when the task is added
     */
    const handleAddTask = async (title: string, description: string, dueDate: string) => {
        const supabase = createClient();
        
        try {
            // First, check if the user exists in the database
            let userId;
            
            if (user?.email) {
                // Try to find the user by email
                const { data: userData, error: userError } = await supabase
                    .from('users')
                    .select('id')
                    .eq('username', user.email)
                    .single();
                
                if (userError || !userData) {
                    console.log("User not found, defaulting to admin user");
                    
                    // Check if admin user exists
                    const { data: adminData, error: adminError } = await supabase
                        .from('users')
                        .select('id')
                        .eq('username', 'admin')
                        .single();
                    
                    if (adminError || !adminData) {
                        console.log("Admin user not found, creating admin user");
                        
                        // Create admin user
                        const { data: newAdminData, error: createError } = await supabase
                            .from('users')
                            .insert([{
                                username: 'admin',
                                created_at: new Date().toISOString(),
                                points: 0,
                                phone_number: null,
                                discord_user_id: null
                            }])
                            .select();
                        
                        if (createError || !newAdminData || newAdminData.length === 0) {
                            console.error("Failed to create admin user:", createError?.message);
                            alert("Failed to add task. Could not create admin user.");
                            return;
                        }
                        
                        userId = newAdminData[0].id;
                    } else {
                        userId = adminData.id;
                    }
                } else {
                    userId = userData.id;
                }
            } else {
                // Default to admin user if no user is logged in
                // Check if admin user exists
                const { data: adminData, error: adminError } = await supabase
                    .from('users')
                    .select('id')
                    .eq('username', 'admin')
                    .single();
                
                if (adminError || !adminData) {
                    console.log("Admin user not found, creating admin user");
                    
                    // Create admin user
                    const { data: newAdminData, error: createError } = await supabase
                        .from('users')
                        .insert([{
                            username: 'admin',
                            created_at: new Date().toISOString(),
                            points: 0,
                            phone_number: null,
                            discord_user_id: null
                        }])
                        .select();
                    
                    if (createError || !newAdminData || newAdminData.length === 0) {
                        console.error("Failed to create admin user:", createError?.message);
                        alert("Failed to add task. Could not create admin user.");
                        return;
                    }
                    
                    userId = newAdminData[0].id;
                } else {
                    userId = adminData.id;
                }
            }
            
            // Convert the date string to a UTC Date object
            // The dueDate format should be YYYY-MM-DDThh:mm
            const dueDateObj = new Date(dueDate);
            const utcDueDate = dueDateObj.toISOString();
            
            // Prepare task data according to the schema
            const newTaskData = {
                user_id: userId,
                description: description,
                due_time: utcDueDate, // Store as UTC ISO string
                status: "pending", // Default status is pending
                created_at: new Date().toISOString()
            };

            // Insert task into the tasks table
            const { data: insertedTask, error: taskError } = await supabase
                .from('tasks')
                .insert([newTaskData])
                .select();

            // Handle database errors
            if (taskError) {
                console.error("Error adding task:", taskError.message);
                alert("Failed to add task. Please try again.");
                return;
            }
            
            // Check if task was inserted and we have the ID
            if (!insertedTask || insertedTask.length === 0) {
                console.error("Task was not inserted properly");
                alert("Failed to add task. Please try again.");
                return;
            }
            
            // Check if we should post to the feed
            if (description && description.trim().length > 0) {
                // Prepare feed data
                const feedData = {
                    user_id: userId,
                    task_id: insertedTask[0].id,
                    image_url: null, // Optional image
                    status: "pending",
                    timestamp: new Date().toISOString(),
                    post_content: description
                };
                
                // Insert into feed table
                const { error: feedError } = await supabase
                    .from('feed')
                    .insert([feedData]);
                
                if (feedError) {
                    console.error("Error adding to feed:", feedError.message);
                    // Continue even if feed post fails
                }
            }
            
            // Success handling
            console.log("Task added successfully");
            alert("Task added successfully! +25 XP");
            
            // Update user points
            const { error: pointsError } = await supabase
                .from('users')
                .update({ points: supabase.rpc('increment', { x: 25 }) })
                .eq('id', userId);
                
            if (pointsError) {
                console.error("Error updating points:", pointsError.message);
            }
            
            // Refresh the task list
            // TODO: Implement proper state refresh
            window.location.reload();
        } catch (err) {
            console.error("Error in handleAddTask:", err);
            alert("An unexpected error occurred. Please try again.");
        }
    };

    return (
        <div className="min-h-screen bg-[#f8fafc]">
            {/* Header with user info and logout */}
            <header className="bg-white shadow-md sticky top-0 z-30 border-b border-[#e5e7eb]">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex justify-between items-center">
                    <motion.h1 
                        className="text-2xl font-bold text-[#60a5fa]"
                        initial={{ opacity: 0, y: -10 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.5 }}
                    >
                        {appName}
                    </motion.h1>
                    <div className="flex items-center gap-4">
                        <motion.div 
                            className="flex items-center gap-2"
                            initial={{ opacity: 0, x: 10 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{ duration: 0.5, delay: 0.1 }}
                        >
                            <img 
                                src={user?.image} 
                                alt={user?.username} 
                                className="w-8 h-8 rounded-full border-2 border-[#60a5fa]"
                            />
                            <span className="text-sm font-medium">{user?.fullName}</span>
                        </motion.div>
                        <motion.div
                            initial={{ opacity: 0, x: 10 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{ duration: 0.5, delay: 0.2 }}
                        >
                            <Button 
                                variant="outline" 
                                onClick={handleLogout}
                                className="border-[#f87171] text-[#f87171] hover:bg-[#fee2e2] hover:text-[#ef4444] hover:border-[#ef4444]"
                            >
                                Logout
                            </Button>
                        </motion.div>
                    </div>
                </div>
            </header>

            {/* Floating Action Button */}
            <FloatingActionButton onClick={() => setIsAddTaskModalOpen(true)} />
            
            {/* Add Task Modal */}
            <AddTaskModal 
                isOpen={isAddTaskModalOpen} 
                onClose={() => setIsAddTaskModalOpen(false)}
                onAddTask={handleAddTask}
            />

            {/* Main content */}
            <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                {/* Main content grid with side-by-side layout */}
                <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
                    {/* News Feed - Takes 7 columns on large screens */}
                    <motion.div 
                        className="lg:col-span-7 space-y-6"
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.5 }}
                    >
                        <NewsFeed />
                    </motion.div>

                    {/* Right sidebar - Takes 5 columns on large screens */}
                    <motion.div 
                        className="lg:col-span-5 space-y-6"
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.5, delay: 0.2 }}
                    >
                        {/* User Stats */}
                        <Card className="bg-white border-[#60a5fa] shadow-md">
                            <CardHeader className="bg-[#60a5fa] text-white">
                                <CardTitle className="flex items-center gap-2">
                                    <Trophy className="h-5 w-5" /> Your Progress
                                </CardTitle>
                            </CardHeader>
                            <CardContent>
                                <div className="space-y-4 pt-4">
                                    <div className="flex items-center justify-between">
                                        <span className="text-sm font-medium">Total Points</span>
                                        <span className="text-2xl font-bold text-[#60a5fa]">{totalXP}</span>
                                    </div>
                                    <div className="flex items-center justify-between">
                                        <span className="text-sm font-medium">Tasks Completed</span>
                                        <span className="text-2xl font-bold text-[#60a5fa]">5</span>
                                    </div>
                                    <div className="flex items-center justify-between">
                                        <span className="text-sm font-medium">Current Streak</span>
                                        <span className="text-2xl font-bold text-[#60a5fa]">3 days</span>
                                    </div>
                                    
                                    {/* Health Bar / Progress bar */}
                                    <div className="pt-2">
                                        <div className="flex justify-between text-xs mb-1">
                                            <span>Level 3</span>
                                            <span>{totalXP}/{xpToNextLevel} XP to Level 4</span>
                                        </div>
                                        <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden border border-gray-300">
                                            <motion.div 
                                                className={`h-full rounded-full ${isHealthy ? 'bg-[#22c55e]' : 'bg-[#ef4444]'}`}
                                                style={{ width: `${progressPercentage}%` }}
                                                initial={{ width: '0%' }}
                                                animate={{ width: `${progressPercentage}%` }}
                                                transition={{ duration: 1, delay: 0.5 }}
                                            >
                                                {/* Add a subtle pulse animation for low health */}
                                                {!isHealthy && (
                                                    <motion.div 
                                                        className="w-full h-full bg-[#ef4444]"
                                                        animate={{ opacity: [0.7, 1, 0.7] }}
                                                        transition={{ 
                                                            repeat: Infinity, 
                                                            duration: 1.5,
                                                            ease: "easeInOut" 
                                                        }}
                                                    />
                                                )}
                                            </motion.div>
                                        </div>
                                        
                                        {/* Health status message */}
                                        <div className="mt-1 text-xs text-center">
                                            {isHealthy ? (
                                                <span className="text-[#22c55e] font-medium">Good progress! Keep it up!</span>
                                            ) : (
                                                <span className="text-[#ef4444] font-medium">Low progress! Complete more tasks to level up!</span>
                                            )}
                                        </div>
                                    </div>
                                </div>
                            </CardContent>
                        </Card>

                        {/* Upcoming Goals - Now in the sidebar with scrolling */}
                        <UpcomingGoals />
                    </motion.div>
                </div>
            </main>
        </div>
    );
};

export default Dashboard; 