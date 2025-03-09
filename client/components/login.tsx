"use client"

import { useState } from "react";
import { motion } from "framer-motion";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { User, Lock, Heart } from "lucide-react";
import Image from "next/image";
import { ThemeToggle } from '@/components/ThemeToggle';

// Import auth hook
import { useAppAuth } from "@/context/AppContext";

// Import dummy credentials for development
import { dummyCredentials } from "@/lib/dummy-data";

export const Login = () => {
    const { login, error: authError, isLoading } = useAppAuth();
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [error, setError] = useState<string | null>(null);

    const handleLogin = async (e: React.FormEvent) => {
        e.preventDefault();
        setError(null);
        
        try {
            await login(username, password);
            // No need to redirect here as the hook handles it
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to login');
        }
    };

    // Use auth error if available, otherwise use local error
    const displayError = authError || error;

    return (
        <div className="min-h-screen flex flex-col items-center justify-center bg-[#60a5fa] dark:bg-gray-900 p-4">
            <Card className="w-full max-w-md bg-white dark:bg-gray-800 shadow-xl">
                <CardContent className="p-0">
                    <div className="grid grid-cols-1 md:grid-cols-1">
                        {/* Login Form */}
                        <div className="p-6">
                            <div className="flex justify-end mb-4">
                                <ThemeToggle />
                            </div>
                            <div className="text-center mb-8">
                                <motion.div
                                    initial={{ scale: 0 }}
                                    animate={{ scale: 1 }}
                                    transition={{ delay: 0.3, type: "spring", stiffness: 200 }}
                                    className="flex justify-center w-full mb-4"
                                >
                                    <Image 
                                        src="/lockedin.svg"
                                        alt="Lockdin Logo" 
                                        width={2400}
                                        height={1200}
                                        className="h-96 w-auto"
                                        priority
                                    />
                                </motion.div>
                                <motion.h1
                                    initial={{ opacity: 0, y: -10 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    transition={{ delay: 0.4 }}
                                    className="text-3xl font-bold text-gray-900 dark:text-white"
                                >
                                    Welcome to LOCKDIN
                                </motion.h1>
                                <motion.p
                                    initial={{ opacity: 0, y: -10 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    transition={{ delay: 0.5 }}
                                    className="text-gray-600 dark:text-gray-300"
                                >
                                    Your health accountability partner
                                </motion.p>
                            </div>
                            <form onSubmit={handleLogin} className="space-y-5">
                                <motion.div 
                                    initial={{ opacity: 0, y: 10 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    transition={{ delay: 0.6 }}
                                    className="space-y-2"
                                >
                                    <Label htmlFor="username" className="text-gray-700 dark:text-gray-300 flex items-center gap-2">
                                        <User className="h-4 w-4" /> Username
                                    </Label>
                                    <Input
                                        id="username"
                                        type="text"
                                        placeholder="Enter your username"
                                        value={username}
                                        onChange={(e) => setUsername(e.target.value)}
                                        className="border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white"
                                        required
                                    />
                                </motion.div>
                                
                                <motion.div 
                                    initial={{ opacity: 0, y: 10 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    transition={{ delay: 0.7 }}
                                    className="space-y-2"
                                >
                                    <Label htmlFor="password" className="text-gray-700 dark:text-gray-300 flex items-center gap-2">
                                        <Lock className="h-4 w-4" /> Password
                                    </Label>
                                    <Input
                                        id="password"
                                        type="password"
                                        placeholder="Enter your password"
                                        value={password}
                                        onChange={(e) => setPassword(e.target.value)}
                                        className="border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white"
                                        required
                                    />
                                </motion.div>
                                
                                {displayError && (
                                    <motion.div
                                        initial={{ opacity: 0, height: 0 }}
                                        animate={{ opacity: 1, height: 'auto' }}
                                        className="bg-red-100 dark:bg-red-900 text-red-800 dark:text-red-200 p-3 rounded-md text-sm"
                                    >
                                        {displayError}
                                    </motion.div>
                                )}
                                
                                <motion.div
                                    initial={{ opacity: 0, y: 10 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    transition={{ delay: 0.8 }}
                                >
                                    <Button 
                                        type="submit" 
                                        className="w-full bg-[#60a5fa] hover:bg-[#3b82f6] text-white dark:bg-blue-700 dark:hover:bg-blue-600"
                                        disabled={isLoading}
                                    >
                                        {isLoading ? 'Logging in...' : 'Login'}
                                    </Button>
                                </motion.div>
                                
                                <motion.p 
                                    initial={{ opacity: 0 }}
                                    animate={{ opacity: 1 }}
                                    transition={{ delay: 0.9 }}
                                    className="text-center text-sm text-gray-600 dark:text-gray-400 mt-4"
                                >
                                    For demo, use: {dummyCredentials[0].username} / {dummyCredentials[0].password}
                                </motion.p>
                            </form>
                        </div>
                    </div>
                </CardContent>
            </Card>
        </div>
    );
}; 