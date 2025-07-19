# backend/init_db.py

from .database import Base, engine
from .models import ClientMail # Import your model

print("Creating database and tables...")

# This command looks at all the classes that inherit from Base (i.e., your models)
# and creates the corresponding tables in the database.
Base.metadata.create_all(bind=engine)

print("Database and tables created successfully.")