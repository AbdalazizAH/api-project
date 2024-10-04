# # backend/app/routers/DasRouteAdmin.py


from datetime import timedelta
from fastapi import APIRouter,HTTPException, Depends,status
from fastapi.security import OAuth2PasswordRequestForm
from backend.app.database import get_db
from backend.app.models.DasModelAdmin import User
from backend.app.schemas.DasSchemasAdmin import UserCreate, UserInDB
from backend.app.schemas.Verif import VerificationRequest
from backend.app.utils.authenticate import authenticate_user, create_access_token, generate_verification_code, get_current_user, get_password_hash, send_email_verification

prefix = "/admin"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
router = APIRouter(prefix=prefix, tags=["Admin"])


@router.post("/register", response_model=UserInDB)
def register_user(user: UserCreate, db=Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")

    db_email = db.query(User).filter(User.email == user.email).first()
    if db_email:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = get_password_hash(user.password)
    email_code = generate_verification_code()

    new_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        email_verification_code=email_code,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Send verification codes
    send_email_verification(user.email, email_code)
    db.commit()

    return UserInDB(
        id=new_user.id,
        username=new_user.username,
        email=new_user.email,
        registration_date=new_user.registration_date,
        is_email_verified=new_user.is_email_verified,
    )

@router.post("/verify/email")
def verify_email(verification: VerificationRequest, db=Depends(get_db)):
    user = db.query(User).filter(User.username == verification.username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.email_verification_code != verification.code:
        raise HTTPException(status_code=400, detail="Invalid verification code")
    user.is_email_verified = True
    db.commit()
    return {"msg": "Email verified successfully"}



@router.get("/users/me", response_model=UserInDB)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return UserInDB(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        registration_date=current_user.registration_date,
        is_email_verified=current_user.is_email_verified,

    )
