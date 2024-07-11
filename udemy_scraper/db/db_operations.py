import mysql.connector
import pandas as pd

class DatabaseManager:
    def __init__(self, config):
        self.config = config
        self.conn = None
        self.cursor = None

    def connect(self):
        self.conn = mysql.connector.connect(**self.config)
        self.cursor = self.conn.cursor()

    def disconnect(self):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()

    def insert_course(self, course_data):
        sql = """
        INSERT INTO courses (title, course_url, image_url, description, rating, reviews, instructor, current_price, original_price)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        try:
            self.cursor.execute(sql, course_data)
            self.conn.commit()
            print(f"Inserted '{course_data[0]}' into 'courses' table.")
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            self.conn.rollback()

    def insert_courses_from_csv(self, csv_file):
        df = pd.read_csv(csv_file)
        for index, row in df.iterrows():
            course_data = (
                row['title'],
                row['course_url'],
                row['image_url'],
                row['description'],
                row['rating'],
                row['reviews'],
                row['instructor'],
                row['current_price'],
                row['original_price']
            )
            self.insert_course(course_data)
