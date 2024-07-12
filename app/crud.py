from sqlalchemy.orm import Session
from . import models, schemas
from passlib.context import CryptContext
from datetime import datetime, timedelta
import random
import string

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_user_by_email(db: Session, email: str):
    """
    Get a user by email.
    - **email**: Email address of the user.
    """
    return db.query(models.User).filter(models.User.email == email).first()

def get_user_by_account_id(db: Session, account_id: str):
    """
    Get a user by account ID.
    - **account_id**: Unique account ID of the user.
    """
    return db.query(models.User).filter(models.User.account_id == account_id).first()

def create_user(db: Session, user: schemas.UserCreate):
    """
    Create a new user in the database.
    - **user**: UserCreate schema containing user details.
    """
    hashed_password = pwd_context.hash(user.password)
    account_id = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
    db_user = models.User(
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        phone=user.phone,
        hashed_password=hashed_password,
        account_id=account_id
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def generate_otp():
    """
    Generate a 6-digit OTP code.
    """
    return ''.join(random.choices(string.digits, k=6))

def set_otp(db: Session, user: models.User, otp_code: str):
    """
    Set OTP code and expiry for a user.
    - **user**: User model instance.
    - **otp_code**: Generated OTP code.
    """
    user.otp_code = otp_code
    user.otp_expiry = datetime.utcnow() + timedelta(minutes=10)
    db.commit()
    db.refresh(user)

def verify_otp(db: Session, user: models.User, otp_code: str):
    """
    Verify the OTP code for a user.
    - **user**: User model instance.
    - **otp_code**: OTP code provided by the user.
    """
    if user.otp_code == otp_code and user.otp_expiry > datetime.utcnow():
        user.is_verified = True
        user.otp_code = None
        user.otp_expiry = None
        db.commit()
        db.refresh(user)
        return True
    return False
