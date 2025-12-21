from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .. import models, database, schemas

router = APIRouter()

@router.get("/notes/", response_model=List[schemas.Note])
def list_notes(db: Session = Depends(database.get_db)):
    return db.query(models.Note).all()

@router.post("/notes/", response_model=schemas.Note)
def create_note(note: schemas.NoteCreate, db: Session = Depends(database.get_db)):
    db_note = models.Note(**note.dict())
    db.add(db_note)
    db.commit()
    db.refresh(db_note)
    return db_note

@router.get("/notes/{note_id}", response_model=schemas.Note)
def get_note(note_id: int, db: Session = Depends(database.get_db)):
    note = db.query(models.Note).filter(models.Note.id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Nota não encontrada")
    return note

@router.delete("/notes/{note_id}", response_model=schemas.Note)
def delete_note(note_id: int, db: Session = Depends(database.get_db)):
    note = db.query(models.Note).filter(models.Note.id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Nota não encontrada")
    db.delete(note)
    db.commit()
    return note
