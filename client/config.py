import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Server settings
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8001"))

# gRPC settings
GRPC_HOST = os.getenv("GRPC_HOST", "localhost")
GRPC_PORT = os.getenv("GRPC_PORT", "50051")
GRPC_MAX_MESSAGE_SIZE = int(os.getenv("GRPC_MAX_MESSAGE_SIZE", "50")) * 1024 * 1024

# JWT settings
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "gcvyhgviyviuvuvgui")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# Database settings
DB_PATH = os.getenv("DB_PATH", "books.db")
