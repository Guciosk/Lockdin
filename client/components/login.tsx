"use client"

import { useState } from "react";
import { motion } from "framer-motion";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { User, Lock, Heart } from "lucide-react";

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
        <div className="min-h-screen flex items-center justify-center bg-[#f8fafc]">
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5 }}
                className="w-[90%] max-w-md"
            >
                <Card className="border-[#60a5fa] shadow-lg overflow-hidden">
                    <CardHeader className="bg-[#60a5fa] text-white pb-6">
                        <motion.div
                            initial={{ opacity: 0, y: -10 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: 0.2, duration: 0.5 }}
                        >
                            <CardTitle className="text-3xl font-bold text-center flex flex-col items-center gap-2">
                                <motion.div
                                    initial={{ scale: 0 }}
                                    animate={{ scale: 1 }}
                                    transition={{ delay: 0.3, type: "spring", stiffness: 200 }}
                                >
                                    <Heart className="h-12 w-12 text-white mb-2" />
                                </motion.div>
                                Welcome to LOCKDIN
                            </CardTitle>
                            <p className="text-center text-white/80 mt-2">Your health accountability partner</p>
                        </motion.div>
                    </CardHeader>
                    <CardContent className="pt-6">
                        <form onSubmit={handleLogin} className="space-y-5">
                            <motion.div 
                                className="space-y-2"
                                initial={{ opacity: 0, x: -20 }}
                                animate={{ opacity: 1, x: 0 }}
                                transition={{ delay: 0.4, duration: 0.5 }}
                            >
                                <Label htmlFor="username" className="text-sm font-medium flex items-center gap-2">
                                    <User className="h-4 w-4 text-[#60a5fa]" /> Username
                                </Label>
                                <Input
                                    id="username"
                                    type="text"
                                    placeholder="Enter your username"
                                    value={username}
                                    onChange={(e) => setUsername(e.target.value)}
                                    className="border-[#60a5fa] focus:ring-[#60a5fa] focus:border-[#60a5fa]"
                                    required
                                    disabled={isLoading}
                                />
                            </motion.div>
                            <motion.div 
                                className="space-y-2"
                                initial={{ opacity: 0, x: -20 }}
                                animate={{ opacity: 1, x: 0 }}
                                transition={{ delay: 0.5, duration: 0.5 }}
                            >
                                <Label htmlFor="password" className="text-sm font-medium flex items-center gap-2">
                                    <Lock className="h-4 w-4 text-[#60a5fa]" /> Password
                                </Label>
                                <Input
                                    id="password"
                                    type="password"
                                    placeholder="Enter your password"
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                    className="border-[#60a5fa] focus:ring-[#60a5fa] focus:border-[#60a5fa]"
                                    required
                                    disabled={isLoading}
                                />
                            </motion.div>
                            {displayError && (
                                <motion.p 
                                    className="text-sm text-[#f87171] text-center"
                                    initial={{ opacity: 0, scale: 0.8 }}
                                    animate={{ opacity: 1, scale: 1 }}
                                    transition={{ duration: 0.3 }}
                                >
                                    {displayError}
                                </motion.p>
                            )}
                            <motion.div
                                initial={{ opacity: 0, y: 20 }}
                                animate={{ opacity: 1, y: 0 }}
                                transition={{ delay: 0.6, duration: 0.5 }}
                            >
                                <Button 
                                    type="submit" 
                                    className="w-full bg-[#f87171] hover:bg-[#ef4444] text-white font-medium py-6 rounded-lg shadow-md hover:shadow-lg transition-all duration-200"
                                    disabled={isLoading}
                                >
                                    {isLoading ? 'Logging in...' : 'Login'}
                                </Button>
                            </motion.div>
                            <motion.p 
                                className="text-xs text-center text-gray-500 mt-4"
                                initial={{ opacity: 0 }}
                                animate={{ opacity: 1 }}
                                transition={{ delay: 0.7, duration: 0.5 }}
                            >
                                Use username: <span className="text-[#60a5fa]">{dummyCredentials.username}</span> and password: <span className="text-[#60a5fa]">{dummyCredentials.password}</span>
                            </motion.p>
                        </form>
                    </CardContent>
                </Card>
            </motion.div>
        </div>
    );
}; 