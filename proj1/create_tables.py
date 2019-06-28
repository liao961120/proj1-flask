import csv
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

def main():
    db.execute("CREATE TABLE books ( id SERIAL PRIMARY KEY, isbn VARCHAR NOT NULL, title VARCHAR NOT NULL, author VARCHAR NOT NULL, year INTEGER NOT NULL);")
    db.execute("CREATE TABLE reviews ( id SERIAL PRIMARY KEY, book_id INTEGER REFERENCES books, user_id INTEGER REFERENCES users, rating INTEGER NOT NULL, comment VARCHAR NOT NULL);")
    db.execute("CREATE TABLE users ( id SERIAL PRIMARY KEY, username VARCHAR NOT NULL, password VARCHAR NOT NULL);")
    db.commit()

if __name__ == "__main__":
    main()
