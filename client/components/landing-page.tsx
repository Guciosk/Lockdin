"use client"

import { motion } from "framer-motion"
import { useRouter } from "next/navigation"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Target, Trophy, Users, Heart, Brain, Zap } from "lucide-react"

export const LandingPage = () => {
  const router = useRouter()

  // Animation variants for staggered children
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1,
        delayChildren: 0.3
      }
    }
  }

  const itemVariants = {
    hidden: { y: 20, opacity: 0 },
    visible: { y: 0, opacity: 1 }
  }

  return (
    <main className="min-h-screen flex items-center justify-center bg-[#f8fafc]">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="w-[90%] max-w-4xl"
      >
        <Card className="shadow-xl border-[#60a5fa] overflow-hidden">
          <CardHeader className="bg-[#60a5fa] text-white pb-8">
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2, duration: 0.5 }}
            >
              <motion.div
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ delay: 0.3, type: "spring", stiffness: 200 }}
                className="flex justify-center mb-4"
              >
                <Heart className="h-16 w-16 text-white" />
              </motion.div>
              <CardTitle className="text-5xl font-bold text-center text-white mb-2">
                LOCKDIN
              </CardTitle>
              <p className="text-xl text-center text-white/90">
                Your Health Accountability Partner
              </p>
            </motion.div>
          </CardHeader>
          <CardContent className="space-y-8 pt-8">
            <motion.div
              variants={containerVariants}
              initial="hidden"
              animate="visible"
              className="grid grid-cols-1 md:grid-cols-3 gap-6 text-center"
            >
              <motion.div variants={itemVariants} className="space-y-3 p-4 rounded-lg bg-white shadow-sm hover:shadow-md transition-shadow duration-300">
                <div className="text-3xl flex justify-center">
                  <Target className="h-10 w-10 text-[#60a5fa]" />
                </div>
                <h3 className="font-semibold text-[#334155]">Set Goals</h3>
                <p className="text-gray-600">Create and track your personal health goals</p>
              </motion.div>
              <motion.div variants={itemVariants} className="space-y-3 p-4 rounded-lg bg-white shadow-sm hover:shadow-md transition-shadow duration-300">
                <div className="text-3xl flex justify-center">
                  <Trophy className="h-10 w-10 text-[#f87171]" />
                </div>
                <h3 className="font-semibold text-[#334155]">Earn Points</h3>
                <p className="text-gray-600">Get rewarded for your health progress</p>
              </motion.div>
              <motion.div variants={itemVariants} className="space-y-3 p-4 rounded-lg bg-white shadow-sm hover:shadow-md transition-shadow duration-300">
                <div className="text-3xl flex justify-center">
                  <Users className="h-10 w-10 text-[#60a5fa]" />
                </div>
                <h3 className="font-semibold text-[#334155]">Join Community</h3>
                <p className="text-gray-600">Connect with health-focused achievers</p>
              </motion.div>
            </motion.div>

            <motion.div
              className="space-y-6 bg-white p-6 rounded-lg shadow-sm"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.7, duration: 0.5 }}
            >
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="flex items-start gap-3">
                  <div className="mt-1">
                    <Brain className="h-6 w-6 text-[#60a5fa]" />
                  </div>
                  <div>
                    <h4 className="font-semibold text-[#334155]">Improve Focus</h4>
                    <p className="text-sm text-gray-600">Our app helps students with ADHD stay on track with their studies</p>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <div className="mt-1">
                    <Zap className="h-6 w-6 text-[#f87171]" />
                  </div>
                  <div>
                    <h4 className="font-semibold text-[#334155]">Boost Productivity</h4>
                    <p className="text-sm text-gray-600">Complete tasks on time and build healthy study habits</p>
                  </div>
                </div>
              </div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.8, duration: 0.5 }}
              className="flex flex-col items-center space-y-4"
            >
              <Button 
                size="lg" 
                className="bg-[#f87171] hover:bg-[#ef4444] text-white font-medium text-lg px-8 py-6 rounded-lg shadow-md hover:shadow-lg transition-all duration-200"
                onClick={() => router.push('/login')}
              >
                Get Started
              </Button>
              <p className="text-sm text-gray-500">
                Join thousands of students improving their focus and health
              </p>
            </motion.div>
          </CardContent>
        </Card>

        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1, duration: 0.5 }}
          className="mt-8 text-center text-gray-600"
        >
          <p className="text-sm">
            Already achieving goals? <Button variant="link" className="text-[#60a5fa] hover:text-[#3b82f6]" onClick={() => router.push('/login')}>Log in here</Button>
          </p>
        </motion.div>
      </motion.div>
    </main>
  )
} 