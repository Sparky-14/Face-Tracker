import time
import json
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class LinkedInScraper:
    def __init__(self, headless=False):
        """
        Initialize the LinkedIn scraper
        
        Args:
            headless (bool): Whether to run browser in headless mode
        """
        self.driver = None
        self.wait = None
        self.scraped_posts = []
        self.setup_driver(headless)
    
    def setup_driver(self, headless=False):
        """Setup Chrome WebDriver with necessary options"""
        chrome_options = Options()
        
        if headless:
            chrome_options.add_argument("--headless")
        
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        
        # Install and setup Chrome driver
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.wait = WebDriverWait(self.driver, 10)
        
        print("✅ Browser setup complete")
    
    def login(self, email=None, password=None):
        """
        Login to LinkedIn
        
        Args:
            email (str): LinkedIn email (can also be set via environment variable LINKEDIN_EMAIL)
            password (str): LinkedIn password (can also be set via environment variable LINKEDIN_PASSWORD)
        """
        # Get credentials from parameters or environment variables
        email = email or os.getenv('LINKEDIN_EMAIL')
        password = password or os.getenv('LINKEDIN_PASSWORD')
        
        if not email or not password:
            print("❌ Please provide email and password or set LINKEDIN_EMAIL and LINKEDIN_PASSWORD environment variables")
            return False
        
        try:
            print("🔐 Starting LinkedIn login...")
            self.driver.get("https://www.linkedin.com/login")
            
            # Wait for login form and fill credentials
            email_field = self.wait.until(EC.presence_of_element_located((By.ID, "username")))
            password_field = self.driver.find_element(By.ID, "password")
            
            email_field.send_keys(email)
            password_field.send_keys(password)
            
            # Click login button
            login_button = self.driver.find_element(By.XPATH, "//button[@type='submit']")
            login_button.click()
            
            # Wait for successful login (check for feed or dashboard)
            try:
                self.wait.until(EC.presence_of_element_located((By.XPATH, "//a[contains(@href, '/feed/')]")))
                print("✅ Successfully logged in to LinkedIn")
                return True
            except TimeoutException:
                print("⚠️ Login might have failed or requires additional verification")
                return False
                
        except Exception as e:
            print(f"❌ Login failed: {str(e)}")
            return False
    
    def search_posts(self, query, filters=None):
        """
        Search for posts on LinkedIn
        
        Args:
            query (str): Search query
            filters (dict): Optional filters (e.g., {'content_type': 'posts'})
        """
        try:
            print(f"🔍 Searching for: '{query}'")
            
            # Navigate to search
            search_url = f"https://www.linkedin.com/search/results/content/?keywords={query.replace(' ', '%20')}"
            self.driver.get(search_url)
            
            # Wait for search results to load
            time.sleep(3)
            
            # Apply filters if needed (focus on posts)
            try:
                posts_filter = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Posts')]")))
                posts_filter.click()
                time.sleep(2)
                print("✅ Applied posts filter")
            except:
                print("⚠️ Could not apply posts filter, continuing with general results")
            
            return True
            
        except Exception as e:
            print(f"❌ Search failed: {str(e)}")
            return False
    
    def scroll_and_load_posts(self, scroll_count=5, scroll_pause=2):
        """
        Scroll down to load more posts
        
        Args:
            scroll_count (int): Number of times to scroll
            scroll_pause (float): Pause between scrolls in seconds
        """
        print(f"📜 Scrolling to load more posts...")
        
        for i in range(scroll_count):
            # Scroll to bottom
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(scroll_pause)
            
            print(f"   Scrolled {i+1}/{scroll_count} times")
        
        print("✅ Finished scrolling")
    
    def scrape_posts(self, max_posts=50):
        """
        Scrape post content and links from the current page
        
        Args:
            max_posts (int): Maximum number of posts to scrape
        """
        print(f"🎯 Starting to scrape posts (max: {max_posts})")
        
        try:
            # Wait for posts to load
            time.sleep(3)
            
            # Find all post containers
            posts = self.driver.find_elements(By.XPATH, "//div[@data-id]//div[contains(@class, 'feed-shared-update-v2')]")
            
            if not posts:
                # Try alternative selector
                posts = self.driver.find_elements(By.XPATH, "//div[contains(@class, 'search-results-container')]//div[contains(@class, 'update-components-text')]")
            
            print(f"Found {len(posts)} posts on page")
            
            scraped_count = 0
            for i, post in enumerate(posts[:max_posts]):
                if scraped_count >= max_posts:
                    break
                    
                try:
                    post_data = self.extract_post_data(post, i)
                    if post_data:
                        self.scraped_posts.append(post_data)
                        scraped_count += 1
                        print(f"   ✅ Scraped post {scraped_count}/{max_posts}")
                        
                except Exception as e:
                    print(f"   ⚠️ Failed to scrape post {i+1}: {str(e)}")
                    continue
            
            print(f"🎉 Successfully scraped {scraped_count} posts")
            return scraped_count
            
        except Exception as e:
            print(f"❌ Error during scraping: {str(e)}")
            return 0
    
    def extract_post_data(self, post_element, index):
        """
        Extract data from a single post element
        
        Args:
            post_element: Selenium WebElement of the post
            index (int): Post index for identification
        """
        try:
            post_data = {
                'index': index,
                'content': '',
                'author': '',
                'post_link': '',
                'likes': '',
                'comments': '',
                'timestamp': '',
                'scraped_at': time.strftime('%Y-%m-%d %H:%M:%S')
            }
            
            # Extract post content
            try:
                content_elements = post_element.find_elements(By.XPATH, ".//span[contains(@class, 'break-words')]")
                if content_elements:
                    post_data['content'] = content_elements[0].text.strip()
                else:
                    # Try alternative selector
                    content_elements = post_element.find_elements(By.XPATH, ".//div[contains(@class, 'feed-shared-text')]")
                    if content_elements:
                        post_data['content'] = content_elements[0].text.strip()
            except:
                pass
            
            # Extract author name
            try:
                author_elements = post_element.find_elements(By.XPATH, ".//span[contains(@class, 'feed-shared-actor__name')]")
                if author_elements:
                    post_data['author'] = author_elements[0].text.strip()
                else:
                    # Try alternative selector
                    author_elements = post_element.find_elements(By.XPATH, ".//a[contains(@class, 'app-aware-link')]//span")
                    if author_elements:
                        post_data['author'] = author_elements[0].text.strip()
            except:
                pass
            
            # Extract post link
            try:
                link_elements = post_element.find_elements(By.XPATH, ".//a[contains(@href, '/feed/update/')]")
                if link_elements:
                    post_data['post_link'] = link_elements[0].get_attribute('href')
                else:
                    # Try to find any post link
                    link_elements = post_element.find_elements(By.XPATH, ".//a[contains(@href, 'linkedin.com')]")
                    if link_elements:
                        post_data['post_link'] = link_elements[0].get_attribute('href')
            except:
                pass
            
            # Extract engagement metrics
            try:
                # Likes
                likes_elements = post_element.find_elements(By.XPATH, ".//span[contains(@class, 'social-counts-reactions')]")
                if likes_elements:
                    post_data['likes'] = likes_elements[0].text.strip()
                
                # Comments
                comments_elements = post_element.find_elements(By.XPATH, ".//button[contains(@aria-label, 'comment')]")
                if comments_elements:
                    post_data['comments'] = comments_elements[0].get_attribute('aria-label')
            except:
                pass
            
            return post_data if post_data['content'] or post_data['author'] else None
            
        except Exception as e:
            print(f"Error extracting post data: {str(e)}")
            return None
    
    def save_data(self, filename=None, format='csv'):
        """
        Save scraped data to file
        
        Args:
            filename (str): Output filename
            format (str): Output format ('csv', 'json', 'excel')
        """
        if not self.scraped_posts:
            print("❌ No data to save")
            return False
        
        timestamp = time.strftime('%Y%m%d_%H%M%S')
        
        if not filename:
            filename = f"linkedin_posts_{timestamp}"
        
        try:
            if format.lower() == 'csv':
                df = pd.DataFrame(self.scraped_posts)
                df.to_csv(f"{filename}.csv", index=False, encoding='utf-8')
                print(f"✅ Data saved to {filename}.csv")
                
            elif format.lower() == 'json':
                with open(f"{filename}.json", 'w', encoding='utf-8') as f:
                    json.dump(self.scraped_posts, f, indent=2, ensure_ascii=False)
                print(f"✅ Data saved to {filename}.json")
                
            elif format.lower() == 'excel':
                df = pd.DataFrame(self.scraped_posts)
                df.to_excel(f"{filename}.xlsx", index=False)
                print(f"✅ Data saved to {filename}.xlsx")
            
            return True
            
        except Exception as e:
            print(f"❌ Error saving data: {str(e)}")
            return False
    
    def run_full_scraping(self, email, password, query, max_posts=50, scroll_count=5):
        """
        Run the complete scraping process
        
        Args:
            email (str): LinkedIn email
            password (str): LinkedIn password
            query (str): Search query
            max_posts (int): Maximum posts to scrape
            scroll_count (int): Number of scrolls to perform
        """
        print("🚀 Starting LinkedIn scraping automation...")
        
        # Step 1: Login
        if not self.login(email, password):
            print("❌ Failed to login. Stopping automation.")
            return False
        
        # Step 2: Search
        if not self.search_posts(query):
            print("❌ Failed to search. Stopping automation.")
            return False
        
        # Step 3: Scroll to load more posts
        self.scroll_and_load_posts(scroll_count)
        
        # Step 4: Scrape posts
        scraped_count = self.scrape_posts(max_posts)
        
        if scraped_count > 0:
            # Step 5: Save data
            self.save_data(format='csv')
            self.save_data(format='json')
            print(f"🎉 Automation completed! Scraped {scraped_count} posts")
            return True
        else:
            print("❌ No posts were scraped")
            return False
    
    def close(self):
        """Close the browser"""
        if self.driver:
            self.driver.quit()
            print("🔒 Browser closed")


# Example usage
if __name__ == "__main__":
    # Configuration
    SEARCH_QUERY = "artificial intelligence"  # Change this to your search query
    MAX_POSTS = 30
    SCROLL_COUNT = 3
    
    # Initialize scraper
    scraper = LinkedInScraper(headless=False)  # Set to True for headless mode
    
    try:
        # Option 1: Use environment variables (recommended)
        # Set LINKEDIN_EMAIL and LINKEDIN_PASSWORD in your .env file
        scraper.run_full_scraping(
            email=None,  # Will use environment variable
            password=None,  # Will use environment variable
            query=SEARCH_QUERY,
            max_posts=MAX_POSTS,
            scroll_count=SCROLL_COUNT
        )
        
        # Option 2: Direct credentials (not recommended for security)
        # scraper.run_full_scraping(
        #     email="your-email@example.com",
        #     password="your-password",
        #     query=SEARCH_QUERY,
        #     max_posts=MAX_POSTS,
        #     scroll_count=SCROLL_COUNT
        # )
        
    except KeyboardInterrupt:
        print("\n⏹️ Scraping interrupted by user")
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
    finally:
        scraper.close()