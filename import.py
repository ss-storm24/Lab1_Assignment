import os
import csv

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

def main():
    f_books = open("books.csv")
    reader = csv.reader(f_books)
    for title, author, year, isbn in reader:
        db.execute("INSERT INTO books (title, author, year, isbn) VALUES (:title, :author, :year, :isbn)", {"title": title, "author": author, "year": year, "isbn": isbn})
        print(f"Added book with title:{title}, author:{author}, publication year:{year}, and isbn:{isbn}")
    db.commit()

if __name__=="__main__":
    main()

