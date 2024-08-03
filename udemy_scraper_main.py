# udemy_scraper_main.py

from udemy_scraper.classes.scraper import UdemyScraper
from udemy_scraper.db.db_operations import DatabaseManager
from udemy_scraper.config.settings import mysql_config
#path:"C:\Users\user\Downloads\chromedriver-win64\chromedriver-win64\chromedriver.exe"

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

    db_manager = DatabaseManager(mysql_config)
    scraper = UdemyScraper(driver_path, base_url, output_csv, num_pages, categories, db_manager)
    scraper.run()
