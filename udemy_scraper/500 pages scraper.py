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
