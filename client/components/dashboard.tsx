"use client"

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label"

import { createClient } from "@/utils/supabase/client";

interface Goal {
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

interface UserStats {
    goals: Goal[];
    userImage: string;
    points: number;
}

const dummyNewsFeed = [
    {
        id: 1,
        title: "Complete Marathon Training",
        description: "Training for my first full marathon in 6 months 🏃‍♂️ #fitness #marathon #goals",
        username: "FitnessFreak",
        userImage: "https://api.dicebear.com/7.x/avataaars/svg?seed=FitnessFreak",
        goalImage: "https://images.unsplash.com/photo-1461896836934-ffe607ba8211?w=800&h=800&fit=crop",
        dueDate: "2024-09-15",
        status: "In Progress",
        isComplete: false,
        createdAt: "2024-03-10",
        likes: 124,
        comments: 15
    },
    {
        id: 2,
        title: "Learn Spanish",
        description: "¡Hola amigos! Starting my journey to learn Spanish 🇪🇸 #languagelearning #spanish",
        username: "LanguageLover",
        userImage: "https://api.dicebear.com/7.x/avataaars/svg?seed=LanguageLover",
        goalImage: "https://images.unsplash.com/photo-1545703549-7bdb1d01b734?w=800&h=800&fit=crop",
        dueDate: "2024-12-31",
        status: "Just Started",
        isComplete: false,
        createdAt: "2024-03-09",
        likes: 89,
        comments: 8
    },
    {
        id: 3,
        title: "Launch My Startup",
        description: "Building the next big thing in tech! 💻 Late night coding sessions #startup #entrepreneurship",
        username: "TechFounder",
        userImage: "https://api.dicebear.com/7.x/avataaars/svg?seed=TechFounder",
        goalImage: "https://images.unsplash.com/photo-1553877522-43269d4ea984?w=800&h=800&fit=crop",
        dueDate: "2024-06-30",
        status: "Planning",
        isComplete: false,
        createdAt: "2024-03-08",
        likes: 256,
        comments: 23
    },
    {
        id: 4,
        title: "Read 50 Books",
        description: "Current book: 'Atomic Habits' 📚 Making progress on my reading challenge! #books #reading",
        username: "BookWorm",
        userImage: "https://api.dicebear.com/7.x/avataaars/svg?seed=BookWorm",
        goalImage: "https://images.unsplash.com/photo-1512820790803-83ca734da794?w=800&h=800&fit=crop",
        dueDate: "2024-12-31",
        status: "In Progress",
        isComplete: false,
        createdAt: "2024-03-07",
        likes: 167,
        comments: 19
    }
];

const NewsFeed = () => {
    const calculatePoints = (goals: Goal[]): number => {
        const points = goals.reduce((total: number, goal: Goal) => {
            if (goal.status === "Complete") return total + 50;
            return total + 25; // Partial points for in-progress goals
        }, 0);
        return points;
    };

    // Group goals by user and calculate points
    const userStats = dummyNewsFeed.reduce<Record<string, UserStats>>((acc, goal) => {
        if (!acc[goal.username]) {
            acc[goal.username] = {
                goals: [],
                userImage: goal.userImage,
                points: 0
            };
        }
        acc[goal.username].goals.push(goal);
        acc[goal.username].points = calculatePoints(acc[goal.username].goals);
        return acc;
    }, {});

    return (
        <div className="space-y-6">
            <Card>
                <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                        🏆 Community Leaderboard
                    </CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {Object.entries(userStats)
                            .sort(([,a], [,b]) => b.points - a.points) // Sort by points
                            .map(([username, data], index) => (
                            <Card key={username} className={`bg-gray-50 ${index === 0 ? 'border-2 border-yellow-400' : ''}`}>
                                <CardContent className="pt-4">
                                    <div className="flex items-center gap-4">
                                        <div className={`relative ${index === 0 ? 'ring-2 ring-yellow-400 ring-offset-2' : ''} rounded-full`}>
                                            <img 
                                                src={data.userImage} 
                                                alt={username} 
                                                className="w-12 h-12 rounded-full"
                                            />
                                            {index < 3 && (
                                                <span className="absolute -top-2 -right-2 w-6 h-6 flex items-center justify-center rounded-full bg-yellow-400 text-white text-sm font-bold">
                                                    {index + 1}
                                                </span>
                                            )}
                                        </div>
                                        <div>
                                            <h3 className="font-bold">{username}</h3>
                                            <p className="text-sm text-blue-600">
                                                🏆 {data.points} points • {data.goals.length} goals
                                            </p>
                                        </div>
                                    </div>
                                </CardContent>
                            </Card>
                        ))}
                    </div>
                </CardContent>
            </Card>

            <div className="space-y-6">
                {dummyNewsFeed.map((item) => (
                    <Card key={item.id} className="overflow-hidden">
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
                                <div className="text-sm font-medium text-blue-600">
                                    +{item.status === "Complete" ? "50" : "25"} pts
                                </div>
                            </div>
                        </div>
                        
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

                        <CardContent className="pt-4">
                            <div className="flex items-center gap-4 mb-3">
                                <button className="hover:text-red-500">
                                    <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
                                    </svg>
                                </button>
                                <button className="hover:text-blue-500">
                                    <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                                    </svg>
                                </button>
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
                ))}
            </div>
        </div>
    );
};

const Dashboard = () => {
    const router = useRouter();
    // const supabase = createClient();
    
    const [goal, setGoal] = useState("");
    const [description, setDescription] = useState("");
    const [dueDate, setDueDate] = useState("");
    const [user, setUser] = useState<any>(null);
    const appName = "LOCKDIN";

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

    const handleLogout = () => {
        localStorage.removeItem("isAuthenticated");
        localStorage.removeItem("user");
        router.push("/login");
    };

    const handleAddGoal = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!goal || !dueDate) return;

