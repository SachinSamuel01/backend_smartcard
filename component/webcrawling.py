from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
import time
import random

def random_sleep(min_seconds=1, max_seconds=3):
    time.sleep(random.uniform(min_seconds, max_seconds))

def scrape_content(page):
    return page.evaluate("""
        () => {
            document.querySelectorAll('script, style').forEach(el => el.remove());
            return document.body.innerText;
        }
    """)

def scrape_website(url, max_retries=10, max_sub_links=0):
    attempt= 0
    while attempt < max_retries:
        attempt +=1
        try:
            with sync_playwright() as p:
                # browser = p.chromium.launch(headless=True)  # Set to True for headless mode
                browser = p.webkit.launch(headless=True)
                context = browser.new_context(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
                )
                page = context.new_page()
                
                print(f"Attempt {attempt + 1}: Navigating to {url}")
                page.goto(url, timeout=60000)  # Increase timeout to 60 seconds
                page.wait_for_load_state('networkidle', timeout=60000)
                
                random_sleep()
                
                # Scroll to load dynamic content
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                random_sleep()

                # Find all links on the page
                links = page.query_selector_all('a')
                
                with open('scraped_content1.txt', 'w', encoding='utf-8') as f:
                    # First, scrape and write the main page content
                    main_content = scrape_content(page)
                    return main_content
                    f.write(f"Main URL: {url}\n")
                    f.write(f"Content:\n{main_content}\n")
                    f.write("=" * 80 + "\n\n")

                    

                    sub_links_scraped = 0
                    for link in links:
                        if sub_links_scraped >= max_sub_links:
                            break

                        href = link.get_attribute('href')
                        if href and href.startswith('http'):
                            sub_links_scraped += 1
                            link_text = link.inner_text().strip()

                            # Scrape and write sub-link content
                            try:
                                print(f"Scraping sub-link {sub_links_scraped}: {href}")
                                page.goto(href, timeout=30000)
                                page.wait_for_load_state('networkidle', timeout=30000)
                                random_sleep()
                                sub_content = scrape_content(page)
                                f.write(f"Sub-link {sub_links_scraped}:\n")
                                f.write(f"Text: {link_text}\n")
                                f.write(f"URL: {href}\n")
                                f.write(f"Content:\n{sub_content}\n")
                                f.write("-" * 80 + "\n\n")
                            except Exception as e:
                                print(f"Error scraping sub-link {href}: {str(e)}")
                                f.write(f"Error scraping sub-link {href}: {str(e)}\n")
                                f.write("-" * 80 + "\n\n")

                browser.close()
                print(f"Scraped content saved to 'scraped_content.txt'")
                return True
        except PlaywrightTimeoutError:
            print(f"Timeout error on attempt {attempt + 1}. Retrying...")
            random_sleep(3, 5)
        except Exception as e:
            print(f"Error on attempt {attempt + 1}: {str(e)}")
            random_sleep(3, 5)
    
    print("Max retries reached. Unable to scrape the website.")
    return False




def business_card_research(url):
    research= scrape_website(url)
    return research


# url_test=r"https://in.linkedin.com/in/aman-malviya-839392201"
# url_test1= r'https://in.linkedin.com/in/sachin-samuel-28a5a9260'
# url_test2=r'https://www.linkedin.com/in/sanyam-gupta-bb2a92a4'
# url_test3= r'https://in.linkedin.com/in/anoopvrinda'
# test= business_card_research(url_test3)
# print(test)