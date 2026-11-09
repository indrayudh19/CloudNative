from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from services.userservice.routes import router

app = FastAPI(title="LMS User Service", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

@app.get("/")
def root():
    return {"service": "User Service", "status": "online"}

if __name__ == "__main__":
    import uvicorn
    from config import SERVICE_PORTS
    uvicorn.run("services.userservice.main:app", host="127.0.0.1", port=SERVICE_PORTS["user"], reload=True)

