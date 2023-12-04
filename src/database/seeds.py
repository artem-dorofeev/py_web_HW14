from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from faker import Faker

from models import Base, Contact
from db import URI


engine = create_engine(URI)
Session = sessionmaker(bind=engine)
session = Session()

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)

fake = Faker('uk_UA')

# Create 40 fake contacts and insert them into the database
for _ in range(40):
    contact = Contact(
        name=fake.first_name(),
        surname=fake.last_name(),
        email=fake.email(),
        phone=fake.phone_number(),
        birthday=fake.date_of_birth(minimum_age=18, maximum_age=65),
        additional=fake.text(max_nb_chars=20),  # Limit text to 20 characters
    )

    session.add(contact)

session.commit()
