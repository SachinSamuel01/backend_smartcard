import warnings
warnings.filterwarnings("ignore")


# import requests
# from bs4 import BeautifulSoup
# from urllib.parse import urljoin, urlparse
# from scrapy import Spider, Request
# import re

# dict={}

# link_lst=[]


# def clean_text(text: str) -> str:
#     # Step 1: Remove leading and trailing whitespace
#     text = text.strip()
    
#     # Step 2: Replace multiple consecutive newline characters with a single newline
#     text = re.sub(r'\n+', '\n', text)
    
#     # Step 3: Remove lines that are entirely whitespace or contain no meaningful content
#     lines = text.split('\n')
#     meaningful_lines = [line for line in lines if line.strip()]
    
#     # Join the meaningful lines back together
#     cleaned_text = '\n'.join(meaningful_lines)
    
#     return cleaned_text


# html_text= requests.get("https://store.nvidia.com/en-us").text
# soup = BeautifulSoup(html_text, 'lxml')
# text= soup.get_text()

# text= clean_text(text)
# # print(text)

# for link in soup.find_all('a'):
#     print(type(link.get('href')))



# def get_text(link):
#     html_text= requests.get(link).text
#     soup = BeautifulSoup(html_text, 'lxml')
#     text= soup.get_text()
    
#     return text


# def 


import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import os

def scrape_page(url, visited):
    if url in visited:
        return ""

    visited.add(url)
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Failed to retrieve {url}: {e}")
        return ""

    soup = BeautifulSoup(response.content, 'html.parser')
    text = soup.get_text(separator='\n', strip=True)
    
    print(visited)

    print(f'no. of links {len(visited)}')

    
    
    
    # Find and process all sub-links
    for link in soup.find_all('a', href=True):
        href = link.get('href')
        if len(visited)>=20:
            return text
        sub_url = urljoin(url, href)
        if (urlparse(sub_url).netloc == urlparse(url).netloc):
            text += "\n\n" + scrape_page(sub_url, visited)

    return text

def scrape_and_save_links(links, collection_dir):
    visited = set()
    for index, link in enumerate(links):
        text_content = scrape_page(link, visited)
        file_path = os.path.join(collection_dir, f"scraped_content_{index + 1}.txt")
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(text_content)

# if __name__ == "__main__":
#     start_url = 'https://store.nvidia.com/en-us'  # Replace with the starting URL
#     output_file = r'D:\projects\VS_code\internships\smartcard_python\uploads\filesUploads\1234.txt'
#     main(start_url, output_file)
#     print(f"Scraping completed. Content saved to {output_file}")



# from selenium import webdriver
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from bs4 import BeautifulSoup
# import time
# import re
# import logging

# # Set up logging
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# def setup_driver():
#     chrome_options = Options()
#     chrome_options.add_argument("--headless")
#     chrome_options.add_argument("--disable-gpu")
#     chrome_options.add_argument("--no-sandbox")
#     chrome_options.add_argument("--disable-dev-shm-usage")
#     chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    
#     # Suppress logging
#     chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
    
#     service = Service('path/to/chromedriver')  # Specify the path to your chromedriver
#     driver = webdriver.Chrome(service=service, options=chrome_options)
#     return driver

# def scrape_website(url):
#     driver = setup_driver()
#     try:
#         logger.info(f"Navigating to {url}")
#         driver.get(url)

#         logger.info("Waiting for page to load")
#         WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

#         logger.info("Scrolling page")
#         driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
#         time.sleep(5)

#         logger.info("Parsing page source")
#         page_source = driver.page_source
#         soup = BeautifulSoup(page_source, 'html.parser')

#         logger.info("Finding product links")
#         links = soup.find_all('a', class_='product-tile__link')
#         logger.info(f"Found {len(links)} product links")

#         result = []
#         for link in links:
#             href = link.get('href')
#             if href:
#                 link_data = {
#                     'text': link.find('h2', class_='product-tile__title').text.strip() if link.find('h2', class_='product-tile__title') else '',
#                     'link': url + href if href.startswith('/') else href,
#                     'description': link.find('p', class_='product-tile__description').text.strip() if link.find('p', class_='product-tile__description') else '',
#                     'price': link.find('span', class_='product-price__amount').text.strip() if link.find('span', class_='product-price__amount') else ''
#                 }
#                 logger.info(f"Scraped product: {link_data['text']}")
#                 result.append(link_data)

#         return result

#     except Exception as e:
#         logger.error(f"An error occurred: {str(e)}")
#         return []

#     finally:
#         logger.info("Closing browser")
#         driver.quit()

# # Example usage
# url = "https://store.nvidia.com/en-us/"
# scraped_data = scrape_website(url)

# if scraped_data:
#     logger.info("Printing results")
#     for item in scraped_data:
#         print(f"Product: {item['text']}")
#         print(f"Link: {item['link']}")
#         print(f"Description: {item['description']}")
#         print(f"Price: {item['price']}")
#         print("---")
# else:
#     logger.warning("No data was scraped")