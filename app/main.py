from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import List, Optional
import uuid
import os
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Task Manager API")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    completed: bool = False

class Task(TaskBase):
    id: str

# In-memory storage for tasks
tasks = {}

@app.get("/api/tasks", response_model=List[Task])
async def get_tasks():
    return list(tasks.values())

@app.post("/api/tasks", response_model=Task, status_code=201)
async def create_task(task: TaskBase):
    task_id = str(uuid.uuid4())
    new_task = Task(
        id=task_id,
        title=task.title,
        description=task.description,
        completed=task.completed
    )
    tasks[task_id] = new_task
    return new_task

@app.get("/api/tasks/{task_id}", response_model=Task)
async def get_task(task_id: str):
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    return tasks[task_id]

@app.delete("/api/tasks/{task_id}", status_code=204)
async def delete_task(task_id: str):
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    del tasks[task_id]
    return None

@app.put("/api/tasks/{task_id}", response_model=Task)
async def update_task(task_id: str, task_update: TaskBase):
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Update task properties while keeping the same ID
    existing_task = tasks[task_id]
    updated_task = Task(
        id=task_id,
        title=task_update.title,
        description=task_update.description,
        completed=task_update.completed
    )
    tasks[task_id] = updated_task
    return updated_task

# Setup templates
templates = Jinja2Templates(directory="app/templates")

@app.get("/", response_class=HTMLResponse)
async def get_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Mount static files
if os.path.exists("app/static"):
    app.mount("/static", StaticFiles(directory="app/static"), name="static") 