        try {
            const { error } = await supabase
                .from('goals')
                .insert([
                    { title: goal, description, due_date: dueDate, user_email: user?.email }
                ]);

            if (error) throw error;

            // Reset form
            setGoal("");
            setDescription("");
            setDueDate("");
        } catch (error) {
            console.error('Error adding goal:', error);
        }
    };

    if (!user) {
        return null; // Or a loading spinner
    }

    return (
        <div className="container mx-auto p-6 space-y-6">
            <div className="flex justify-between items-center mb-8">
                <h1 className="text-4xl font-bold">{appName}</h1>
                <div className="flex items-center gap-4">
                    <img src={user.image} alt="User" className="w-10 h-10 rounded-full" />
                    <div className="flex items-center gap-4">
                        <div>
                            <h2 className="font-bold">{user.fullName}</h2>
                            <p className="text-sm text-gray-500">{user.email}</p>
                        </div>
                        <Button variant="outline" onClick={handleLogout}>
                            Logout
                        </Button>
                    </div>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <div className="lg:col-span-2">
                    <NewsFeed />
                </div>
                
                <div className="lg:col-span-1">
                    <Card>
                        <CardHeader>
                            <CardTitle>Add New Goal</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <form onSubmit={handleAddGoal} className="space-y-4">
                                <div className="space-y-2">
                                    <Label htmlFor="goal">Goal Title</Label>
                                    <Input
                                        id="goal"
                                        value={goal}
                                        onChange={(e) => setGoal(e.target.value)}
                                        placeholder="Enter your goal"
                                        required
                                    />
                                </div>
                                <div className="space-y-2">
                                    <Label htmlFor="description">Description</Label>
                                    <Input
                                        id="description"
                                        value={description}
                                        onChange={(e) => setDescription(e.target.value)}
                                        placeholder="Describe your goal"
                                    />
                                </div>
                                <div className="space-y-2">
                                    <Label htmlFor="dueDate">Due Date</Label>
                                    <Input
                                        id="dueDate"
                                        type="date"
                                        value={dueDate}
                                        onChange={(e) => setDueDate(e.target.value)}
                                        required
                                    />
                                </div>
                                <Button type="submit" className="w-full">
                                    Add Goal
                                </Button>
                            </form>
                        </CardContent>
                    </Card>
                </div>
            </div>
        </div>
    );
};

export { Dashboard };