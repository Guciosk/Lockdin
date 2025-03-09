/**
 * Dummy Data for LOCKDIN Application
 * 
 * This file contains mock data used for development and testing purposes.
 * In a production environment, this data would be fetched from the backend API.
 */

/**
 * Goal interface representing a user's goal or task
 */
export interface Goal {
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

/**
 * UserGoal interface representing a personal goal with urgency level
 */
export interface UserGoal {
    id: number;
    title: string;
    description: string;
    dueDate: string;
    urgency: 'high' | 'medium' | 'low';
    status: string;
    isComplete: boolean;
    category: string;
    createdAt: string;
}

/**
 * UserStats interface for tracking user performance and points
 */
export interface UserStats {
    goals: Goal[];
    userImage: string;
    points: number;
}

/**
 * Mock user for testing authentication
 */
export const dummyUser = {
    username: "admin",
    email: "admin@lockdin.com",
    fullName: "Admin User",
    image: "https://api.dicebear.com/7.x/avataaars/svg?seed=AdminUser",
    points: 0,
    discord_user_id: null
};

/**
 * Mock credentials for testing login functionality
 */
export const dummyCredentials = [
    {
        username: "admin",
        password: "admin"
    },
    {
        username: "dabi_fe",
        password: "1234",
        points: 50,
        discord_user_id: "1199341644810559541"
    }
];

/**
 * Helper function to determine urgency based on due date
 * @param dueDate The due date string in YYYY-MM-DD format
 * @returns Urgency level: 'high' (within 2 days), 'medium' (within 7 days), or 'low' (beyond 7 days)
 */
export const calculateUrgency = (dueDate: string): 'high' | 'medium' | 'low' => {
    const today = new Date();
    const due = new Date(dueDate);
    const diffTime = due.getTime() - today.getTime();
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    if (diffDays <= 2) return 'high';
    if (diffDays <= 7) return 'medium';
    return 'low';
};

/**
 * Mock personal goals for the current user
 * Urgency is calculated based on due date proximity:
 * - High: Due within 2 days
 * - Medium: Due within 7 days
 * - Low: Due beyond 7 days
 */
export const dummyUserGoals: UserGoal[] = [
    {
        id: 1,
        title: "Complete Math Assignment",
        description: "Finish calculus problems 1-20 for Professor Smith's class",
        dueDate: (() => {
            const tomorrow = new Date();
            tomorrow.setDate(tomorrow.getDate() + 1);
            return tomorrow.toISOString().split('T')[0];
        })(),
        urgency: 'high',
        status: "In Progress",
        isComplete: false,
        category: "Academic",
        createdAt: "2024-03-08"
    },
    {
        id: 2,
        title: "Study for Biology Exam",
        description: "Review chapters 5-8 and lab notes",
        dueDate: (() => {
            const twoDaysLater = new Date();
            twoDaysLater.setDate(twoDaysLater.getDate() + 2);
            return twoDaysLater.toISOString().split('T')[0];
        })(),
        urgency: 'high',
        status: "Not Started",
        isComplete: false,
        category: "Academic",
        createdAt: "2024-03-07"
    },
    {
        id: 3,
        title: "Complete Programming Project",
        description: "Finish the React app for web development class",
        dueDate: (() => {
            const fiveDaysLater = new Date();
            fiveDaysLater.setDate(fiveDaysLater.getDate() + 5);
            return fiveDaysLater.toISOString().split('T')[0];
        })(),
        urgency: 'medium',
        status: "In Progress",
        isComplete: false,
        category: "Academic",
        createdAt: "2024-03-05"
    },
    {
        id: 4,
        title: "Read Research Paper",
        description: "Read and take notes on the assigned research paper for Psychology",
        dueDate: (() => {
            const sixDaysLater = new Date();
            sixDaysLater.setDate(sixDaysLater.getDate() + 6);
            return sixDaysLater.toISOString().split('T')[0];
        })(),
        urgency: 'medium',
        status: "Not Started",
        isComplete: false,
        category: "Academic",
        createdAt: "2024-03-06"
    },
    {
        id: 5,
        title: "Prepare Presentation",
        description: "Create slides for the group presentation in Business class",
        dueDate: (() => {
            const tenDaysLater = new Date();
            tenDaysLater.setDate(tenDaysLater.getDate() + 10);
            return tenDaysLater.toISOString().split('T')[0];
        })(),
        urgency: 'low',
        status: "Not Started",
        isComplete: false,
        category: "Academic",
        createdAt: "2024-03-04"
    },
    {
        id: 6,
        title: "Gym Workout",
        description: "Complete 30 minutes of cardio and strength training",
        dueDate: (() => {
            const today = new Date();
            return today.toISOString().split('T')[0];
        })(),
        urgency: 'high',
        status: "Not Started",
        isComplete: false,
        category: "Health",
        createdAt: "2024-03-08"
    },
    {
        id: 7,
        title: "Submit Research Proposal",
        description: "Finalize and submit research proposal for senior project",
        dueDate: (() => {
            const twoWeeksLater = new Date();
            twoWeeksLater.setDate(twoWeeksLater.getDate() + 14);
            return twoWeeksLater.toISOString().split('T')[0];
        })(),
        urgency: 'low',
        status: "In Progress",
        isComplete: false,
        category: "Academic",
        createdAt: "2024-03-01"
    }
];

/**
 * Mock news feed data representing community activity
 */
export const dummyNewsFeed: Goal[] = [
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

/**
 * Helper function to calculate points based on goal completion status
 * @param goals Array of user goals
 * @returns Total points earned
 */
export const calculatePoints = (goals: Goal[]): number => {
    return goals.reduce((total: number, goal: Goal) => {
        if (goal.status === "Complete") return total + 50;
        return total + 25; // Partial points for in-progress goals
    }, 0);
};

/**
 * Generate user statistics based on goals
 * @param goals Array of goals to process
 * @returns Object with username keys and UserStats values
 */
export const generateUserStats = (goals: Goal[]): Record<string, UserStats> => {
    return goals.reduce<Record<string, UserStats>>((acc, goal) => {
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
}; 