import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"

export const LandingPage = () => {
  return (
    <main className="min-h-screen flex items-center justify-center bg-gradient-to-b from-gray-50 to-gray-100">
      <Card className="w-[90%] max-w-2xl shadow-lg">
        <CardHeader>
          <CardTitle className="text-4xl font-bold text-center text-gray-800">
            Under Construction
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          <p className="text-center text-gray-600 text-lg">
            We're working hard to bring you something amazing. Stay tuned!
          </p>
          <div className="flex justify-center">
            <Button size="lg" className="bg-blue-600 hover:bg-blue-700">
              Visit Soon
            </Button>
          </div>
        </CardContent>
      </Card>
    </main>
  )
} 