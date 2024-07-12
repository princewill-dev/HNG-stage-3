from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from . import crud, schemas, models, database
from .otp import send_otp

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/register", response_model=schemas.User, summary="Create a new user", description="Register a new user with first name, last name, email, phone, and password.")
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Create a new user in the system.
    - **first_name**: First name of the user.
    - **last_name**: Last name of the user.
    - **email**: Unique email address of the user.
    - **phone**: Phone number of the user.
    - **password**: Password for the user account.
    """
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    db_user = crud.create_user(db=db, user=user)
    otp_code = crud.generate_otp()
    crud.set_otp(db, db_user, otp_code)
    send_otp(db_user.email, otp_code)
    return db_user

@router.post("/verify-otp", summary="Verify OTP", description="Verify the OTP code sent to the user's email address.")
def verify_otp(email: str, otp_code: str, db: Session = Depends(get_db)):
    """
    Verify the OTP code for a user.
    - **email**: Email address of the user.
    - **otp_code**: OTP code received by the user.
    """
    user = crud.get_user_by_email(db, email=email)
    if not user:
        raise HTTPException(status_code=400, detail="User not found")
    if not crud.verify_otp(db, user, otp_code):
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")
    return {"msg": "Verification successful"}

@router.post("/token", summary="Login to get an access token", description="Login with email and password to receive an access token.")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Authenticate a user and return an access token.
    - **username**: The email of the user.
    - **password**: The password of the user.
    """
    user = crud.get_user_by_email(db, email=form_data.username)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    if not crud.pwd_context.verify(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    if not user.is_verified:
        raise HTTPException(status_code=400, detail="Email not verified")
    return {"access_token": user.email, "token_type": "bearer"}

@router.get("/profile/{account_id}", response_model=schemas.UserProfile, summary="Get user profile", description="Fetch the profile details of a user by their account ID.")
def get_profile(account_id: str, db: Session = Depends(get_db)):
    """
    Get the profile details of a user.
    - **account_id**: Unique account ID of the user.
    """
    user = crud.get_user_by_account_id(db, account_id=account_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return schemas.UserProfile(
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        phone=user.phone,
        account_id=user.account_id
    )
