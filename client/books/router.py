from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
import grpc

from .models import Book, BookCreate
from .client import get_books_client
from ..auth.dependencies import get_current_active_user
from ..auth.models import User

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import books_pb2

router = APIRouter(prefix="/books", tags=["Books"])


@router.get("", response_model=List[Book])
async def list_books(current_user: User = Depends(get_current_active_user)):
    try:
        stub = get_books_client()
        response = stub.list_books(books_pb2.ListBooksRequest())

        books = []
        for book in response.books:
            books.append(Book(
                id=book.id,
                title=book.title,
                author=book.author,
                year=book.year
            ))

        return books
    except grpc.RpcError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"gRPC service error: {e.details()}")


@router.get("/{book_id}", response_model=Book)
async def get_book(book_id: int, current_user: User = Depends(get_current_active_user)):
    try:
        stub = get_books_client()
        response = stub.get_book(books_pb2.BookRequest(id=book_id))

        return Book(
            id=response.book.id,
            title=response.book.title,
            author=response.book.author,
            year=response.book.year
        )
    except grpc.RpcError as e:
        if e.code() == grpc.StatusCode.NOT_FOUND:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"Book with ID {book_id} not found")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"gRPC service error: {e.details()}")


@router.post("", response_model=Book, status_code=status.HTTP_201_CREATED)
async def create_book(book: BookCreate, current_user: User = Depends(get_current_active_user)):
    try:
        stub = get_books_client()
        request = books_pb2.AddBookRequest(
            title=book.title,
            author=book.author,
            year=book.year
        )

        response = stub.add_book(request)

        return Book(
            id=response.book.id,
            title=response.book.title,
            author=response.book.author,
            year=response.book.year
        )
    except grpc.RpcError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"gRPC service error: {e.details()}")


@router.delete("/{book_id}")
async def delete_book(book_id: int, current_user: User = Depends(get_current_active_user)):
    try:
        stub = get_books_client()
        response = stub.delete_book(books_pb2.BookRequest(id=book_id))

        if response.success:
            return {"success": True, "message": response.message}
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=response.message)
    except grpc.RpcError as e:
        if e.code() == grpc.StatusCode.NOT_FOUND:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"Book with ID {book_id} not found")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"gRPC service error: {e.details()}")
