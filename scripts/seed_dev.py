"""
Seed dev users for local development.

USAGE:
    python3 scripts/seed_dev.py

Creates:
    admin@swa.local / admin123!  (role: admin)
    pm@swa.local / pm123!        (role: pm)

WARNING: NEVER run in production. Default passwords are weak by design.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import uuid
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


def main():
    env = os.environ.get("APP_ENV", "dev")
    if env not in ("dev", "test"):
        print(f"REFUSING to seed in {env} environment.")
        sys.exit(1)

    db_url = os.environ.get("DATABASE_URL", "postgresql://swa:swa@localhost:5432/swa_erp")
    print(f"Seeding dev users into: {db_url}")

    try:
        from src.backend.models.user import User
        from src.backend.core.security import hash_password
    except ImportError:
        print("Backend not yet built — wait for Task 01 to complete.")
        sys.exit(1)

    engine = create_engine(db_url)
    Session = sessionmaker(bind=engine)

    seeds = [
        {"email": "admin@swa.local", "name": "Admin User", "password": "admin123!", "role": "admin"},
        {"email": "pm@swa.local", "name": "PM User", "password": "pm123!", "role": "pm"},
    ]

    with Session() as db:
        for s in seeds:
            existing = db.query(User).filter_by(email=s["email"]).first()
            if existing:
                print(f"  ✓ {s['email']} already exists")
                continue
            u = User(
                email=s["email"],
                name=s["name"],
                password_hash=hash_password(s["password"]),
                role=s["role"],
                is_active=True,
            )
            db.add(u)
            print(f"  + {s['email']} created (password: {s['password']})")
        db.commit()

    print("\n⚠️  These passwords are WEAK. For dev only. Never use in production.\n")


if __name__ == "__main__":
    main()
