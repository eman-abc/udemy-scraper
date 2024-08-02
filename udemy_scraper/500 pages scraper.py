import csv
import time
import random
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
import subprocess
import psutil

class ConfigManager:
    def __init__(self, driver_path):
        self.driver_path = driver_path

    def get_driver_options(self):
        user_data_dir = r"C:\Users\user\AppData\Local\Google\Chrome\User Data"
        profile_dir = "Profile 1"
        chrome_options = Options()
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument(f"--user-data-dir={user_data_dir}")
        chrome_options.add_argument(f"--profile-directory={profile_dir}")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-dev-shm-usage")
        # chrome_options.add_argument("--headless")
        return chrome_options

class WebDriverManager:
    def __init__(self, config):
        self.driver_path = config.driver_path
        self.driver = None
        subprocess.run(["taskkill", "/F", "/IM", "chrome.exe"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.setup_driver(config.get_driver_options())
        self.clear_cache()

    def setup_driver(self, chrome_options):
        service = Service(self.driver_path)
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        
    def clear_cache(self):
        try:
            # Access Chrome DevTools Protocol
            self.driver.execute_cdp_cmd('Network.clearBrowserCache', {})
            print("Cache cleared successfully.")
        except Exception as e:
            print(f"Error clearing cache: {e}")

    def load_page(self, url):
        self.driver.get(url)
        WebDriverWait(self.driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '[class^="course-card-module"]'))
        )
        WebDriverWait(self.driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '[data-purpose="course-price-text"] span span'))
        )

    def close_driver(self):
        if self.driver:
            self.driver.quit()

class HtmlParser:
    @staticmethod
    def parse_html(element):
        inner_html = element.get_attribute('innerHTML')
        return BeautifulSoup(inner_html, 'html.parser')

    @staticmethod
    def get_element_text(soup, selector, multiple=False):
        if multiple:
            elements = soup.select(selector)
            return [element.text.strip() for element in elements] if elements else None
        else:
            element = soup.select_one(selector)
            return element.text.strip() if element else None

class CourseExtractor:
    def __init__(self, driver):
        self.driver = driver
        self.course_urls = []  # List to store course URLs

    def extract_courses(self, category):
        elements = self.driver.find_elements(By.CSS_SELECTOR, '[class^="course-card-module"]')
        courses = []
        for element in elements:
            try:
                soup = HtmlParser.parse_html(element)
                course_data = self.extract_course_data(soup, category)
                if course_data:
                    courses.append(course_data)
                    self.course_urls.append(course_data['course_url'])  # Store course URL
                    CoursePrinter.print_course_data(course_data)
            except Exception as e:
                print(f"Error extracting course data: {e}")
                continue
        return courses

    def extract_course_data(self, soup, category):
        try:
            title_element = soup.select_one('a')
            if title_element:
                for tag in title_element.find_all(['div', 'span']):
                    tag.decompose()
                title = title_element.text.strip()
            else:
                title = None
                
            url_element = soup.select_one('[data-purpose="course-title-url"] a')
            course_url = 'https://www.udemy.com' + url_element['href'] if url_element else None
            image_element = soup.select_one('img')
            image_url = image_element['src'] if image_element else None
            description = HtmlParser.get_element_text(soup, '[data-purpose="safely-set-inner-html:course-card:course-headline"]')
            rating = HtmlParser.get_element_text(soup, '[data-purpose="rating-number"]')
            reviews = HtmlParser.get_element_text(soup, '[aria-label][class*="reviews-text"]')
            reviews = reviews if reviews else None
            instructor = HtmlParser.get_element_text(soup, '[data-purpose="safely-set-inner-html:course-card:visible-instructors"]')
            instructor = instructor if instructor else None
            
            current_price = self.wait_for_element_text('[data-purpose="course-price-text"] span span')
            original_price = self.wait_for_element_text('[data-purpose="course-old-price-text"] span s span')
            
            if title and course_url and description and rating and reviews and image_url:
                return {
                    "category": category,
                    "title": title,
                    "course_url": course_url,
                    "image_url": image_url,
                    "description": description,
                    "rating": rating,
                    "reviews": reviews,
                    "instructor": instructor,
                    "current_price": current_price,
                    "original_price": original_price
                }
        except Exception as e:
            print(f"Error extracting data: {e}")
            return None

    def wait_for_element_text(self, selector):
        try:
            element = WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, selector))
            )
            return element.text
        except TimeoutException:
            return None

