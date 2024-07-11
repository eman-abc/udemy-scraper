import csv

class CourseCSVWriter:
    def __init__(self, filename):
        self.filename = filename

    def write_courses_to_csv(self, courses, write_header):
        keys = courses[0].keys() if courses else []
        with open(self.filename, 'a', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=keys)
            if write_header:
                writer.writeheader()
            writer.writerows(courses)
