# udemy_scraper_main.py

from udemy_scraper.scraper import UdemyScraper

#path:"C:\Users\user\Downloads\chromedriver-win64\chromedriver-win64\chromedriver.exe"

if __name__ == "__main__":
    chrome_driver_path = r"C:\Users\user\Downloads\chromedriver-win64\chromedriver-win64\chromedriver.exe"
    base_url = 'https://www.udemy.com/courses/search/?q=python&src=ukw'
    output_csv = 'udemy_courses_20.csv'
    num_pages = input("Enter number of pages to scrape: ")  # Set the number of pages you want to scrape

    scraper = UdemyScraper(chrome_driver_path, base_url, output_csv, int(num_pages))
    scraper.run()
