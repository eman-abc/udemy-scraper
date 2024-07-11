class CoursePrinter:
    @staticmethod
    def print_course_data(course):
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
