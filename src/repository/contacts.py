from datetime import date, timedelta
from sqlalchemy import and_, extract, or_, between
from sqlalchemy.orm import Session

from src.database.models import Contact, User
from src.schemas import ContactModel


async def get_all_contacts(limit: int, offset: int, current_user: User, db: Session):
    contacts = db.query(Contact).filter_by(user_id=current_user.id)
    contacts = contacts.limit(limit).offset(offset).all()
    return contacts

async def get_contact_by_id(contact_id: int, db: Session):
    contact = db.query(Contact).filter_by(id=contact_id).first()
    return contact


async def get_contact_by_name(contact_name: str, limit: int, offset: int, db: Session):
    contacts = db.query(Contact).filter_by(name=contact_name)
    contacts = contacts.limit(limit).offset(offset)
    return contacts


async def get_contact_by_surname(contact_surname: str, limit: int, offset: int,db: Session):
    contacts = db.query(Contact).filter_by(surname=contact_surname)
    contacts = contacts.limit(limit).offset(offset)
    return contacts


async def get_contact_by_email(contact_email: str, db: Session):
    contact = db.query(Contact).filter_by(email=contact_email).first()
    return contact


async def get_birthdays_in_next_week(limit: int, offset: int, db: Session):
    current_date = date.today()
    next_week_start = current_date
    next_week_end = current_date + timedelta(days=7)

    condition = between(extract('month', Contact.birthday), next_week_start.month, next_week_end.month) & \
                between(extract('day', Contact.birthday), next_week_start.day, next_week_end.day)

    contacts = db.query(Contact).filter(condition).limit(limit).offset(offset).all()

    return contacts


async def create_contact(body: ContactModel, db: Session):
    contact = Contact(**body.model_dump())
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact


async def update_contact(body: ContactModel, contact_id: int, db: Session):
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
    contact = db.query(Contact).filter_by(id=contact_id).first()
    if contact:
        db.delete(contact)
        db.commit()
    return contact

