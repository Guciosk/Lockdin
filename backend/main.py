from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from supabase_client import supabase

app = FastAPI()

class User(BaseModel):
    username: str
    phone_number: str
    points: int

class Task(BaseModel):
    user_id: int
    description: str
    due_time: str

class FeedPost(BaseModel):
    user_id: int
    task_id: int
    image_url: str
    status: str
    post_content: str = None

@app.post("/users/")
async def create_user(user: User):
    response = supabase.table("users").insert(user.model_dump()).execute()
    if response.data:
        return {"message": "User registered", "user": response.data}
    raise HTTPException(status_code=400, detail="Error registering user")

@app.post("/tasks/")
async def create_task(task: Task):
    response = supabase.table("tasks").insert(task.model_dump()).execute()
    if response.data:
        return {"message": "Task created", "task": response.data}
    raise HTTPException(status_code=400, detail="Error creating task")

@app.get("/tasks/{task_id}")
async def get_task(task_id: int):
    response = supabase.table("tasks").select("*").eq("task_id", task_id).single().execute()
    if not response.data:
        raise HTTPException(status_code=404, detail="Task not found")
    task = Task(**response.data)
    return task

@app.get("/users/{user_id}")
async def get_user(user_id: int):
    response = supabase.table("users").select("*").eq("user_id", user_id).single().execute()
    if not response.data:
        raise HTTPException(status_code=404, detail="User not found")
    user = User(**response.data)
    return user

@app.post("/feed/")
async def post_to_feed(feed_post: FeedPost):
    response = supabase.table("feed").insert(feed_post.model_dump()).execute()
    if response.data:
        return {"message": "Feed post created", "feed_post": response.data}
    raise HTTPException(status_code=400, detail="Error creating feed post")

# Feed of a specific user
@app.get("/feed/{user_id}")
async def get_user_feed(user_id: int):
    response = supabase.table("feed").select("*").eq("user_id", user_id).execute()
    return response.data if response.data else {"message": "No posts found"}

# For universal feed
@app.get("/feed/")
async def get_all_feed_posts():
    response = supabase.table("feed").select("*").execute()
    if not response.data:
        raise HTTPException(status_code=404, detail="No feed posts found")
    feed_posts = [FeedPost(**post) for post in response.data]
    return feed_posts
