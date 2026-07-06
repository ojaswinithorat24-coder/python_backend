from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

import models
from database import SessionLocal, engine

# Create tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# CORS Configuration (Allow React Frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Home Route
@app.get("/")
def read_root():
    return {"message": "Hello, Intern!"}

# Health Check
@app.get("/health")
def health_check():
    return {"status": "healthy"}

# CREATE TODO
@app.post("/todos")
def create_todo(title: str, db: Session = Depends(get_db)):
    todo = models.Todo(title=title)
    db.add(todo)
    db.commit()
    db.refresh(todo)
    return todo

# READ ALL TODOS
@app.get("/todos")
def get_todos(db: Session = Depends(get_db)):
    return db.query(models.Todo).all()

# READ ONE TODO
@app.get("/todos/{todo_id}")
def get_todo(todo_id: int, db: Session = Depends(get_db)):
    todo = db.query(models.Todo).filter(models.Todo.id == todo_id).first()

    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")

    return todo

# UPDATE TODO
@app.put("/todos/{todo_id}")
def update_todo(todo_id: int, title: str, completed: bool, db: Session = Depends(get_db)):
    todo = db.query(models.Todo).filter(models.Todo.id == todo_id).first()

    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")

    todo.title = title
    todo.completed = completed

    db.commit()
    db.refresh(todo)

    return todo

# DELETE TODO
@app.delete("/todos/{todo_id}")
def delete_todo(todo_id: int, db: Session = Depends(get_db)):
    todo = db.query(models.Todo).filter(models.Todo.id == todo_id).first()

    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")

    db.delete(todo)
    db.commit()

    return {"message": "Todo deleted successfully"}