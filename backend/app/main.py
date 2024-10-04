from datetime import timedelta
from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from backend.app.routes import DasRouteAdmin, HeroRoute
from backend.app.database import Base, get_db, engine
from backend.app.utils.authenticate import authenticate_user, create_access_token
ACCESS_TOKEN_EXPIRE_MINUTES = 30

class Config:
    DEBUG = True
    ALLOWED_ORIGINS = [
        "http://localhost:3000",
        "https://yourdomain.com",
    ]


class HeaderMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
            "Pragma": "no-cache",
        }
        response.headers.update(headers)
        return response


app = FastAPI(
    title="Ecommerce Project",
    description="A project for E-commerce",
    version="0.1.0",
    openapi_url="/openapi.json" if Config.DEBUG else None,
    docs_url="/docs" if Config.DEBUG else None,
    redoc_url="/redoc" if Config.DEBUG else None,
    debug=Config.DEBUG,
)
Base.metadata.create_all(bind=engine)

app.add_middleware(HeaderMiddleware)
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    CORSMiddleware,
    allow_origins= ["*"] if Config.DEBUG else Config.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

app.include_router(HeroRoute.router)
app.include_router(DasRouteAdmin.router)
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected error occurred."},
    )

@app.get("/")
def root():
    return {
        "info": {
            "test": "welcome",
            "title": "Ecommerce Project",
            "description": "A project for E-commerce",
            "version": "0.1.0",
        },
        "docs": {"docs_url": "/docs", "redoc_url": "/redoc"},
    }

@app.post("/token")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db=Depends(get_db)
):
    user = authenticate_user(db, form_data.username, form_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_email_verified:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email not verified",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
