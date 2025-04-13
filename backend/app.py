import os
import time
from datetime import datetime, timedelta
from typing import Optional, Dict
import google.generativeai as genai
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from jose import jwt, JWTError
from passlib.context import CryptContext
import logging
from cachetools import TTLCache
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from sqlalchemy.orm import Session
from sqlalchemy.exc import OperationalError, SQLAlchemyError
import schemas
from database import get_db, engine
import models
from fastapi.responses import JSONResponse
import httpx

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

try:
    # Create database tables
    models.Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")
except Exception as e:
    logger.error(f"Error creating database tables: {str(e)}")
    raise

# Initialize FastAPI app
app = FastAPI(
    title="AI Tutor API",
    description="An AI-powered educational tutoring system",
    version="1.0.0"
)

# Configure CORS with proper origins
FRONTEND_URL = os.getenv("FRONTEND_URL", "https://ai-tutor-io.vercel.app/")
ALLOWED_ORIGINS = [
    FRONTEND_URL,
    "http://localhost:3000",  # Local development
    "http://localhost:5000"   # Local development alternative
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,
)

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Initialize cache
cache = TTLCache(maxsize=100, ttl=300)  # Cache for 5 minutes

# Security
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

# Configure Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-pro")

# Secret key for JWT
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

# User model
class User(BaseModel):
    username: str
    email: str
    full_name: Optional[str] = None
    disabled: Optional[bool] = None

class UserInDB(User):
    hashed_password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

# Query model
class Query(BaseModel):
    topic: str

# Google OAuth settings
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:3000/auth/google/callback")

def get_user(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def authenticate_user(db: Session, username: str, password: str):
    user = get_user(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

@app.post("/signup", response_model=schemas.User)
def signup(user: schemas.UserCreate, db: Session = Depends(get_db)):
    try:
        # Check if username already exists
        db_user = db.query(models.User).filter(models.User.username == user.username).first()
        if db_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered"
            )
        
        # Check if email already exists
        db_user = db.query(models.User).filter(models.User.email == user.email).first()
        if db_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create new user
        hashed_password = get_password_hash(user.password)
        db_user = models.User(
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            hashed_password=hashed_password
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error during signup: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Unable to create user account. Please try again later."
        )

@app.post("/token", response_model=schemas.Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me", response_model=schemas.User)
async def read_users_me(current_user: models.User = Depends(get_current_user)):
    return current_user

@app.post("/tutor")
@limiter.limit("5/minute")
async def educational_tutor(
    request: Request,
    query: Query,
    current_user: User = Depends(get_current_user)
):
    cache_key = f"tutor_{query.topic}_{current_user.username}"
    if cache_key in cache:
        logger.info(f"Returning cached response for {query.topic}")
        return cache[cache_key]

    prompt = f"""
    You are an educational tutor. 
    The topic is: {query.topic}.
    
    Tasks:
    1. Start with a friendly greeting and brief introduction to the topic 🎯
    2. Structure your response with clear sections using emojis:
       📚 Main Concepts
       💡 Key Points
       ⚡ Examples
       🎯 Practice Tips
       ❓ Common Questions
    3. Use emojis to highlight important points and make the content engaging
    4. Include code examples where relevant
    5. End with an encouraging message and next steps
    
    Format Guidelines:
    - Use bullet points (•) instead of asterisks
    - Keep paragraphs short and readable
    - Use proper spacing between sections
    - Include relevant emojis for visual appeal
    - Make code examples clear and well-commented
    
    Make the response engaging, easy to understand, and well-structured.
    """
    try:
        response = model.generate_content(prompt)
        result = {"response": response.text, "user": current_user.username}
        cache[cache_key] = result
        logger.info(f"Generated new response for {query.topic}")
        return result
    except Exception as e:
        logger.error(f"Error generating response: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tutor")
@limiter.limit("5/minute")
async def educational_tutor_get(
    request: Request,
    topic: str,
    current_user: User = Depends(get_current_user)
):
    query = Query(topic=topic)
    return await educational_tutor(request, query, current_user)

@app.post("/upload")
@limiter.limit("3/minute")
async def upload_file(
    request: Request,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    contents = await file.read()
    prompt = f"Analyze this document and assist the student accordingly:\n\n{contents.decode()}"
    
    try:
        response = model.generate_content(prompt)
        return {
            "response": response.text,
            "filename": file.filename,
            "user": current_user.username
        }
    except Exception as e:
        logger.error(f"Error processing file: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Health check endpoint
@app.get("/health")
async def health_check():
    try:
        # Check database connection
        with engine.connect() as connection:
            connection.execute("SELECT 1")
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy", "database": "disconnected"}
        )

# Error handler for database errors
@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    logger.error(f"Database error: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={"detail": "Database error occurred. Please try again later."}
    )

# Google OAuth endpoints
@app.post("/auth/google", response_model=schemas.GoogleAuthResponse)
async def google_auth(google_token: dict, db: Session = Depends(get_db)):
    """
    Authenticate user with Google token
    """
    try:
        # Verify the token with Google
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://www.googleapis.com/oauth2/v3/userinfo?access_token={google_token['access_token']}"
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid Google token"
                )
            
            user_info = response.json()
            google_id = user_info["sub"]
            email = user_info["email"]
            full_name = user_info.get("name")
            picture = user_info.get("picture")
            
            # Check if user exists
            user = db.query(models.User).filter(models.User.google_id == google_id).first()
            
            if not user:
                # Check if user exists with this email
                user = db.query(models.User).filter(models.User.email == email).first()
                
                if user:
                    # Update existing user with Google ID
                    user.google_id = google_id
                    user.picture = picture
                    db.commit()
                else:
                    # Create new user
                    username = email.split('@')[0]  # Use email prefix as username
                    # Check if username exists
                    existing_user = db.query(models.User).filter(models.User.username == username).first()
                    if existing_user:
                        # Add random number to username
                        import random
                        username = f"{username}{random.randint(1000, 9999)}"
                    
                    user = models.User(
                        username=username,
                        email=email,
                        full_name=full_name,
                        google_id=google_id,
                        picture=picture
                    )
                    db.add(user)
                    db.commit()
                    db.refresh(user)
            
            # Create access token
            access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            access_token = create_access_token(
                data={"sub": user.username}, expires_delta=access_token_expires
            )
            
            return {
                "access_token": access_token,
                "token_type": "bearer",
                "user": {
                    "username": user.username,
                    "email": user.email,
                    "full_name": user.full_name
                }
            }
            
    except Exception as e:
        logger.error(f"Google authentication error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication failed"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
