from datetime import datetime, timedelta
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status, Path, Query
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.schemas import ResponseContact, ContactModel
from src.repository import contacts as repository_contacts
from src.services.auth import auth_service
from src.database.models import User

router = APIRouter(prefix='/contacts', tags=['contacts'])



@router.get("/", response_model=List[ResponseContact], name="Get all contacts form database (10 requests per minute)", dependencies=[Depends(RateLimiter(times=10, seconds=60))],)
async def get_contacts(limit: int = Query(10, le=1000), offset: int = 0, db: Session = Depends(get_db), current_user: User = Depends(auth_service.get_current_user),):
    contacts = await repository_contacts.get_all_contacts(limit, offset, current_user, db)
    return contacts


@router.post("/", response_model=ResponseContact, status_code=status.HTTP_201_CREATED, name="Create a new contact",)
async def create_contact(body: ContactModel, db: Session = Depends(get_db), current_user: User = Depends(auth_service.get_current_user),):
    contact = await repository_contacts.create_contact(body, current_user, db)
    return contact


@router.get("/id/{contact_id}", response_model=ResponseContact, name="Find contact by ID")
async def get_contact_by_id(contact_id: int = Path(ge=1), db: Session = Depends(get_db), current_user: User = Depends(auth_service.get_current_user),):
    contact = await repository_contacts.get_contact_by_id(contact_id, current_user, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Contact with ID={contact_id} not found",)
    return contact


@router.get("/name/{contact_name}", response_model=list[ResponseContact], name="Find contact by name",)
async def get_contact_by_name(contact_name: str, limit: int = Query(10, le=1000), offset: int = 0, db: Session = Depends(get_db), current_user: User = Depends(auth_service.get_current_user),):
    contacts = await repository_contacts.get_contact_by_name(contact_name, limit, offset, current_user, db)
    if contacts is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Contacts with name {contact_name} not found",)
    return contacts


@router.get("/surname/{contact_surname}", response_model=list[ResponseContact], name="Find contact by surname",)
async def get_contact_by_surname(contact_surname: str, limit: int = Query(10, le=1000), offset: int = 0, db: Session = Depends(get_db), current_user: User = Depends(auth_service.get_current_user),):
    contacts = await repository_contacts.get_contact_by_surname(contact_surname, limit, offset, db)
    if contacts is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Contacts with surname {contact_surname} not found",)
    return contacts


@router.get("/email/{contact_email}", response_model=ResponseContact, name="Find contact by email",)
async def get_contact_by_email(contact_email: str, db: Session = Depends(get_db), current_user: User = Depends(auth_service.get_current_user),):
    contact = await repository_contacts.get_contact_by_email(contact_email, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Contact with email {contact_email} not found",)
    return contact


@router.get("/birthdays_in_next_week", response_model=list[ResponseContact])
async def get_birthdays_in_next_week(limit: int = Query(10, le=1000), offset: int = 0, db: Session = Depends(get_db), current_user: User = Depends(auth_service.get_current_user),):
    contacts = await repository_contacts.get_birthdays_in_next_week(limit, offset, current_user, db)
    if not contacts:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contacts with birthdays for the next week not found",)
    return contacts


@router.put("/{contact_id}", response_model=ResponseContact)
async def update_contact(body: ContactModel, contact_id: int = Path(ge=1), db: Session = Depends(get_db), current_user: User = Depends(auth_service.get_current_user),):
    contact = await repository_contacts.update_contact(body, contact_id, db)
    if get_contact_by_id is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Contact with ID {contact_id} not found",)
    return contact


@router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT, name="Delete contact form database by ID",)
async def remove_contact(contact_id: int = Path(ge=1), db: Session = Depends(get_db), current_user: User = Depends(auth_service.get_current_user),):
    contact = await repository_contacts.remove_contact(contact_id, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Contact with ID={contact_id} not found",)
    return contact
