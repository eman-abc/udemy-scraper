import time
import random
from .webdriver_manager import WebDriverManager
from .course_extractor import CourseExtractor
from .course_csv_writer import CourseCSVWriter
from .config_manager import ConfigManager


class UdemyScraper:
    def __init__(self, driver_path, base_url, output_csv, num_pages):
        self.config = ConfigManager(driver_path)
        self.driver_manager = WebDriverManager(self.config)
        self.course_extractor = CourseExtractor(self.driver_manager.driver)
        self.course_csv_writer = CourseCSVWriter(output_csv)
        self.base_url = base_url
        self.num_pages = num_pages

    def run(self):
        try:
            for page in range(1, self.num_pages + 1):
                try:
                    url = f"{self.base_url}&p={page}"
                    self.driver_manager.load_page(url)
                    courses = self.course_extractor.extract_courses()
                    write_header = (page == 1)  # Write header only for the first page
                    self.course_csv_writer.write_courses_to_csv(courses, write_header)
                    print('scraped page', page)
                    # Add a random delay between 1 and 5 seconds
                    time.sleep(random.uniform(1, 5))
                except:
                    continue
        finally:
            self.driver_manager.close_driver()

# if __name__ == "__main__":
#     chrome_driver_path = r"C:\Users\user\Downloads\chromedriver-win64\chromedriver-win64\chromedriver.exe"
#     base_url = 'https://www.udemy.com/courses/search/?q=python&src=ukw'
#     output_csv = 'udemy_courses_20.csv'
#     num_pages = input("Enter number of page to scrape")  # Set the number of pages you want to scrape

#     scraper = UdemyScraper(chrome_driver_path, base_url, output_csv, num_pages)
#     scraper.run()
