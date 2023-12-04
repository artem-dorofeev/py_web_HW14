from fastapi import HTTPException, status
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker

from src.conf.config import settings

URI = settings.sqlalchemy_database_url

engine = create_engine(URI, echo=False, pool_size=5)

DBSession = sessionmaker(bind=engine)
session = DBSession()

# Dependency


def get_db():
    """
    The get_db function is a context manager that will automatically close the database connection when it goes out of scope.
    It also handles any exceptions that occur within the with block, rolling back changes if necessary.

    :return: A generator, which is a function that returns an object on which you can call next,
    :doc-author: Trelent
    """

    db = DBSession()
    try:
        yield db
    except SQLAlchemyError as err:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err))
    finally:
        db.close()