class CoursePrinter:
    @staticmethod
    def print_course_data(course):
        print("Category:", course['category'])
        print("Course Title:", course['title'])
        print("URL:", course['course_url'])
        print("Image URL:", course['image_url'])
        print("Description:", course['description'])
        print("Rating:", course['rating'])
        print("Reviews:", course['reviews'])
        print("Instructor:", course['instructor'])
        print("Current Price:", course['current_price'])
        print("Original Price:", course['original_price'])
        print()

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
        if category in ["Development", "Business", "Health & Fitness", "Lifestyle", "Finance & Accounting", "IT & Software", "Personal Development", "Design", "Marketing"]:
            num_pages = 625
        elif category == "Office Productivity":
            num_pages = 467
        elif category == "Photography & Video":
            num_pages = 265
        elif category == "Music":
            num_pages = 389
        else:
            num_pages = 625
        try:
            for page in range(1, self.num_pages + 1):
                try:
                    url = f"{self.base_url}&q={category}&p={page}"
                    self.driver_manager.load_page(url)
                    courses = self.course_extractor.extract_courses(category)
                    self.all_courses.extend(courses)  # Append courses to the list
                    write_header = (page == 1)  # Write header only for the first page
                    self.write_courses_to_csv(courses, write_header)
                    print('scraped page', page)
                    # Add a random delay between 1 and 5 seconds
                    time.sleep(random.uniform(1, 5))
                except Exception as e:
                    print(f"Error scraping page {page} of category {category}: {e}")
                    break
            print('scraped category:', category)
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


if __name__ == "__main__":
    driver_path = r"C:\Users\user\Downloads\chromedriver-win64\chromedriver-win64\chromedriver.exe"
    base_url = "https://www.udemy.com/courses/search/?"
    output_csv = "courses.csv"
    num_pages = 500
    categories = [
        # "Development",
        # "Business",
        # "Finance & Accounting",
        # "IT & Software",
        # "Office Productivity",
        # "Personal Development",
        # "Design",
        # "Marketing",
        # "Lifestyle",
        # "Photography & Video",
        # "Health & Fitness",
        "Music",
        "Teaching & Academics"
    ]

    scraper = UdemyScraper(driver_path, base_url, output_csv, num_pages, categories)
    scraper.run()

# import csv
# import time
# import random
# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.common.exceptions import TimeoutException
# from bs4 import BeautifulSoup
# import subprocess
# import psutil

# class ConfigManager:
#     def __init__(self, driver_path):
#         self.driver_path = driver_path

#     def get_driver_options(self):
#         # Define the path to your Chrome profile
#         user_data_dir = r"C:\Users\user\AppData\Local\Google\Chrome\User Data"
#         profile_dir = "Profile 1"
#         chrome_options = Options()
#         chrome_options.add_argument("--disable-gpu")
#         chrome_options.add_argument("--no-sandbox")
#         chrome_options.add_argument(f"--user-data-dir={user_data_dir}")
#         chrome_options.add_argument(f"--profile-directory={profile_dir}")
#         #chrome_options.add_argument("--remote-debugging-port=9222")  # Add this line to avoid the DevToolsActivePort error
#         chrome_options.add_argument("--disable-extensions")
#         chrome_options.add_argument("--disable-dev-shm-usage")
#         #chrome_options.add_argument("--headless")
#         return chrome_options

# class WebDriverManager:
#     def __init__(self, config):
#         self.driver_path = config.driver_path
#         self.driver = None
#         # Kill all Chrome processes to avoid conflicts
#         subprocess.run(["taskkill", "/F", "/IM", "chrome.exe"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
#         #self.kill_specific_chrome_profile("Profile 1")
#         self.setup_driver(config.get_driver_options())

#     def setup_driver(self, chrome_options):
#         service = Service(self.driver_path)
#         self.driver = webdriver.Chrome(service=service, options=chrome_options)

#     def load_page(self, url):
#         self.driver.get(url)
#         WebDriverWait(self.driver, 30).until(
#             EC.presence_of_element_located((By.CSS_SELECTOR, '[class^="course-card-module"]'))
#         )
#         WebDriverWait(self.driver, 30).until(
#             EC.presence_of_element_located((By.CSS_SELECTOR, '[data-purpose="course-price-text"] span span'))
#         )

#     def close_driver(self):
#         if self.driver:
#             self.driver.quit()
            
#     def kill_specific_chrome_profile(self, profile_name):
#         for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
#             if proc.info['name'] == 'chrome.exe' and profile_name in proc.info['cmdline']:
#                 try:
#                     proc.kill()
#                 except psutil.NoSuchProcess:
#                     pass

# class HtmlParser:
#     @staticmethod
#     def parse_html(element):
#         inner_html = element.get_attribute('innerHTML')
#         return BeautifulSoup(inner_html, 'html.parser')

#     @staticmethod
#     def get_element_text(soup, selector, multiple=False):
#         if multiple:
#             elements = soup.select(selector)
#             return [element.text.strip() for element in elements] if elements else None
#         else:
#             element = soup.select_one(selector)
#             return element.text.strip() if element else None

# class CourseExtractor:
#     def __init__(self, driver):
#         self.driver = driver

