import grpc
from concurrent import futures
import sys
import os
import signal
import sqlite3
from dotenv import load_dotenv

load_dotenv()

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import books_pb2
import books_pb2_grpc

DB_PATH = os.getenv('DB_PATH', 'books.db')


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS books (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        author TEXT NOT NULL,
        year INTEGER NOT NULL
    )
    ''')

    cursor.execute("SELECT COUNT(*) FROM books")
    count = cursor.fetchone()[0]

    if count == 0:
        sample_books = [
            ("Pride and Prejudice", "Jane Austen", 1813),
            ("1984", "George Orwell", 1949),
            ("To Kill a Mockingbird", "Harper Lee", 1960)
        ]
        cursor.executemany("INSERT INTO books (title, author, year) VALUES (?, ?, ?)", sample_books)

    conn.commit()
    conn.close()


class BookServiceServicer(books_pb2_grpc.BookServiceServicer):

    def get_book(self, request, context):
        """Returns a book by ID"""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute("SELECT id, title, author, year FROM books WHERE id = ?", (request.id,))
        book_data = cursor.fetchone()

        conn.close()

        if book_data:
            book = books_pb2.Book(
                id=book_data[0],
                title=book_data[1],
                author=book_data[2],
                year=book_data[3]
            )
            return books_pb2.BookResponse(book=book)
        else:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"Book with ID {request.id} not found")
            return books_pb2.BookResponse()

    def list_books(self, request, context):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute("SELECT id, title, author, year FROM books")
        books_data = cursor.fetchall()

        conn.close()

        books = []
        for book_data in books_data:
            book = books_pb2.Book(
                id=book_data[0],
                title=book_data[1],
                author=book_data[2],
                year=book_data[3]
            )
            books.append(book)

        return books_pb2.ListBooksResponse(books=books)

    def add_book(self, request, context):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO books (title, author, year) VALUES (?, ?, ?)",
            (request.title, request.author, request.year)
        )

        book_id = cursor.lastrowid

        conn.commit()
        conn.close()

        book = books_pb2.Book(
            id=book_id,
            title=request.title,
            author=request.author,
            year=request.year
        )

        return books_pb2.BookResponse(book=book)

    def delete_book(self, request, context):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute("SELECT id FROM books WHERE id = ?", (request.id,))
        book = cursor.fetchone()

        if not book:
            conn.close()
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"Book with ID {request.id} not found")
            return books_pb2.DeleteBookResponse(success=False, message=f"Book with ID {request.id} not found")

        cursor.execute("DELETE FROM books WHERE id = ?", (request.id,))
        conn.commit()
        conn.close()

        return books_pb2.DeleteBookResponse(success=True, message=f"Book with ID {request.id} deleted successfully")


def serve():
    init_db()

    port = int(os.getenv('GRPC_PORT', '50051'))
    max_workers = int(os.getenv('GRPC_MAX_WORKERS', '10'))
    max_message_size = int(os.getenv('GRPC_MAX_MESSAGE_SIZE', '50')) * 1024 * 1024  # in MB
    keepalive_time = int(os.getenv('GRPC_KEEPALIVE_TIME', '60000'))  # in ms
    keepalive_timeout = int(os.getenv('GRPC_KEEPALIVE_TIMEOUT', '20000'))  # in ms
    shutdown_timeout = int(os.getenv('GRPC_SHUTDOWN_TIMEOUT', '30'))  # in seconds

    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=max_workers),
        options=[
            ('grpc.max_send_message_length', max_message_size),
            ('grpc.max_receive_message_length', max_message_size),
            ('grpc.keepalive_time_ms', keepalive_time),
            ('grpc.keepalive_timeout_ms', keepalive_timeout),
        ]
    )

    books_pb2_grpc.add_BookServiceServicer_to_server(BookServiceServicer(), server)

    server.add_insecure_port(f'[::]:{port}')

    server.start()
    print(f"Server started on port {port}")

    def handle_shutdown(sign, frame):
        print("Shutting down server...")
        stopped = server.stop(shutdown_timeout)
        if stopped:
            print("Server stopped successfully")
        else:
            print("Server forced to stop")

    signal.signal(signal.SIGTERM, handle_shutdown)
    signal.signal(signal.SIGINT, handle_shutdown)

    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        handle_shutdown(None, None)


if __name__ == '__main__':
    serve()
