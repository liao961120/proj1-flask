# Web Programming with Python and JavaScript: Project 1

## Goal

<https://docs.cs50.net/web/2018/x/projects/1/project1.html>


## Setup and Run App: 

1. Import `books.csv` to Database (Only first time)

    - Set up database URL and Goodreads API key:

      - Set database URL in `export DATABASE_URL='<database-url>'` of `keys`
      
      - Set Goodreads API key in `export goodreadsAPI='<goodreads-key>'` of `keys`
      
      - Export environmental variables
      
      ```bash
      source keys
      ```
    
    - Create tables
    
    ```bash
    python3 create_tables.py
    ```
    
    - Import data from csv to database
    
    ```bash
    python3 import.py
    ```
    
2. Configure Flask

    - Export environmental variables
    
    ```bash
    export FLASK_APP=application.py
    export FLASK_DEBUG=1
    source keys
    ```

3. Run App
    
    ```bash
    flask run
    ```
