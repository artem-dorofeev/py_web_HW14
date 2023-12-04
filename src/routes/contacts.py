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
    """
    The get_contacts function returns a list of contacts.

    The limit and offset parameters are used to paginate the results.
        
    
    :param limit: int: Limit the amount of contacts returned
    :param le: Limit the maximum number of contacts that can be returned
    :param offset: int: Specify the offset of the first item to be returned
    :param db: Session: Get a database session
    :param current_user: User: Get the current user from the database
    :return: A list of contacts
    :doc-author: Trelent
    """
    contacts = await repository_contacts.get_all_contacts(limit, offset, current_user, db)
    return contacts


@router.post("/", response_model=ResponseContact, status_code=status.HTTP_201_CREATED, name="Create a new contact",)
async def create_contact(body: ContactModel, db: Session = Depends(get_db), current_user: User = Depends(auth_service.get_current_user),):
    """
    The create_contact function creates a new contact in the database.

    The function takes in a ContactModel object, which is defined as follows:
    class ContactModel(BaseModel):
    name: str = Field(..., title=&quot;The name of the contact&quot;, max_length=100)
    email: EmailStr = Field(..., title=&quot;The email address of the contact&quot;)
    
    :param body: ContactModel: Get the data from the request body
    :param db: Session: Pass the database session to the repository layer
    :param current_user: User: Get the user id of the current user
    :return: A contactmodel object
    :doc-author: Trelent
    """
    contact = await repository_contacts.create_contact(body, current_user, db)
    return contact


@router.get("/id/{contact_id}", response_model=ResponseContact, name="Find contact by ID")
async def get_contact_by_id(contact_id: int = Path(ge=1), db: Session = Depends(get_db), current_user: User = Depends(auth_service.get_current_user),):
    """
    The get_contact_by_id function returns a contact by its ID.
    
    :param contact_id: int: Get the id of the contact that you want to retrieve
    :param db: Session: Pass the database session to the repository layer
    :param current_user: User: Get the current user from the database
    :return: A contact object
    :doc-author: Trelent
    """
    contact = await repository_contacts.get_contact_by_id(contact_id, current_user, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Contact with ID={contact_id} not found",)
    return contact


@router.get("/name/{contact_name}", response_model=list[ResponseContact], name="Find contact by name",)
async def get_contact_by_name(contact_name: str, limit: int = Query(10, le=1000), offset: int = 0, db: Session = Depends(get_db), current_user: User = Depends(auth_service.get_current_user),):
    """
    The get_contact_by_name function is used to search for a contact by name.

    The function takes in the following parameters:
    - contact_name: str, the name of the contact you are searching for.
    - limit: int, how many contacts you want returned (defaults to 10).
    - offset: int, where in your list of contacts do you want to start returning from (defaults to 0).
    The function returns a list of Contact objects that match your query.
    
    :param contact_name: str: Pass the name of the contact to be searched
    :param limit: int: Limit the number of contacts returned
    :param le: Limit the number of results returned
    :param offset: int: Skip the first n records
    :param db: Session: Get the database session object
    :param current_user: User: Get the user_id of the current logged in user
    :return: The function returns a list of Contact objects that match your query
    :doc-author: Trelent
    """
    contacts = await repository_contacts.get_contact_by_name(contact_name, limit, offset, current_user, db)
    if contacts is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Contacts with name {contact_name} not found",)
    return contacts


@router.get("/surname/{contact_surname}", response_model=list[ResponseContact], name="Find contact by surname",)
async def get_contact_by_surname(contact_surname: str, limit: int = Query(10, le=1000), offset: int = 0, db: Session = Depends(get_db), current_user: User = Depends(auth_service.get_current_user),):
    """
    The get_contact_by_surname function is used to retrieve a list of contacts with the same surname.

    The function takes in a contact_surname, limit, offset and db as parameters.
    It returns an HTTP response containing the list of contacts with that surname.
    
    :param contact_surname: str: Get the surname of a contact
    :param limit: int: Limit the number of results returned
    :param le: Limit the number of results returned
    :param offset: int: Specify the number of records to skip before starting to return rows
    :param db: Session: Get the database session
    :param current_user: User: Get the current user from the database
    :return: A list of contacts
    :doc-author: Trelent
    """
    contacts = await repository_contacts.get_contact_by_surname(contact_surname, limit, offset, db)
    if contacts is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Contacts with surname {contact_surname} not found",)
    return contacts


@router.get("/email/{contact_email}", response_model=ResponseContact, name="Find contact by email",)
async def get_contact_by_email(contact_email: str, db: Session = Depends(get_db), current_user: User = Depends(auth_service.get_current_user),):
    """
    The get_contact_by_email function is used to retrieve a contact by email.

    The function will return the contact if it exists, otherwise it will raise an HTTPException with status code 404 and detail message "Contact with email {contact_email} not found";.
    
    
    :param contact_email: str: Pass the email of the contact we want to retrieve
    :param db: Session: Pass the database session to the repository layer
    :param current_user: User: Get the current user from the database
    :return: A contact object
    :doc-author: Trelent
    """
    contact = await repository_contacts.get_contact_by_email(contact_email, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Contact with email {contact_email} not found",)
    return contact


@router.get("/birthdays_in_next_week", response_model=list[ResponseContact])
async def get_birthdays_in_next_week(limit: int = Query(10, le=1000), offset: int = 0, db: Session = Depends(get_db), current_user: User = Depends(auth_service.get_current_user),):
    """
    The get_contacts_with_birthdays_in_next_7_days function returns a list of contacts with birthdays in the next 7 days.

    The limit and offset parameters are used to paginate the results.
    
    
    :param limit: int: Limit the number of contacts returned
    :param le: Limit the maximum number of contacts returned
    :param offset: int: Specify the number of records to skip before returning the results
    :param db: Session: Pass the database session to the repository layer
    :param current_user: User: Get the current user from the auth_service
    :return: A list of contacts with birthdays in the next 7 days
    :doc-author: Trelent
    """
    contacts = await repository_contacts.get_birthdays_in_next_week(limit, offset, current_user, db)
    if not contacts:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contacts with birthdays for the next week not found",)
    return contacts


@router.put("/{contact_id}", response_model=ResponseContact)
async def update_contact(body: ContactModel, contact_id: int = Path(ge=1), db: Session = Depends(get_db), current_user: User = Depends(auth_service.get_current_user),):
    """
    The update_contact function updates a contact in the database.

    The function takes an ID and a body as input, and returns the updated contact.
    If no contact is found with that ID, it raises an HTTPException.
    
    :param body: ContactModel: Pass the contact details to be updated
    :param contact_id: int: Specify the id of the contact to be updated
    :param db: Session: Pass the database session to the function
    :param current_user: User: Get the current user from the database
    :return: The contact object
    :doc-author: Trelent
    """
    contact = await repository_contacts.update_contact(body, contact_id, db)
    if get_contact_by_id is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Contact with ID {contact_id} not found",)
    return contact


@router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT, name="Delete contact form database by ID",)
async def remove_contact(contact_id: int = Path(ge=1), db: Session = Depends(get_db), current_user: User = Depends(auth_service.get_current_user),):
    """
    The remove_contact function removes a contact from the database.
    
    :param contact_id: int: Specify the id of the contact to be removed
    :param db: Session: Pass the database connection to the function
    :param current_user: User: Get the current user
    :return: A contact object
    :doc-author: Trelent
    """
    contact = await repository_contacts.remove_contact(contact_id, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Contact with ID={contact_id} not found",)
    return contact
