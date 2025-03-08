# LOCKDIN Client

This is the frontend application for LOCKDIN, a focus and accountability app designed to help students improve their productivity and achieve their academic goals.

## Project Structure

```
client/
├── app/                # Next.js app directory with routes
├── components/         # React components
│   ├── ui/             # UI components (buttons, cards, etc.)
│   ├── dashboard.tsx   # Main dashboard component
│   ├── login.tsx       # Authentication component
│   └── landing-page.tsx # Landing page component
├── lib/                # Utility functions and data
│   ├── dummy-data.ts   # Mock data for development
│   └── utils.ts        # Helper functions
└── utils/              # Additional utilities
    └── supabase/       # Supabase client configuration
```

## Key Components

### Dashboard

The main dashboard component displays:
- User's upcoming goals with urgency indicators
- Goal creation form
- Community feed with other users' goals
- Leaderboard showing top users by points
- User statistics and progress

### Login

Handles user authentication with:
- Username/password login form
- Error handling for invalid credentials
- Redirection to dashboard upon successful login

### Landing Page

The entry point for new users featuring:
- App introduction and value proposition
- Call-to-action buttons
- Feature highlights

## Data Models

### Goal

Represents a goal shared in the community feed:

```typescript
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
```

### UserGoal

Represents a personal goal with urgency level:

```typescript
interface UserGoal {
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
```

### UserStats

Tracks user performance and points:

```typescript
interface UserStats {
    goals: Goal[];
    userImage: string;
    points: number;
}
```

## Urgency Calculation

Goals are assigned urgency levels based on their due dates:

- **High**: Due within 2 days
- **Medium**: Due within 7 days
- **Low**: Due beyond 7 days

```typescript
const calculateUrgency = (dueDate: string): 'high' | 'medium' | 'low' => {
    const today = new Date();
    const due = new Date(dueDate);
    const diffTime = due.getTime() - today.getTime();
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    if (diffDays <= 2) return 'high';
    if (diffDays <= 7) return 'medium';
    return 'low';
};
```

## Points System

Users earn points based on goal completion:
- 50 points for completed goals
- 25 points for in-progress goals

```typescript
const calculatePoints = (goals: Goal[]): number => {
    return goals.reduce((total: number, goal: Goal) => {
        if (goal.status === "Complete") return total + 50;
        return total + 25; // Partial points for in-progress goals
    }, 0);
};
```

## Development

### Prerequisites

- Node.js (v14+)
- npm or yarn

### Setup

1. Install dependencies:
   ```
   npm install
   ```

2. Run the development server:
   ```
   npm run dev
   ```

3. Open [http://localhost:3000](http://localhost:3000) in your browser.

### Mock Data

During development, the application uses mock data from `lib/dummy-data.ts`. In production, this would be replaced with API calls to the backend server.

## Authentication Flow

1. User enters credentials on the login page
2. If valid, user information is stored in localStorage
3. User is redirected to the dashboard
4. Dashboard checks for authentication on load
5. If not authenticated, user is redirected back to login
