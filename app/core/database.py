from sqlmodel import create_engine, Session
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

engine = create_engine(
    settings.MYSQL_URL,
    echo=False,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=True,
    bind=engine,
    class_=Session
)

def get_db():
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()