#     def extract_courses(self):
#         elements = self.driver.find_elements(By.CSS_SELECTOR, '[class^="course-card-module"]')
#         courses = []
#         for element in elements:
#             try:
#                 soup = HtmlParser.parse_html(element)
#                 course_data = self.extract_course_data(soup)
#                 if course_data:
#                     courses.append(course_data)
#                     CoursePrinter.print_course_data(course_data)
#             except:
#                 continue
#         return courses
    

#     def extract_course_data(self, soup):
#         try:
#             title_element = soup.select_one('a')
#             if title_element:
#                 # Remove child divs and spans
#                 for tag in title_element.find_all(['div', 'span']):
#                     tag.decompose()
#                 title = title_element.text.strip()
#             else:
#                 title = None
                
#             url_element = soup.select_one('[data-purpose="course-title-url"] a')
#             course_url = 'https://www.udemy.com' + url_element['href'] if url_element else None
#             image_element = soup.select_one('img')
#             image_url = image_element['src'] if image_element else None
#             description = HtmlParser.get_element_text(soup, '[data-purpose="safely-set-inner-html:course-card:course-headline"]')
#             rating = HtmlParser.get_element_text(soup, '[data-purpose="rating-number"]')
#             reviews = HtmlParser.get_element_text(soup, '[aria-label][class*="reviews-text"]')
#             reviews = reviews if reviews else None
#             # .replace('(', '').replace(')', '').replace(',', '')
#             instructor = HtmlParser.get_element_text(soup, '[data-purpose="safely-set-inner-html:course-card:visible-instructors"]')
#             instructor = instructor if instructor else None

#             current_price = self.wait_for_element_text('[data-purpose="course-price-text"] span span')
#             original_price = self.wait_for_element_text('[data-purpose="course-old-price-text"] span s span')

#             if title and course_url and description and rating and reviews and image_url:
#                 return {
#                     "title": title,
#                     "course_url": course_url,
#                     "image_url": image_url,
#                     "description": description,
#                     "rating": rating,
#                     "reviews": reviews,
#                     "instructor": instructor,
#                     "current_price": current_price,
#                     "original_price": original_price
#                 }
#         except Exception as e:
#             print(f"Error extracting data: {e}")
#             return None

#     def wait_for_element_text(self, selector):
#         try:
#             element = WebDriverWait(self.driver, 20).until(
#                 EC.presence_of_element_located((By.CSS_SELECTOR, selector))
#             )
#             return element.text
#         except TimeoutException:
#             return None

# class CoursePrinter:
#     @staticmethod
#     def print_course_data(course):
#         print("Course Title:", course['title'])
#         print("URL:", course['course_url'])
#         print("Image URL:", course['image_url'])
#         print("Description:", course['description'])
#         print("Rating:", course['rating'])
#         print("Reviews:", course['reviews'])
#         print("Instructor:", course['instructor'])
#         print("Current Price:", course['current_price'])
#         print("Original Price:", course['original_price'])
#         print()

# class CourseCSVWriter:
#     def __init__(self, filename):
#         self.filename = filename

#     def write_courses_to_csv(self, courses, write_header):
#         keys = courses[0].keys() if courses else []
#         with open(self.filename, 'a', newline='', encoding='utf-8') as csvfile:
#             writer = csv.DictWriter(csvfile, fieldnames=keys)
#             if write_header:
#                 writer.writeheader()
#             writer.writerows(courses)

# class UdemyScraper:
#     def __init__(self, driver_path, base_url, output_csv, num_pages):
#         self.config = ConfigManager(driver_path)
#         self.driver_manager = WebDriverManager(self.config)
#         self.course_extractor = CourseExtractor(self.driver_manager.driver)
#         self.course_csv_writer = CourseCSVWriter(output_csv)
#         self.base_url = base_url
#         self.num_pages = num_pages

#     def run(self):
#         try:
#             for page in range(1, self.num_pages + 1):
#                 try:
#                     url = f"{self.base_url}&p={page}"
#                     self.driver_manager.load_page(url)
#                     courses = self.course_extractor.extract_courses()
#                     write_header = (page == 1)  # Write header only for the first page
#                     self.course_csv_writer.write_courses_to_csv(courses, write_header)
#                     print('scraped page', page)
#                     # Add a random delay between 1 and 5 seconds
#                     time.sleep(random.uniform(1, 5))
#                 except:
#                     continue
#         finally:
#             self.driver_manager.close_driver()

# if __name__ == "__main__":
#     chrome_driver_path = r"C:\Users\user\Downloads\chromedriver-win64\chromedriver-win64\chromedriver.exe"
#     base_url = 'https://www.udemy.com/courses/search/?q=python&src=ukw'
#     output_csv = 'udemy_courses_20.csv'
#     num_pages = 20  # Set the number of pages you want to scrape

#     scraper = UdemyScraper(chrome_driver_path, base_url, output_csv, num_pages)
#     scraper.run()
