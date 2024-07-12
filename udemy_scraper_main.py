# udemy_scraper_main.py

from udemy_scraper.classes.scraper import UdemyScraper
from udemy_scraper.db.db_operations import DatabaseManager
from udemy_scraper.config.settings import mysql_config
#path:"C:\Users\user\Downloads\chromedriver-win64\chromedriver-win64\chromedriver.exe"

if __name__ == "__main__":
    chrome_driver_path = r"C:\Users\user\Downloads\chromedriver-win64\chromedriver-win64\chromedriver.exe"
    base_url = 'https://www.udemy.com/courses/search/?q=python&src=ukw'
    output_csv = r"udemy_scraper\data\all_courses_udemy.csv"
    num_pages = input("Enter number of pages to scrape: ")  # Set the number of pages you want to scrape

    scraper = UdemyScraper(chrome_driver_path, base_url, output_csv, int(num_pages))
    scraper.run()
    
    #csv file to import courses from
    courses_csv=r"udemy_scraper\data\all_courses_udemy.csv"
    
    #set up and manage database manager connection
    db_manager= DatabaseManager(mysql_config)
    db_manager.connect()
    db_manager.insert_courses_from_csv(courses_csv)
    db_manager.disconnect()
