from app.database import engine
from app.models import Base
import os

def create_folders():
    for folder in ["logs", "audio", "temp_calls"]:
        os.makedirs(folder, exist_ok=True)

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    create_folders()