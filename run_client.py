import uvicorn
from client.config import API_HOST, API_PORT

if __name__ == "__main__":
    uvicorn.run(
        "client.main:app",
        host=API_HOST,
        port=API_PORT,
        reload=True
    )
