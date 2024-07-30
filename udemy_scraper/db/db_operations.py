import mysql.connector
import pandas as pd
import numpy as np

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
        INSERT INTO initial_courses (category, subcategory, title, course_url, image_url, description, rating, reviews, instructor, current_price, original_price)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        try:
            self.cursor.execute(sql, course_data)
            self.conn.commit()
            print(f"Inserted '{course_data[0]}' into 'courses' table.")
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            self.conn.rollback()
            
    def insert_instructor(self, instructor_data):
        sql = """
        INSERT INTO initial_instructor (course_url, instructor_image_urls, instructor_profile_urls)
        VALUES (%s, %s, %s)
        """
        try:
            self.cursor.execute(sql, instructor_data)
            self.conn.commit()
            print(f"Inserted '{instructor_data[0]}' into 'instructor' table.")
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            self.conn.rollback()
            
    def insert_instructor_from_csv(self, csv_file):
        df = pd.read_csv(csv_file)
        for index, row in df.iterrows():
            instructor_data = (
                row['course_url'],
                row['instructor_image_url'],
                row['instructor_profile_url']
            )
            self.insert_instructor(instructor_data)

    def insert_courses_from_csv(self, csv_file):
#category,subcategory,title,course_url,image_url,description,rating,reviews,instructor,current_price,original_price
#category, subcategory, title, course_url, image_url, description, rating, reviews, instructor, current_price, original_price
        df = pd.read_csv(csv_file)
        df = df.replace({np.nan: None})
        for index, row in df.iterrows():
            course_data = (
                row['category'],
                row['subcategory'],
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