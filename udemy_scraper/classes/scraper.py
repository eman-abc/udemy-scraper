import time
import random
from .webdriver_manager import WebDriverManager
from .course_extractor import CourseExtractor
from config.config_manager import ConfigManager
from udemy_scraper_main import db_manager
import urllib
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

class UdemyScraper:
    def __init__(self, driver_path, base_url, output_csv, num_pages, categories, db_manager):
        self.config = ConfigManager(driver_path)
        self.driver_manager = WebDriverManager(self.config)
        self.course_extractor = CourseExtractor(self.driver_manager.driver)
        self.output_csv = output_csv
        self.base_url = base_url
        self.num_pages = num_pages
        self.categories = categories
        self.all_courses = []  # List to store all course data
        self.course_urls1=[]
        self.db_manager=db_manager

    def run(self):
        # try:
        #     for category in self.categories:
        #         print()
        #         # self.scrape_category(category)
        # finally:
        #     # self.save_all_courses_to_csv()
        self.fetch_instructor_data()
        self.driver_manager.close_driver()

    def scrape_category(self, category):
        try:
            for subcategory in self.categories.get(category, []):
                self.num_pages=11
                for page in range(1, self.num_pages + 1):
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
        instructor_data = []
        # course_urls1 = self.read_course_urls_from_csv(r'C:\Users\user\OneDrive\Documents\DMN\selenium udemy\course_urls.csv')
        print("Starting instructor data extraction...")
        db_manager.connect()
        course_urls = db_manager.read_course_urls_from_db()
        # for index in range(1,10):
        #     print(course_urls)
        if not course_urls:
            print("No courses to extract instructors from.")
            return
        try:
            for course_url in course_urls:
                try:
                    instructor_image_urls, instructor_profile_urls,course_desc = self.get_instructor_urls(course_url)
                    if instructor_image_urls != "not available" and instructor_profile_urls != "not available":
                        instructor_data.append({
                            "course_url": course_url,
                            "instructor_image_urls": instructor_image_urls,
                            "instructor_profile_urls": instructor_profile_urls,
                            "course_desc" :course_desc,
                        })
                except Exception as e:
                    print(f"WebDriver exception while processing course URL {course_url}: {e}")
        except Exception as e:
            print(f"WebDriver exception while processing course URL {course_url}: {e}")
        finally:    
            # Write instructor data to CSV
            db_manager.insert_instructor_data(instructor_data)
            print(instructor_data)
            db_manager.disconnect()

    def get_instructor_urls(self, course_url):
        try:
            # Visit course page
            print(course_url)
            self.driver_manager.driver.get(course_url)
            WebDriverWait(self.driver_manager.driver, 30).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '[data-purpose="instructor-bio"]'))
            )
            WebDriverWait(self.driver_manager.driver, 30).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '[data-purpose="safely-set-inner-html:description:description"]'))
            )
            
            # Find instructor bio elements
            ins_elements = self.driver_manager.driver.find_elements(By.CSS_SELECTOR, '[data-purpose="instructor-bio"]')
            
            
            # Initialize lists to store instructors' image and profile URLs
            instructor_image_urls = []
            instructor_profile_urls = []
            
            for ins_element in ins_elements:
                # Parse the HTML of the element
                soup = BeautifulSoup(ins_element.get_attribute('innerHTML'), 'html.parser')
                print(soup)
                
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
                    
            # Extract course description from the entire page source
            description_div = self.driver_manager.driver.find_element(By.CSS_SELECTOR, "div[data-purpose='course-description']")
            description_html = description_div.get_attribute('innerHTML')
            description_soup = BeautifulSoup(description_html, 'html.parser')
            print(description_soup)
            # Attempt to find and extract the description
            description_content = description_soup.get_text(separator="\n").strip()

            if description_content:
                course_desc = description_content
            else:
                course_desc = "Description not found."    
            # Navigate back to the previous search results page
            self.driver_manager.driver.back()
            
            # Concatenate URLs into a single string
            instructor_image_urls_str = ";".join(instructor_image_urls)
            instructor_profile_urls_str = ";".join(instructor_profile_urls)
            print(instructor_image_urls_str, instructor_profile_urls_str,course_desc)
            return instructor_image_urls_str, instructor_profile_urls_str, course_desc
        
        except Exception as e:
            print(f"Error getting instructor URLs: {e}")
            return "not available", "not available","not available"


    #write_courses_to_csv(self, courses, write_header),save_all_courses_to_csv(self),read_course_urls_from_csv moved to course_csv_writer