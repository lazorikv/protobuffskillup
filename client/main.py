import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .auth.router import router as auth_router
from .books.router import router as books_router
from .config import API_HOST, API_PORT
from .services.database import init_db


init_db()

app = FastAPI(
    title="API Gateway",
    description="API Gateway for Book Service with Authentication",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(books_router)


@app.get("/", tags=["Root"])
async def read_root():
    return {
        "message": "Welcome to the Book Service API Gateway",
        "endpoints": {
            "Authentication": {
                "POST /register": "Register a new user",
                "POST /login": "Get access token",
                "GET /users/me": "Get current user info"
            },
            "Books": {
                "GET /books": "List all books",
                "GET /books/{book_id}": "Get a book by ID",
                "POST /books": "Add a new book",
                "DELETE /books/{book_id}": "Delete a book by ID"
            }
        }
    }

if __name__ == "__main__":
    uvicorn.run(
        "gateway.main:app",
        host=API_HOST,
        port=API_PORT,
        reload=True
    )
 