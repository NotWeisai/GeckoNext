from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Task, MediaFile, Segment, User, Project, Comment
from ..auth import get_current_user
from pydantic import BaseModel
from typing import List, Optional
import shutil
import os

router = APIRouter()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

class TaskCreate(BaseModel):
    project_id: int
    filename: str

class SegmentCreate(BaseModel):
    start_time: float
    end_time: float
    text: str
    speaker_id: Optional[int] = None

@router.post("/tasks")
def create_task(
    filename: str = "unknown.mp3",
    db: Session = Depends(get_db), 
    username: str = Depends(get_current_user)
):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Автоматически создаём проект, если его нет
    project = db.query(Project).filter(Project.id == 1).first()
    if not project:
        project = Project(
            name="Default Project",
            description="Создан автоматически для теста",
            owner_id=user.id
        )
        db.add(project)
        db.commit()
        db.refresh(project)
    
    new_task = Task(
        project_id=project.id,
        assignee_id=user.id,
        status="В работе"
    )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task

@router.get("/tasks")
def get_my_tasks(db: Session = Depends(get_db), username: str = Depends(get_current_user)):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.role == "verifier":
        # Верификатор видит задачи на проверке и на доработке
        tasks = db.query(Task).filter(
            Task.status.in_(["На проверке", "На доработке"])
        ).all()
    else:
        # Разметчик видит свои задачи
        tasks = db.query(Task).filter(Task.assignee_id == user.id).all()
    
    return tasks

@router.post("/upload-audio")
async def upload_audio(file: UploadFile = File(...), db: Session = Depends(get_db), username: str = Depends(get_current_user)):
    file_path = f"{UPLOAD_DIR}/{file.filename}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    media = MediaFile(audio_path=file_path, format=file.filename.split('.')[-1])
    db.add(media)
    db.commit()
    db.refresh(media)
    return {"id": media.id, "filename": file.filename, "path": file_path}

@router.get("/tasks/{task_id}")
def get_task(task_id: int, db: Session = Depends(get_db), username: str = Depends(get_current_user)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

class SegmentUpdate(BaseModel):
    start: float
    end: float
    text: str = ""
    speaker_id: Optional[int] = None

class SegmentsUpdate(BaseModel):
    segments: List[SegmentUpdate]

@router.put("/tasks/{task_id}/segments")
def save_segments(
    task_id: int,
    data: SegmentsUpdate,          # ← теперь используем Pydantic модель
    db: Session = Depends(get_db),
    username: str = Depends(get_current_user)
):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Удаляем старые сегменты
    db.query(Segment).filter(Segment.task_id == task_id).delete()
    
    # Добавляем новые
    for seg in data.segments:
        new_seg = Segment(
            task_id=task_id,
            start_time=seg.start,
            end_time=seg.end,
            text=seg.text,
            speaker_id=seg.speaker_id
        )
        db.add(new_seg)
    
    db.commit()
    return {"status": "saved", "segments_count": len(data.segments)}

@router.get("/tasks/{task_id}/segments")
def get_segments(task_id: int, db: Session = Depends(get_db), username: str = Depends(get_current_user)):
    segments = db.query(Segment).filter(Segment.task_id == task_id).order_by(Segment.start_time).all()
    
    return [
        {
            "id": s.id,
            "start": s.start_time,
            "end": s.end_time,
            "text": s.text or "",
            "speaker": s.speaker_id
        }
        for s in segments
    ]

@router.delete("/tasks/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db), username: str = Depends(get_current_user)):
    user = db.query(User).filter(User.username == username).first()
    task = db.query(Task).filter(Task.id == task_id).first()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Разрешаем удаление только своих задач или админу/супервайзеру (для MVP упрощаем)
    if task.assignee_id != user.id and user.role not in ["admin", "supervisor"]:
        raise HTTPException(status_code=403, detail="Нет прав на удаление этой задачи")
    
    # Удаляем связанные данные
    db.query(Segment).filter(Segment.task_id == task_id).delete()
    db.query(Comment).filter(Comment.task_id == task_id).delete()
    
    db.delete(task)
    db.commit()
    
    return {"status": "deleted", "task_id": task_id}

class TaskStatusUpdate(BaseModel):
    status: str

@router.put("/tasks/{task_id}/status")
def update_task_status(
    task_id: int,
    update: TaskStatusUpdate,
    db: Session = Depends(get_db),
    username: str = Depends(get_current_user)
):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task.status = update.status
    db.commit()
    db.refresh(task)
    return task

class CommentCreate(BaseModel):
    text: str

@router.post("/tasks/{task_id}/comments")
def create_comment(
    task_id: int,
    comment: CommentCreate,
    db: Session = Depends(get_db),
    username: str = Depends(get_current_user)
):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    new_comment = Comment(
        task_id=task_id,
        author_id=user.id,
        text=comment.text,
        status="open"
    )
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)
    return {"id": new_comment.id, "text": new_comment.text, "created_at": new_comment.created_at}

@router.get("/tasks/{task_id}/comments")
def get_comments(
    task_id: int,
    db: Session = Depends(get_db),
    username: str = Depends(get_current_user)
):
    # Делаем join, чтобы получить username автора
    comments = db.query(Comment, User).join(User, Comment.author_id == User.id)\
        .filter(Comment.task_id == task_id)\
        .order_by(Comment.created_at.desc()).all()

    return [
        {
            "id": c[0].id,
            "text": c[0].text,
            "author": c[1].username,          # теперь берём username
            "created_at": c[0].created_at
        }
        for c in comments
    ]