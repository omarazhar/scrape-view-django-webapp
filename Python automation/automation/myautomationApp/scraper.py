from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
import logging
from selenium.common.exceptions import NoSuchElementException

from myautomationApp.models import MostWanted
from django.db import transaction

def scrap_data() -> list[dict]:

    url = "https://www.edmontonpolice.ca/home/crimefiles/edmontonsmostwanted.aspx"

    op = Options()
    op.add_argument("--headless=new")
    driver = webdriver.Chrome(options=op)
    driver.get(url)

    # ensure the page is fully loaded
    wait = WebDriverWait(driver, timeout=10)

    max_page = 5
    page_num = 1

    scraped_data = []
    logger = logging.getLogger(__name__)


    while (page_num < max_page):  # coudl have used True, using it for avoiding the risk of infinite loop
        print(f"Scraping page {page_num}\n\n")

    # wait till the class to be scraped is loaded
        wait.until(
        expected_conditions.presence_of_all_elements_located((By.CLASS_NAME, "mostWanted"))
        )
    #get page code and store needed data
        page_sourse_data = driver.page_source
        soup_data = BeautifulSoup(page_sourse_data, 'html.parser')
        criminals = soup_data.find_all("div", class_="mostWanted")

    # loopint and scraping the page content
        for criminal in criminals:
            name = criminal.find("h2").text.strip()
            name = " ".join(name.split())

            relative_img_url = criminal.find("img")["src"].replace("../", "")
            abs_img_url = "https://www.edmontonpolice.ca/" + relative_img_url

            age = criminal.find("div", class_="age").text.strip().replace("DOB/Age:", "")
            height = criminal.find("div", class_="height").text.strip().replace("Height:", "")
            weight = criminal.find("div", class_="weight").text.strip().replace("Weight:", "")
            description = criminal.find("div", class_="description").text.strip()

            temp_dict = {
                'name': name,
                'age': age,
                'height': height,
                'weight': weight,
                'description': description,
                'image_url': abs_img_url
            }
            scraped_data.append(temp_dict)

    # try finding the next button using ID
        try:
            next_page = driver.find_element(By.ID, "phmain_0_phcontent_0_grdPager_nextButton")
        except NoSuchElementException:
            print("Unable to find ID")
            logger.exception("Unable to find ID.....Scraping failed")
            driver.quit()
            return []

        # check if this is the last page
        if "aspNetDisabled" in next_page.get_attribute("class"):
            print("This was the last page Scrapd")
            break


        #try to click the next button and wait until it is loaded for scraping
        try:
            # js for ensuring if the view is on screen to click
            driver.execute_script("arguments[0].scrollIntoView(true);", next_page)
            next_page.click()
            page_num += 1
            
            # wait for page to update:
            WebDriverWait(driver, 10).until(expected_conditions.staleness_of(next_page))
        except Exception as e:
            print(f"Click failed or wait failed: {e}")
            logger.exception(f"Click failed or wait failed: {e}D.....Scraping failed")
            driver.quit()
            return []

    driver.quit()
    return scraped_data


def compare_data() -> dict:
        scraped = scrap_data()
        
        # get desired field for comparison
        db_fields = ['name', 'age', 'height', 'weight', 'description', 'image_url']
        db_data = list(MostWanted.objects.all().values(*db_fields))

        changes = {
            'new': [],
            'deleted': []
        }
    # creating set for better efficiency in comparing large datasets
        scraped_set = {tuple(item.items()) for item in scraped}
        db_set = {tuple(item.items()) for item in db_data}

        changes = {
            'new': [dict(t) for t in scraped_set - db_set],       # In scrape, not in DB
            'deleted': [dict(t) for t in db_set - scraped_set]    # In DB, not in scrape
        }

        return changes

def apply_changes_to_db(changes):

    #Save changes if confirmed
    try:
        with transaction.atomic():
            # Save new records
            if changes['new']:
                MostWanted.objects.bulk_create(
                    [MostWanted(**data) for data in changes['new']]
                )
                print("Successfully saved in db")
            
        #Delete if confirmed only records matching ALL specified fields
            if changes['deleted']:
                for record in changes['deleted']:
                    MostWanted.objects.filter(
                        name=record['name'],
                        age=record['age'],
                        height=record['height'],
                        weight=record['weight'],
                        description=record['description'],
                        image_url=record['image_url']
                    ).delete()
                print("Successfully deleted from db")
            return True
    
    except Exception as e:
        print(f"Error saving changes: {str(e)}")
        logging.exception(f"Error saving changes: {str(e)}")

