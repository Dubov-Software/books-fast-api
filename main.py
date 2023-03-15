from fastapi import FastAPI
import motor.motor_asyncio
import ujson
import uvicorn
from pydantic import BaseModel, EmailStr
from fastapi_users.authentication import AuthenticationBackend, BearerTransport, JWTStrategy
from bson.objectid import ObjectId
from dotenv import load_dotenv
import os
load_dotenv()

SECRET = os.getenv("SECRET_KEY")
bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")

def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=SECRET, lifetime_seconds=3600)

auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)

app = FastAPI(
    title="Books API",
    description="A simple CRUD API for managing books",
    version="1.0.0",
    openapi_url="/api/v1/openapi.json",
    docs_url="/api/v1/docs",
    redoc_url="/api/v1/redoc",
)
client = motor.motor_asyncio.AsyncIOMotorClient(os.getenv("DATABASE_URL"))
database = client.BooksDB
collection = database.books

class User(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: EmailStr
    password: str

class Book(BaseModel):
    id: str = None
    title: str
    author: str
    year: int

    # TODO - find a better way to gaurd data in the 
    def to_dict(self):
        return {
            "title": self.title,
            "author": self.author,
            "year": self.year
        }

@app.on_event("startup")
async def startup():
    pass

@app.get("/")
async def root():
    return {"message": "Hello, World!"}

@app.get("/books")
async def read_books():
    books = []
    async for book in collection.find():
        books.append(Book(**book, id=str(book['_id'])))
    return books

@app.get("/books/{book_id}")
async def read_book(book_id: str):
    book = await collection.find_one({'_id': ObjectId(book_id)})
    if book:
        return Book(**book, id=str(book['_id']))
    else:
        return {"message": "Book not found"}

@app.post("/books")
async def create_book(book: Book):
    result = await collection.insert_one(book.to_dict())
    return Book(**book.dict(), id=str(result.inserted_id))

@app.put("/books/{book_id}")
async def update_book(book_id: str, book: Book):
    book_dict = book.dict(exclude_unset=True)
    if len(book_dict) > 0:
        result = await collection.update_one({'_id': ObjectId(book_id)}, {'$set': book_dict})
        if result.modified_count == 1:
            return Book(**book.dict(), id=book_id)
        else:
            return {"message": "Failed to update book"}
    else:
        return Book(**book.dict(), id=book_id)

@app.delete("/books/{book_id}")
async def delete_book(book_id: str):
    result = await collection.delete_one({'_id': ObjectId(book_id)})
    if result.deleted_count == 1:
        return {"message": "Book deleted successfully"}
    else:
        return {"message": "Failed to delete book"}

if __name__ == "__main__":
    config = uvicorn.Config("main:app", port=int(os.getenv("PORT")), log_level="info", reload=True)
    server = uvicorn.Server(config)
    server.run()