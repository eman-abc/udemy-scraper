import time
import random
from .webdriver_manager import WebDriverManager
from .course_extractor import CourseExtractor
from common.course_csv_writer import CourseCSVWriter
from config.config_manager import ConfigManager
import csv
import urllib
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
class UdemyScraper:
    def __init__(self, driver_path, base_url, output_csv, num_pages, categories):
        self.config = ConfigManager(driver_path)
        self.driver_manager = WebDriverManager(self.config)
        self.course_extractor = CourseExtractor(self.driver_manager.driver)
        self.output_csv = output_csv
        self.base_url = base_url
        self.num_pages = num_pages
        self.categories = categories
        self.all_courses = []  # List to store all course data
        self.course_urls1=[]

    def run(self):
        try:
            for category in self.categories:
                print(category)
                self.scrape_category(category)
        finally:
            self.save_all_courses_to_csv()
            #self.fetch_instructor_data()
            self.driver_manager.close_driver()

    def scrape_category(self, category):
        try:
            for subcategory in self.categories.get(category, []):
                self.num_pages=100
                for page in range(5, self.num_pages + 1):
                    try:
                        # URL encode subcategory
                        encoded_subcategory = urllib.parse.quote(subcategory)
                        url = f"{self.base_url}&q={encoded_subcategory}&p={page}"
                        print(f"Scraping URL: {url}")  # Debugging output
                        self.driver_manager.load_page(url)
                        courses = self.course_extractor.extract_courses(category, subcategory)
                        self.all_courses.extend(courses)  # Append courses to the list
                        write_header = (page == 1)  # Write header only for the first page
                        self.write_courses_to_csv(courses, write_header)
                        print('Scraped page', page)
                        # Add a random delay between 1 and 5 seconds
                        time.sleep(random.uniform(1, 5))
                    except Exception as e:
                        print(f"Error scraping page {page} of category {category}: {e}")
                        break
                print(f'Scraped {subcategory} in category:', category)
        except Exception as e:
            print(f"Couldn't get category {category}: {e}")

    def fetch_instructor_data(self):
        try:
            instructor_data = []
            course_urls1=self.read_course_urls_from_csv('instructors.csv')
            for course_url in course_urls1:
                try:
                    instructor_image_urls, instructor_profile_urls = self.get_instructor_urls(course_url)
                    instructor_data.append({
                        "course_url": course_url,
                        "instructor_image_urls": instructor_image_urls,
                        "instructor_profile_urls": instructor_profile_urls
                    })
                except:
                    continue
            
            # Write instructor data to CSV
            instructor_csv = 'instructors1.csv'
            with open(instructor_csv, 'a', newline='', encoding='utf-8') as csvfile:
                fieldnames = ["course_url", "instructor_image_urls", "instructor_profile_urls"]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                #writer.writeheader()
                writer.writerows(instructor_data)
            
            print(f"Instructor data saved to {instructor_csv}")
        
        except Exception as e:
            print(f"Error fetching instructor data: {e}")

    def get_instructor_urls(self, course_url):
        try:
            # Visit course page
            self.driver_manager.driver.get(course_url)
            WebDriverWait(self.driver_manager.driver, 30).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '[data-purpose="instructor-bio"]'))
            )
            
            # Find instructor bio elements
            ins_elements = self.driver_manager.driver.find_elements(By.CSS_SELECTOR, '[data-purpose="instructor-bio"]')
            
            # Initialize lists to store instructors' image and profile URLs
            instructor_image_urls = []
            instructor_profile_urls = []
            
            for ins_element in ins_elements:
                # Parse the HTML of the element
                soup = BeautifulSoup(ins_element.get_attribute('innerHTML'), 'html.parser')
                
                # Extract instructor's image URL
                image_element = soup.select_one('div img')
                instructor_image_url = 'https://www.udemy.com' + image_element['src'] if image_element else None
                if instructor_image_url:
                    instructor_image_urls.append(instructor_image_url)
                
                # Extract instructor's profile URL
                profile_link = soup.select_one('div.ud-heading-lg a[href^="/user/"]')
                instructor_profile_url = 'https://www.udemy.com' + profile_link['href'] if profile_link else None
                if instructor_profile_url:
                    instructor_profile_urls.append(instructor_profile_url)
            
            # Navigate back to the previous search results page
            self.driver_manager.driver.back()
            
            # Concatenate URLs into a single string
            instructor_image_urls_str = ";".join(instructor_image_urls)
            instructor_profile_urls_str = ";".join(instructor_profile_urls)
            
            return instructor_image_urls_str, instructor_profile_urls_str
        
        except Exception as e:
            print(f"Error getting instructor URLs: {e}")
            return "not available", "not available"

    def write_courses_to_csv(self, courses, write_header):
        keys = courses[0].keys() if courses else []
        with open(self.output_csv, 'a', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=keys)
            if write_header:
                writer.writeheader()
            writer.writerows(courses)

    def save_all_courses_to_csv(self):
        keys = self.all_courses[0].keys() if self.all_courses else []
        with open(self.output_csv, 'a', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=keys)
            #writer.writeheader()
            writer.writerows(self.all_courses)
            
    def read_course_urls_from_csv(self, csv_file):
        course_urls1 = []
        try:
            with open(csv_file, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    course_urls1.append(row['course_url'])  # Adjust the field name based on your CSV structure
            print(f"Loaded {len(course_urls1)} course URLs from {csv_file}")
        except Exception as e:
            print(f"Error reading course URLs from {csv_file}: {e}")
        return course_urls1
# if __name__ == "__main__":
#     chrome_driver_path = r"C:\Users\user\Downloads\chromedriver-win64\chromedriver-win64\chromedriver.exe"
#     base_url = 'https://www.udemy.com/courses/search/?q=python&src=ukw'
#     output_csv = 'udemy_courses_20.csv'
#     num_pages = input("Enter number of page to scrape")  # Set the number of pages you want to scrape

#     scraper = UdemyScraper(chrome_driver_path, base_url, output_csv, num_pages)
#     scraper.run()