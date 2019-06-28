import requests
import os

def goodreads(isbn):
    res = requests.get('https://www.goodreads.com/book/review_counts.json', 
        params={'key':os.getenv("goodreadsAPI"), 'isbns':str(isbn)})
    return res