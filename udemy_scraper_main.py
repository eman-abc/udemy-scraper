# udemy_scraper_main.py

from udemy_scraper.scraper import UdemyScraper

#path:"C:\Users\user\Downloads\chromedriver-win64\chromedriver-win64\chromedriver.exe"


if __name__ == "__main__":
    chrome_driver_path = r"C:\Users\user\Downloads\chromedriver-win64\chromedriver-win64\chromedriver.exe"
    base_url = 'https://www.udemy.com/courses/search/?&src=ukw'
    categories = [
    "Development",
    "Business",
    "Finance & Accounting",
    "IT & Software",
    "Office Productivity",
    "Personal Development",
    "Design",
    "Marketing",
    "Lifestyle",
    "Photography & Video",
    "Health & Fitness",
    "Music",
    "Teaching & Academics"
    ]
    output_csv = 'itsoftware.csv'
    num_pages = 500  # Set the number of pages you want to scrape

    scraper = UdemyScraper(chrome_driver_path, base_url, output_csv, num_pages, categories)
    start_time = time.time()
    scraper.run()
    end_time = time.time()

    elapsed_time = end_time - start_time
    print(f"Time taken for scraper.run(): {elapsed_time:.2f} seconds")
