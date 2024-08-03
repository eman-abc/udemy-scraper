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
import urllib.parse

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

    def extract_courses(self, category, subcategory):
        elements = self.driver.find_elements(By.CSS_SELECTOR, '[class^="course-card-module"]')
        courses = []
        for element in elements:
            try:
                soup = HtmlParser.parse_html(element)
                course_data = self.extract_course_data(soup, category, subcategory)
                if course_data:
                    courses.append(course_data)
                    self.course_urls.append(course_data['course_url'])  # Store course URL
                    CoursePrinter.print_course_data(course_data)
            except Exception as e:
                print(f"Error extracting course data: {e}")
                continue
        return courses

    def extract_course_data(self, soup, category, subcategory):
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
                    "subcategory": subcategory,
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
        print("Subcategory:", course['subcategory'])
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
        course_urls1 = self.read_course_urls_from_csv(r'C:\Users\user\OneDrive\Documents\DMN\selenium udemy\course_urls.csv')
    
        
        try:
            for course_url in course_urls1:
                try:
                    instructor_image_urls, instructor_profile_urls = self.get_instructor_urls(course_url)
                    if instructor_image_urls != "not available" and instructor_profile_urls != "not available":
                        instructor_data.append({
                            "course_url": course_url,
                            "instructor_image_urls": instructor_image_urls,
                            "instructor_profile_urls": instructor_profile_urls
                        })
                except Exception as e:
                    print(f"WebDriver exception while processing course URL {course_url}: {e}")
                    break
        except Exception as e:
            print(f"WebDriver exception while processing course URL {course_url}: {e}")
        finally:    
            # Write instructor data to CSV
            instructor_csv = r'C:\Users\user\OneDrive\Documents\DMN\selenium udemy\udemy_scraper\instructor_data.csv'
            try:
                with open(instructor_csv, 'a', newline='', encoding='utf-8') as csvfile:
                    fieldnames = ["course_url", "instructor_image_urls", "instructor_profile_urls"]
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    if csvfile.tell() == 0:  # Check if file is empty to write the header
                        writer.writeheader()
                    writer.writerows(instructor_data)
                print(f"Instructor data saved to {instructor_csv}")
            except Exception as e:
                print(f"Error writing instructor data to CSV: {e}")

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
                    
                # course_desc = soup.select_one('div[data-purpose="safely-set-inner-html:description:description"]').get_text(separator='\n')
                # print(course_desc)
            
            # Navigate back to the previous search results page
            self.driver_manager.driver.back()
            
            # Concatenate URLs into a single string
            instructor_image_urls_str = ";".join(instructor_image_urls)
            instructor_profile_urls_str = ";".join(instructor_profile_urls)
            print(instructor_image_urls_str, instructor_profile_urls_str)
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
    driver_path = r"C:\Users\user\OneDrive\Documents\chromedriver-win64\chromedriver.exe"
    base_url = "https://www.udemy.com/courses/search/?"
    output_csv = r"C:\Users\user\OneDrive\Documents\DMN\subcategory_courses.csv"
    num_pages = 100
    categories = {
    "Development": [
        # "Web Development",
        # "Data Science",
        # "Mobile Development",
        # "Programming Languages",
        # "Game Development",
        # "Database Design & Development",
        # # "Software Testing",
        # "Software Engineering",
        # "Development Tools",
        # "No-Code Development"
    ],
    # "Business": [
        # "Entrepreneurship",
        # "Communication",
        # "Management",
        # "Sales",
        # "Strategy",
        # "Operations", starting here 100 pages each
        # "Project Management",
        # "Business Law", 100
        # "Data & Analytics", 100
        # "Home Business",
        # "Human Resources",
        # "Industry",
        # "Media",
    #     "Real Estate",
    #     "Other Business"
    # ],
    # "Finance & Accounting": [
    #     "Accounting & Bookkeeping",
    #     "Cryptocurrency & Blockchain",
    #     "Economics",
    #     "Finance",
    #     "Finance Cert & Exam Prep",
    #     "Investing & Trading",
    #     "Other Finance & Accounting"
    # ],
    # "IT & Software": [
    #     "IT Certification",
    #     "Network & Security",
    #     "Hardware",
    #     "Operating Systems & Servers",
    #     "Other IT & Software"
    # ],
    "Office Productivity": [
    #     "Microsoft",
    #     "Apple",
    #     "Google",
    #     "SAP",
    #     "Oracle",
        # "Other Office Productivity" 
    ],
    # "Personal Development": [
    #     "Personal Transformation",
    #     "Productivity",
    #     "Leadership",
        # "Personal Finance", 
    #     "Career Development",
    #     "Parenting & Relationships",
    #     "Happiness",
    #     "Esoteric Practices",
    #     "Religion & Spirituality",
    #     "Personal Brand Building",
    #     "Creativity",
    #     "Influence",
    #     "Self-Esteem",
    #     "Stress Management",
    #     "Memory & Study Skills",
    #     "Motivation",
    #     "Other Personal Development"
    # ],
    # "Design": [
    #     "Web Design",
    #     "Graphic Design",
        # "Design Tools",
        # "User Experience",
        # "Game Design", till pg 79
        # "3D & Animation",
        # "Fashion Design",
        # "Architectural Design",
        # "Interior Design",
        # "Other Design"
    # ],
    # "Marketing": [
        # "Digital Marketing",
        # "Search Engine Optimization",
        # "Social Media Marketing",
    #     "Branding", 11 PAGES
    #     "Marketing Fundamentals",
    #     "Analytics & Automation",
    #     "Public Relations",
    #     "Advertising",
    #     "Video & Mobile Marketing",
    #     "Content Marketing",
    #     "Growth Hacking",
    #     "Affiliate Marketing",
    #     "Product Marketing",
    #     "Other Marketing"
    # ],
    # "Lifestyle": [
    #     "Arts & Crafts",
    #     "Beauty & Makeup",
    #     "Esoteric Practices",
    #     "Food & Beverage",
    #     "Gaming",
    #     "Home Improvement",
    #     "Pet Care & Training",
    #     "Travel",
    #     "Other Lifestyle"
    # ],
    # "Photography & Video": [
    #     "Digital Photography",
    #     "Photography Tools",
    #     "Photography Fundamentals",
    #     "Portrait Photography", 
        # "Photography Techniques",
        # "Commercial Photography",
        # "Video Design", 
        # "Other Photography & Video"
    # ],
    # "Health & Fitness": [
    #     "Fitness",
    #     "General Health",
    #     "Sports",
    #     "Nutrition",
    #     "Yoga",
    #     "Mental Health",
    #     "Dieting",
    #     "Self Defense",
    #     "Safety & First Aid",
    #     "Dance",
    #     "Meditation",
    #     "Other Health & Fitness"
    # ],
    # "Music": [
    #     "Instruments",
    #     "Music Production",
    #     "Music Fundamentals",
    #     "Vocal",
    #     "Music Software",
    #     "Other Music"
    # ],
    # "Teaching & Academics": [
    #     "Engineering",
    #     "Humanities",
    #     "Math",
    #     "Science",
    #     "Online Education",
    #     "Social Science",
    #     "Language Learning",
    #     "Teacher Training",
    #     "Test Prep",
    #     "Other Teaching & Academics"
    # ]
}


    scraper = UdemyScraper(driver_path, base_url, output_csv, num_pages, categories)
    scraper.run()
