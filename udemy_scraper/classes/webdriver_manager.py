from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import subprocess
import psutil

class WebDriverManager:
    def __init__(self, config):
        self.driver_path = config.driver_path
        self.driver = None
        # Kill all Chrome processes to avoid conflicts
        subprocess.run(["taskkill", "/F", "/IM", "chrome.exe"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # self.kill_specific_chrome_profile("Profile 1")
        self.setup_driver(config.get_driver_options())

    def setup_driver(self, chrome_options):
        service = Service(self.driver_path)
        self.driver = webdriver.Chrome(service=service, options=chrome_options)

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

    def kill_specific_chrome_profile(self, profile_name):
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            if proc.info['name'] == 'chrome.exe' and profile_name in proc.info['cmdline']:
                try:
                    proc.kill()
                except psutil.NoSuchProcess:
                    pass
