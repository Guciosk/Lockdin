from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from supabase_client import supabase
import datetime

app = FastAPI()

class User(BaseModel):
    username: str
    phone_number: str
    points: int

class Task(BaseModel):
    user_id: int
    description: str
    due_time: datetime.datetime

class FeedPost(BaseModel):
    user_id: int
    task_id: int
    image_url: str
    status: str
    post_content: str = None  # Optional

@app.post("/users/")
async def create_user(user: User):
    response = supabase.table("users").insert(user.dict()).execute()
    if response.data:
        return {"message": "User registered", "user": response.data}
    raise HTTPException(status_code=400, detail="Error registering user")

@app.post("/tasks/")
async def create_task(task: Task):
    response = supabase.table("tasks").insert(task.dict()).execute()
    if response.data:
        return {"message": "Task created", "task": response.data}
    raise HTTPException(status_code=400, detail="Error creating task")

@app.get("/feed/{user_id}")
async def get_feed(user_id: int):
    response = supabase.table("feed").select("*").eq("user_id", user_id).execute()
    return response.data if response.data else {"message": "No posts found"}
