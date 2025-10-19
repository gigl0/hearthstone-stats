# scripts/init_db.py
from app.db.session import Base, engine
from app.models.models import BattlegroundsMatch

print("Creating tables...")
Base.metadata.create_all(bind=engine)
print("✅ Tables created successfully.")
