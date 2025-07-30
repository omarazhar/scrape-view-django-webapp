# Project: Scrap & View in Django WebApp!

In this Python based Django web-app project, we will scrape data from a public domain, stores it in a SQLite database, and displays it in our application with user authentication and a manual Refresh feature, and Schedule run it. Differences between the database and new scraped data are highlighted for approval before updates and sent to the user via email. Lastly, a log file is created to store logs.

Libraries used for Webscraping and automation
``` BeautifulSoup, Selenium```

## How to Install & Run

 1. Unzip the **Python automation** file.
 2. Create a virtual environment & install dependencies
```
    python -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
```
3. move to the automation folder

   ``` cd automation ```

4. Apply migrations
```
     python  manage.py  makemigrations
     python manage.py migrate
```
5. run server and visit the localhost (something like http://127.0.0.1:8000)
```
    python manage.py runserver
```
## How the Scraper Works

The scraper uses **Selenium + BeautifulSoup** libraries in order to scrape data.

 - With the help of Selenium, we open the target site
 - wait for the target elements to load
 - get source data
 - With the help of BeautifulSoup, extraction of  records (name, age, height, etc.) is accomplished and stored in dict
 - we navigate pages using seleniums `.click` and stops when no more data is found.
 - In the end, we create a list of dicts (json) and return data.

## A breif on Design
There is a `scaper.py` file, Inside the file we have **3 methods**
1. `scrap_data()` -- which returns a `list[dict]` when called. It can only be called by the 
2. `compare_data()` -- which retuns a dict with new data and to_be_deleted data. Note: The `scrap_data()` can only be called by `compare_data()`
3. `apply_changes_to_db()`-- this basically confirms before storing the data into the database.

A CLI command `run_scraper` was created, which calls `compare_data` and `compare_data` calls `scrap_data`. Eventually, printing the compared resulted. if the user confirms the data is stored in db. By doing this, it was ensured that the scraper can be used by both view and CLI.

 

## How the Refresh Button Works

The Refresh button in the UI triggers a backend `Post` request which:

1.  Calls the `compare_data()` which in turn calls `scrap_data()`.
    
2.  After scraping the data is retuned to `compare_data()`. It then compares new data with what’s in the DB. Returns the result.
3. Result is rendered in a modal using bootstrap with _new_ and _deleted_ records. A button is added to confirm. 
4.  After confirmation, the user can apply the changes to update the DB.

## How Differences Are Displayed

-   **New records** are shown in a table inside a modal.
    
-   **Deleted records** are listed separately in the same view.
    
-   No changes are saved until the user confirms.
    
-   The modal uses **HTMX + Bootstrap** for dynamic display.
- If there is **any change** in data an **email** is set to be send to the receipt 

## How Authentication Works
This is quite basic in terms of configurations and design. 

-   Registration and login use Django’s built-in `User` model.
    
-   Views are protected with `@login_required` decorators.
    
-   After registration, users are redirected to login.
    
-   Logout clears the session securely.

## How to Set Up Scheduled Scraping
If we are using windows **Windows Task Scheduler** can be used to implement it. The steps are as follows:
 - Open **Task Scheduler** from Start.  
 - Create a new **Basic Task** call it whatever name example `RunScraper`.  
 - Trigger according to requiremnet: `Daily`, `Every X minutes`, or `On boot`.  
 - Action: **Start a Program**  
 - Program: `python.exe`  
e.g. `C:\Users\YourUser\AppData\Local\Programs\Python\Python312\python.exe`  
 - Arguments:

    manage.py scrape_mostwanted

 - Start in: project root  
e.g. `C:\Users\YourUser\Documents\myproject`
When the time is  set it will automatically run.

 - **Logs** for scheduled runs can be saved to `changesfromScraper.log`.

## DB Schema
|name   |  |
|age      |    
|weight--|
|height--|
|desc  |  |
## 📄 `MostWanted` Table Schema

| Field         | Type           | Description                     |
|---------------|----------------|---------------------------------|
| `id`          | INT (PK)       | Auto-increment primary key.     |
| `name`        | CharField(50)   | Name of the individual.         |
| `age`         | CharField(10)    | Age or DOB.                     |
| `height`      | CharField(10)    | Height detail.                  |
| `weight`      | CharField(10)    | Weight detail.                  |
| `description` | TextField        | Detailed description.           |
| `image_url`   | urlField		   | Link to the image.              |
| `created_at`  | DATETIME       | Timestamp when created.         |

