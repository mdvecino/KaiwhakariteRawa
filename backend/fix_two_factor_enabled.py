from sqlalchemy.orm import sessionmaker
from ..db import engine
from ..models.users import User

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

try:
    users = db.query(User).filter(User.two_factor_enabled == None).all()
    for user in users:
        user.two_factor_enabled = False
    db.commit()
    print(f"Updated {len(users)} user(s) with NULL two_factor_enabled to False.")
except Exception as e:
    print(f"Error: {e}")
    db.rollback()
finally:
    db.close() 