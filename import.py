import os
import csv

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine("postgresql://wlkiwvwgqndwtf:411e57176f8293d3bafb47d1ad1899c1c9048b85f641b92b4e6b1e9e506351ae@ec2-54-209-165-105.compute-1.amazonaws.com:5432/d87jp096ui7i1f")
db = scoped_session(sessionmaker(bind=engine))

def main():
    f_books = open("books.csv")
    reader = csv.reader(f_books)
    for isbn, title, author, year in reader:
        db.execute("INSERT INTO books (isbn, title, author, year) VALUES (:isbn, :title, :author, :year)", {"isbn": isbn, "title": title, "author": author, "year": year})
        print(f"Added book with isbn:{isbn}, title:{title}, author:{author}, and publication year:{year}")
    db.commit()

if __name__=="__main__":
    main()

