import unittest
from unittest.mock import MagicMock
from datetime import datetime

from sqlalchemy.orm import Session

from src.database.models import Contact, User
from src.schemas import ContactModel
from src.repository.contacts import (
    get_all_contacts,
    get_contact_by_id,
    get_contact_by_name,
    get_contact_by_surname,
    get_contact_by_email,
    get_birthdays_in_next_week,
    create_contact,
    update_contact,
    remove_contact,
)

class TestContacts(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.session = MagicMock(spec=Session)
        self.user = User(id=1)

    async def test_get_all_contacts(self):
        test_contacts = [Contact(), Contact(), Contact()]
        self.session.query().filter_by().limit().offset().all.return_value = (
            test_contacts
        )
        result = await get_all_contacts(10, 0, self.user, self.session)
        self.assertEqual(result, test_contacts)

    async def test_get_contact_by_id(self):
        test_contact = Contact()
        self.session.query().filter_by().first.return_value = test_contact
        result = await get_contact_by_id(1, self.user, self.session)
        self.assertEqual(result, test_contact)

    async def test_get_contact_not_found(self):
        self.session.query().filter_by().first.return_value = None
        result = await get_contact_by_id(1, self.user, self.session)
        self.assertIsNone(result)

    async def test_get_contact_by_name(self):
        test_contacts = [Contact(), Contact(), Contact()]
        self.session.query().filter_by().limit().offset().all.return_value = (
            test_contacts
        )
        result = await get_contact_by_name("Max", 10, 0, self.user, self.session)
        self.assertEqual(result, test_contacts)

    async def test_get_contact_by_surname(self):
        test_contacts = [Contact(), Contact(), Contact()]
        self.session.query().filter_by().limit().offset().all.return_value = (
            test_contacts
        )
        result = await get_contact_by_surname("Jonson", 10, 0, self.user, self.session)
        self.assertEqual(result, test_contacts)

    async def test_get_contact_by_email(self):
        test_contact = Contact()
        self.session.query().filter_by().first.return_value = test_contact
        result = await get_contact_by_email("test@test.com", self.user, self.session)
        self.assertEqual(result, test_contact)

    async def test_get_birthdays_in_next_week(self):
        test_contacts = [Contact(), Contact(), Contact()]
        self.session.query().filter().limit().offset().all.return_value = test_contacts
        result = await get_birthdays_in_next_week(
            10, 0, self.user, self.session
        )
        self.assertEqual(result, test_contacts)

    async def test_create_contact(self):
        birthday_date = datetime.strptime("2000-10-10", "%Y-%m-%d").date()
        body = ContactModel(
            name="name",
            surname="surname",
            email="test@test@email",
            phone="1234456",
            birthday=birthday_date,
            additional="t3st",
        )
        result = await create_contact(body, self.user, self.session)
        self.assertEqual(result.name, body.name)
        self.assertEqual(result.surname, body.surname)
        self.assertEqual(result.email, body.email)
        self.assertEqual(result.phone, body.phone)
        self.assertEqual(str(result.birthday), str(body.birthday))
        self.assertTrue(hasattr(result, "id"))

    async def test_update_contact(self):
        birthday_date = datetime.strptime("2000-10-10", "%Y-%m-%d").date()
        body = ContactModel(
            name="name",
            surname="surname",
            email="test@test@email",
            phone="1234456",
            birthday=birthday_date,
            additional="t3st",
        )
        contact = Contact()
        self.session.query().filter_by().first.return_value = contact
        self.session.commit.return_value = None
        result = await update_contact(body, contact, self.user, self.session)
        self.assertEqual(result, contact)

    async def test_update_contact_not_found(self):
        birthday_date = datetime.strptime("2000-10-10", "%Y-%m-%d").date()
        body = ContactModel(
            name="name",
            surname="surname",
            email="test@test@email",
            phone="1234456",
            birthday=birthday_date,
            additional="t3st",
        )
        contact = Contact()
        self.session.query().filter_by().first.return_value = None
        self.session.commit.return_value = None
        result = await update_contact(body, contact, self.user, self.session)
        self.assertIsNone(result)

    async def test_remove_contact(self):
        contact = Contact()
        self.session.query().filter_by().first.return_value = contact
        result = await remove_contact(1, self.user, self.session)
        self.assertEqual(result, contact)

    async def test_remove_contact_not_found(self):
        self.session.query().filter_by().first.return_value = None
        result = await remove_contact(1, self.user, self.session)
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()