from fastapi import FastAPI
from app.database import engine
from app import models
from app.auth import router as auth_router

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="User Authentication API",
    description="API for user registration, login, and authentication with email verification",
    version="1.0.0",
    terms_of_service="http://example.com/terms/",
    contact={
        "name": "API Support",
        "url": "http://example.com/contact/",
        "email": "support@example.com",
    },
    license_info={
        "name": "Apache 2.0",
        "url": "http://www.apache.org/licenses/LICENSE-2.0.html",
    },
)

app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])

# You can add more routers for other parts of your application here
