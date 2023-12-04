from datetime import date, timedelta
from sqlalchemy import and_, extract, or_, between
from sqlalchemy.orm import Session

from src.database.models import Contact, User
from src.schemas import ContactModel


async def get_all_contacts(limit: int, offset: int, current_user: User, db: Session):
    """
    The get_all_contacts function returns a list of contacts for the current user.
        
    
    :param limit: int: Limit the number of contacts returned
    :param offset: int: Specify the number of records to skip
    :param current_user: User: Get the current user from the database
    :param db: Session: Access the database
    :return: A list of contacts, which is then passed to the response_model
    :doc-author: Trelent
    """
    contacts = db.query(Contact).filter_by(user_id=current_user.id)
    contacts = contacts.limit(limit).offset(offset).all()
    return contacts

async def get_contact_by_id(contact_id: int, db: Session):
    """
    The get_contact_by_id function returns a contact by its id.
        Args:
            contact_id (int): The id of the contact to be returned.
            current_user (User): The user who is making the request for a specific contact.
            db (Session): A database session object that allows us to query and manipulate data in our database.
        Returns: 
            Contact: A single Contact object from our database, or None if no such Contact exists.
    
    :param contact_id: int: Get the contact from the database
    :param current_user: User: Get the user id of the current user
    :param db: Session: Pass the database session to the function
    :return: A contact object
    :doc-author: Trelent
    """
    contact = db.query(Contact).filter_by(id=contact_id).first()
    return contact


async def get_contact_by_name(contact_name: str, limit: int, offset: int, db: Session):
    """
    The get_contact_by_name function returns a list of contacts that match the contact_name parameter.
    The limit and offset parameters are used to paginate the results. The current_user parameter is used to ensure that only
    contacts belonging to the user making this request are returned.
    
    :param contact_name: str: Filter the contacts by name
    :param limit: int: Limit the number of results returned
    :param offset: int: Skip the first n records
    :param current_user: User: Ensure that the user is only able to access their own contacts
    :param db: Session: Access the database
    :return: A list of contacts that match the contact_name argument
    :doc-author: Trelent
    """
    contacts = db.query(Contact).filter_by(name=contact_name)
    contacts = contacts.limit(limit).offset(offset)
    return contacts


async def get_contact_by_surname(contact_surname: str, limit: int, offset: int,db: Session):
    """
    The get_contact_by_surname function returns a list of contacts with the given surname.

    :param contact_surname: str: The surname of the contact to be returned.
    :param limit: int: The maximum number of contacts to return.
    :param offset: int: The number of contacts to skip before returning results.
    :param current_user: User: The current user object.
    :param db: Session: The database session object.
    :return: A list containing all matching contacts, or an empty list if no matches are found.
    :doc-author: Trelent
    """
    contacts = db.query(Contact).filter_by(surname=contact_surname)
    contacts = contacts.limit(limit).offset(offset)
    return contacts


async def get_contact_by_email(contact_email: str, db: Session):
    """
    The get_contact_by_email function returns a contact object from the database based on the email address provided.
    
    :param contact_email: str: Get the email of the contact
    :param current_user: User: Get the current user's id from the database
    :param db: Session: Pass the database session to the function
    :return: A contact object
    :doc-author: Trelent
    """
    contact = db.query(Contact).filter_by(email=contact_email).first()
    return contact


async def get_birthdays_in_next_week(limit: int, offset: int, db: Session):
    """
    The get_birthdays_in_next_week function returns a list of contacts with birthdays in the next week.

        The function takes three arguments: limit, offset, and current_user.
        Limit is an integer that limits the number of results returned by the query.
        Offset is an integer that determines where to start returning results from (i.e., if you want to return only records 11-20).
        Current_user is a User object representing the user who made this request.
    
    :param limit: int: Limit the number of results returned
    :param offset: int: Specify the offset of the first record to return
    :param current_user: User: Filter the contacts by user_id
    :param db: Session: Pass the database session to the function
    :return: A list of contacts that have birthdays in the next week
    :doc-author: Trelent
    """
    current_date = date.today()
    next_week_start = current_date
    next_week_end = current_date + timedelta(days=7)

    condition = between(extract('month', Contact.birthday), next_week_start.month, next_week_end.month) & \
                between(extract('day', Contact.birthday), next_week_start.day, next_week_end.day)

    contacts = db.query(Contact).filter(condition).limit(limit).offset(offset).all()

    return contacts


async def create_contact(body: ContactModel, db: Session):
    """
    The create_contact function creates a new contact in the database.
        
    
    :param body: ContactModel: Pass in the contactmodel object that is created from the request body
    :param current_user: User: Get the user id of the current user
    :param db: Session: Access the database
    :return: A contact object
    :doc-author: Trelent
    """
    contact = Contact(**body.model_dump())
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact


async def update_contact(body: ContactModel, contact_id: int, db: Session):
    """
    The update_contact function updates a contact in the database.

        Args:
            body (ContactModel): The updated contact information.
            contact_id (int): The id of the contact to update.
            current_user (User): The user who is making this request, used for authorization purposes.
            db (Session): A connection to the database, used for querying and updating data.
    
    :param body: ContactModel: Receive the data from the request body
    :param contact_id: int: Identify the contact that is being updated
    :param current_user: User: Get the user_id from the current logged in user
    :param db: Session: Access the database
    :return: A contact
    :doc-author: Trelent
    """
    contact = db.query(Contact).filter_by(id=contact_id).first()
    if contact:
        contact.name = body.name
        contact.surname = body.surname
        contact.email = body.email
        contact.phone = body.phone
        contact.birthday = body.birthday
        contact.additional = body.additional
        db.commit()
    return contact


async def remove_contact(contact_id: int, db: Session):
    """
    The remove_contact function removes a contact from the database.
    
        Args:
            contact_id (int): The id of the contact to be removed.
            current_user (User): The user who is making this request.
            db (Session): A session object for interacting with the database.
        Returns:
            Contact: The deleted Contact object, or None if no such Contact exists.
    
    :param contact_id: int: Specify the id of the contact to be deleted
    :param current_user: User: Identify the user that is currently logged in
    :param db: Session: Access the database
    :return: The contact that was deleted
    :doc-author: Trelent
    """
    contact = db.query(Contact).filter_by(id=contact_id).first()
    if contact:
        db.delete(contact)
        db.commit()
    return contact

