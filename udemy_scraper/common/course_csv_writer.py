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
