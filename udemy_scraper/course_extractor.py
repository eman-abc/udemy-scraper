from .html_parser import HtmlParser
from .course_printer import CoursePrinter
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


class CourseExtractor:
    def __init__(self, driver):
        self.driver = driver

    def extract_courses(self):
        elements = self.driver.find_elements(By.CSS_SELECTOR, '[class^="course-card-module"]')
        courses = []
        for element in elements:
            try:
                soup = HtmlParser.parse_html(element)
                course_data = self.extract_course_data(soup)
                if course_data:
                    courses.append(course_data)
                    CoursePrinter.print_course_data(course_data)
            except:
                continue
        return courses

    def extract_course_data(self, soup):
        try:
            title_element = soup.select_one('a')
            if title_element:
                # Remove child divs and spans
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
