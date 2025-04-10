from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
import logging
import time
from sqlalchemy.exc import OperationalError
import sys

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Get database URL from environment variable
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    logger.error("DATABASE_URL environment variable is not set")
    logger.error("Please set the DATABASE_URL in your .env file")
    sys.exit(1)

def create_db_engine(retries=3, delay=2):
    """Create database engine with retry logic"""
    for attempt in range(retries):
        try:
            logger.info(f"Attempting to connect to database (attempt {attempt+1}/{retries})")
            
            # Create SQLAlchemy engine with connection pooling and timeout settings
            engine = create_engine(
                DATABASE_URL,
                pool_pre_ping=True,  # Enable connection health checks
                pool_recycle=300,    # Recycle connections every 5 minutes
                connect_args={
                    "connect_timeout": 10,  # Connection timeout in seconds
                    "keepalives": 1,        # Enable TCP keepalive
                    "keepalives_idle": 30   # Idle time before sending keepalive
                }
            )
            
            # Test the connection
            with engine.connect() as connection:
                logger.info("Successfully connected to the database")
                return engine
                
        except OperationalError as e:
            if attempt < retries - 1:
                logger.warning(f"Database connection attempt {attempt + 1} failed. Retrying in {delay} seconds...")
                logger.warning(f"Error: {str(e)}")
                time.sleep(delay)
            else:
                logger.error("Failed to connect to the database after multiple attempts")
                logger.error("Please check that:")
                logger.error("1. Your Neon.tech database is active (not paused)")
                logger.error("2. Your database credentials are correct")
                logger.error("3. Your IP is allowed to access the database")
                logger.error(f"Connection string: {DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else 'REDACTED'}")
                raise

# Create engine with retry logic
try:
    engine = create_db_engine()
except Exception as e:
    logger.error(f"Fatal database error: {str(e)}")
    logger.error("Application cannot start without a database connection")
    sys.exit(1)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class
Base = declarative_base()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 