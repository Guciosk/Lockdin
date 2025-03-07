"use client"

import { motion } from "framer-motion"
import { useRouter } from "next/navigation"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"

export const LandingPage = () => {
  const router = useRouter()

  return (
    <main className="min-h-screen flex items-center justify-center bg-gradient-to-b from-gray-50 to-gray-100">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="w-[90%] max-w-4xl"
      >
        <Card className="shadow-lg">
          <CardHeader>
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2, duration: 0.5 }}
            >
              <CardTitle className="text-5xl font-bold text-center text-gray-800 mb-2">
                LOCKDIN
              </CardTitle>
              <p className="text-xl text-center text-gray-600">
                Your Personal Goal Achievement Platform
              </p>
            </motion.div>
          </CardHeader>
          <CardContent className="space-y-8">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4, duration: 0.5 }}
              className="grid grid-cols-1 md:grid-cols-3 gap-6 text-center"
            >
              <div className="space-y-2">
                <div className="text-3xl">🎯</div>
                <h3 className="font-semibold">Set Goals</h3>
                <p className="text-gray-600">Create and track your personal goals</p>
              </div>
              <div className="space-y-2">
                <div className="text-3xl">🏆</div>
                <h3 className="font-semibold">Earn Points</h3>
                <p className="text-gray-600">Get rewarded for your progress</p>
              </div>
              <div className="space-y-2">
                <div className="text-3xl">👥</div>
                <h3 className="font-semibold">Join Community</h3>
                <p className="text-gray-600">Connect with like-minded achievers</p>
              </div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.6, duration: 0.5 }}
              className="flex flex-col items-center space-y-4"
            >
              <Button 
                size="lg" 
                className="bg-blue-600 hover:bg-blue-700 text-lg px-8"
                onClick={() => router.push('/login')}
              >
                Get Started
              </Button>
              <p className="text-sm text-gray-500">
                Join thousands of users achieving their goals
              </p>
            </motion.div>
          </CardContent>
        </Card>

        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.8, duration: 0.5 }}
          className="mt-8 text-center text-gray-600"
        >
          <p className="text-sm">
            Already achieving goals? <Button variant="link" className="text-blue-600" onClick={() => router.push('/login')}>Log in here</Button>
          </p>
        </motion.div>
      </motion.div>
    </main>
  )
} 