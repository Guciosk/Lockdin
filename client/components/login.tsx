"use client"

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

export const Login = () => {
    const router = useRouter();
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [error, setError] = useState("");

    const handleLogin = (e: React.FormEvent) => {
        e.preventDefault();
        
        // Dummy authentication
        if (username === "JDoe321" && password === "password") {
            // In a real app, we would set a proper auth token
            localStorage.setItem("isAuthenticated", "true");
            localStorage.setItem("user", JSON.stringify({
                username: "JDoe321",
                email: "johndoe@gmail.com",
                fullName: "John Doe",
                image: "https://api.dicebear.com/7.x/avataaars/svg?seed=JohnDoe"
            }));
            router.push("/dashboard");
        } else {
            setError("Invalid credentials. Use JDoe321/password");
        }
    };

    return (
        <div className="min-h-screen flex items-center justify-center bg-gray-50">
            <Card className="w-[90%] max-w-md">
                <CardHeader>
                    <CardTitle className="text-2xl text-center">Welcome to LOCKDIN</CardTitle>
                </CardHeader>
                <CardContent>
                    <form onSubmit={handleLogin} className="space-y-4">
                        <div className="space-y-2">
                            <Label htmlFor="username">Username</Label>
                            <Input
                                id="username"
                                type="text"
                                placeholder="Enter your username"
                                value={username}
                                onChange={(e) => setUsername(e.target.value)}
                                required
                            />
                        </div>
                        <div className="space-y-2">
                            <Label htmlFor="password">Password</Label>
                            <Input
                                id="password"
                                type="password"
                                placeholder="Enter your password"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                required
                            />
                        </div>
                        {error && (
                            <p className="text-sm text-red-500 text-center">{error}</p>
                        )}
                        <Button type="submit" className="w-full">
                            Login
                        </Button>
                        <p className="text-xs text-center text-gray-500 mt-4">
                            Use username: JDoe321 and password: password
                        </p>
                    </form>
                </CardContent>
            </Card>
        </div>
    );
}; 