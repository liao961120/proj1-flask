import csv
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

def main():
    # import data from csv
    f = open("books.csv")
    reader = csv.reader(f)
    print(next(reader))
    for isbn, title, author, year in reader:
        db.execute("INSERT INTO books (isbn, title, author, year) VALUES (:isbn, :title, :author, :year)",
                    {"isbn": isbn, "title": title, "author": author, "year": int(year)})
        print(f"Added book '{title}' by {author}, {year}")
    db.commit()
    # Print table
    books = db.execute("SELECT * FROM books LIMIT 10").fetchall()
    for book in books:
        #print(book)
        print(f"{book.id}\t{book.isbn}\t{book.title}\t{book.author}\t{book.year}\n")

if __name__ == "__main__":
    main()
