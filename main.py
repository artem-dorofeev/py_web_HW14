import time
from pathlib import Path

from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
from fastapi.middleware.cors import CORSMiddleware
import redis.asyncio as redis

from sqlalchemy import text 
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.routes import contacts, auth, users
from src.conf.config import settings



app = FastAPI()


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """
    The add_process_time_header function adds a header to the response called My-Process-Time.
    The value of this header is the time it took for the request to be processed by all middleware and routes.
    
    :param request: Request: Access the request object
    :param call_next: Call the next function in the pipeline
    :return: A response object with a header called my-process-time
    :doc-author: Trelent
    """
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["My-Process-Time"] = str(process_time)
    return response



origins = ["http://localhost:3000", "http://127.0.0.1:5000/"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


templates = Jinja2Templates(directory='templates')


# Get the absolute path to the current directory of your script
current_directory = Path(__file__).resolve().parent

# Define the relative path to the 'static' directory from the script's directory
static_directory = current_directory / 'static'

# app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", response_class=HTMLResponse, description="Main page (description)") # by defolt it is JSONResponse
def read_root(request: Request):
    """
    The read_root function is a view callable which takes a request and returns
    a response. The root path of the website will be bound to this function, so it
    will execute when requests are made to the root URL of the site.
    
    :param request: Request: Pass the request object to the template
    :return: A templateresponse object
    :doc-author: Trelent
    """
    return templates.TemplateResponse('index.html', {'request': request, 'title': 'Contacts APP' })

@app.on_event("startup")
async def startup():
    """
    The startup function is called when the application starts up.
    It's a good place to initialize things that are used by the app, such as caches or databases.
    
    :return: A list of coroutines
    :doc-author: Trelent
    """
    r = await redis.Redis(host=settings.redis_host, port=settings.redis_port, db=0, encoding="utf-8",
                          decode_responses=True)
    await FastAPILimiter.init(r)


@app.get("/api/healthchecker")
def healthchecker(db: Session = Depends(get_db)):
    """
    The healthchecker function is used to check the health of the database.
    It will return a 200 status code if it can successfully connect to the database,
    and a 500 status code otherwise.
    
    :param db: Session: Pass the database connection to the function
    :return: A dict with a message
    :doc-author: Trelent
    """
    try:
        # Make request
        result = db.execute(text("SELECT 1")).fetchone()
        print(result)
        if result is None:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Database is not configured correctly")
        return {"message": "Welcome to FastAPI!"}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Error connecting to the database")


app.include_router(contacts.router, prefix='/api')
app.include_router(auth.router, prefix='/api')
app.include_router(users.router, prefix='/api')
