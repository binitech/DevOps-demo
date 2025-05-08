import pytest
from fastapi.testclient import TestClient
from app.main import app, tasks

client = TestClient(app)

@pytest.fixture(autouse=True)
def clear_tasks():
    # Clear tasks before each test
    tasks.clear()
    yield

def test_get_empty_tasks():
    response = client.get("/api/tasks")
    assert response.status_code == 200
    assert response.json() == []

def test_create_task():
    task_data = {"title": "Test Task", "description": "This is a test task"}
    response = client.post("/api/tasks", json=task_data)
    assert response.status_code == 201
    
    data = response.json()
    assert "id" in data
    assert data["title"] == task_data["title"]
    assert data["description"] == task_data["description"]
    assert data["completed"] is False

def test_get_tasks_after_create():
    # Create a task first
    task_data = {"title": "Test Task", "description": "This is a test task"}
    create_response = client.post("/api/tasks", json=task_data)
    
    # Then get all tasks
    response = client.get("/api/tasks")
    assert response.status_code == 200
    assert len(response.json()) == 1
    
    # Verify task data
    task = response.json()[0]
    assert task["title"] == task_data["title"]
    assert task["description"] == task_data["description"]

def test_get_task_by_id():
    # Create a task
    task_data = {"title": "Test Task", "description": "This is a test task"}
    create_response = client.post("/api/tasks", json=task_data)
    task_id = create_response.json()["id"]
    
    # Get the task by ID
    response = client.get(f"/api/tasks/{task_id}")
    assert response.status_code == 200
    
    # Verify task data
    data = response.json()
    assert data["id"] == task_id
    assert data["title"] == task_data["title"]
    assert data["description"] == task_data["description"]

def test_get_nonexistent_task():
    response = client.get("/api/tasks/nonexistent-id")
    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"

def test_delete_task():
    # Create a task
    task_data = {"title": "Task to Delete", "description": "This task will be deleted"}
    create_response = client.post("/api/tasks", json=task_data)
    task_id = create_response.json()["id"]
    
    # Delete the task
    delete_response = client.delete(f"/api/tasks/{task_id}")
    assert delete_response.status_code == 204
    
    # Verify task is deleted
    get_response = client.get(f"/api/tasks/{task_id}")
    assert get_response.status_code == 404

def test_delete_nonexistent_task():
    response = client.delete("/api/tasks/nonexistent-id")
    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"

def test_get_index_page():
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"] 