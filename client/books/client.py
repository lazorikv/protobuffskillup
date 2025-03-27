import sys
import os
import grpc
from ..config import GRPC_HOST, GRPC_PORT, GRPC_MAX_MESSAGE_SIZE
from typing import Optional


sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import books_pb2_grpc


class BooksClient:
    _instance: Optional['BooksClient'] = None
    _stub = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(BooksClient, cls).__new__(cls)
            cls._instance._create_stub()
        return cls._instance

    def _create_stub(self):
        options = [
            ('grpc.max_send_message_length', GRPC_MAX_MESSAGE_SIZE),
            ('grpc.max_receive_message_length', GRPC_MAX_MESSAGE_SIZE),
        ]
        
        channel = grpc.insecure_channel(f'{GRPC_HOST}:{GRPC_PORT}', options=options)
        self._stub = books_pb2_grpc.BookServiceStub(channel)

    @property
    def stub(self):
        if self._stub is None:
            self._create_stub()
        return self._stub


def get_books_client():
    return BooksClient().stub
