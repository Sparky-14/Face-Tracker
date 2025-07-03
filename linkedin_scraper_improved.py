import os
import time
import csv
import json
import pyperclip
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class LinkedInPostScraper:
    def __init__(self, headless=False, max_wait_time=15):
        """
        Initialize the LinkedIn Post Scraper
        
        Args:
            headless (bool): Run browser in headless mode
            max_wait_time (int): Maximum wait time for elements
        """
        self.USERNAME = os.getenv('LINKEDIN_EMAIL', "")
        self.PASSWORD = os.getenv('LINKEDIN_PASSWORD', "")
        self.max_wait_time = max_wait_time
        self.driver = None
        self.setup_driver(headless)
        
        if not self.USERNAME or not self.PASSWORD:
            print("❌ Please set LINKEDIN_EMAIL and LINKEDIN_PASSWORD in your .env file")
            print("   Or update the credentials in the script")
    
    def setup_driver(self, headless=False):
        """Setup Chrome WebDriver with optimized options"""
        options = Options()
        options.add_argument("--start-maximized")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        
        if headless:
            options.add_argument("--headless")
        
        try:
            self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
            print("✅ Browser setup complete")
        except Exception as e:
            print(f"❌ Failed to setup browser: {e}")
            raise

    def login_to_linkedin(self):
        """Login to LinkedIn with improved error handling"""
        try:
            print("🔐 Logging into LinkedIn...")
            self.driver.get("https://www.linkedin.com/login")
            
            # Wait for login form
            WebDriverWait(self.driver, self.max_wait_time).until(
                EC.presence_of_element_located((By.ID, "username"))
            )
            
            # Fill credentials
            username_field = self.driver.find_element(By.ID, "username")
            password_field = self.driver.find_element(By.ID, "password")
            
            username_field.clear()
            username_field.send_keys(self.USERNAME)
            password_field.clear()
            password_field.send_keys(self.PASSWORD)
            
            # Click login
            login_button = self.driver.find_element(By.XPATH, '//button[@type="submit"]')
            login_button.click()
            
            # Wait for successful login
            try:
                WebDriverWait(self.driver, self.max_wait_time).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder='Search']"))
                )
                print("✅ Successfully logged in")
                return True
            except TimeoutException:
                print("⚠️ Login may have failed or requires verification")
                return False
                
        except Exception as e:
            print(f"❌ Login failed: {e}")
            return False

    def search_keyword(self, keyword):
        """Search for keyword with improved error handling"""
        try:
            print(f"🔍 Searching for: '{keyword}'")
            
            # Find and use search box
            search_box = WebDriverWait(self.driver, self.max_wait_time).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder='Search']"))
            )
            
            search_box.clear()
            search_box.send_keys(keyword)
            search_box.send_keys(Keys.RETURN)
            
            time.sleep(5)  # Wait for search results
            
            # Click on Posts filter
            try:
                posts_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[text()='Posts']"))
                )
                posts_button.click()
                print("✅ Applied Posts filter")
                time.sleep(3)
                return True
            except TimeoutException:
                print("⚠️ Could not find Posts filter, continuing with general results")
                return True
                
        except Exception as e:
            print(f"❌ Search failed: {e}")
            return False

    def extract_post_url(self, post_element):
        """Extract post URL using the menu method"""
        try:
            # Find and click the menu button (three dots)
            menu_button = post_element.find_element(
                By.XPATH, ".//button[contains(@class, 'feed-shared-control-menu__trigger')]"
            )
            
            # Scroll element into view and click
            self.driver.execute_script("arguments[0].scrollIntoView(true);", menu_button)
            time.sleep(0.5)
            self.driver.execute_script("arguments[0].click();", menu_button)
            time.sleep(1)

            # Wait for menu to appear and click "Copy link to post"
            copy_link_option = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((
                    By.XPATH, 
                    "//div[contains(@class, 'feed-shared-control-menu__content')]//span[contains(text(), 'Copy link to post')]"
                ))
            )
            copy_link_option.click()
            time.sleep(1)

            # Get URL from clipboard
            post_url = pyperclip.paste().strip()
            
            # Close menu by clicking elsewhere
            self.driver.execute_script("document.body.click();")
            time.sleep(0.5)
            
            return post_url if post_url.startswith('http') else "N/A"
            
        except Exception as e:
            print(f"   ⚠️ Could not extract URL: {e}")
            return "N/A"

    def scrape_posts(self, keyword, limit=50, max_scrolls=10):
        """Scrape posts with improved logic and error handling"""
        results = []
        scroll_count = 0
        posts_processed = set()  # Track processed posts to avoid duplicates

        print(f"\n🎯 Starting scrape for keyword: '{keyword}' (limit: {limit})")
        print(f"📜 Will scroll maximum {max_scrolls} times\n")

        while len(results) < limit and scroll_count < max_scrolls:
            try:
                # Wait for posts to load
                time.sleep(2)
                
                # Find all posts on current page
                posts = self.driver.find_elements(
                    By.XPATH, "//div[contains(@class, 'feed-shared-update-v2')]"
                )
                
                print(f"[Scroll {scroll_count + 1}] Found {len(posts)} posts on page")

                for i, post in enumerate(posts):
                    if len(results) >= limit:
                        break
                    
                    try:
                        # Skip if we've already processed this post
                        post_id = post.get_attribute('data-urn') or f"post_{scroll_count}_{i}"
                        if post_id in posts_processed:
                            continue
                        posts_processed.add(post_id)
                        
                        # Extract post content with multiple selectors
                        post_text = self.extract_post_content(post)
                        
                        if not post_text:
                            continue
                            
                        # Check if keyword matches (case insensitive)
                        if keyword.lower() not in post_text.lower():
                            continue

                        print(f"   ✅ Found matching post #{len(results) + 1}")
                        
                        # Extract post URL
                        post_url = self.extract_post_url(post)
                        
                        # Store result
                        result = {
                            "Post Text": post_text,
                            "Post URL": post_url,
                            "Keyword": keyword,
                            "Scraped At": time.strftime('%Y-%m-%d %H:%M:%S')
                        }
                        
                        results.append(result)
                        print(f"   💾 Saved post #{len(results)} - URL: {post_url[:50]}...")

                    except Exception as e:
                        print(f"   ⚠️ Error processing post {i+1}: {e}")
                        continue

                # Scroll to load more posts
                if len(results) < limit:
                    print(f"   📜 Scrolling for more posts...")
                    self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(3)  # Wait for new posts to load
                    scroll_count += 1
                else:
                    break

            except Exception as e:
                print(f"❌ Error during scrolling iteration {scroll_count + 1}: {e}")
                scroll_count += 1
                continue

        print(f"\n🎉 Scraping complete! Found {len(results)} matching posts")
        return results

    def extract_post_content(self, post_element):
        """Extract post content with multiple fallback selectors"""
        selectors = [
            ".//span[@class='break-words tvm-parent-container' and @dir='ltr']",
            ".//div[contains(@class, 'feed-shared-text')]//span[contains(@class, 'break-words')]",
            ".//div[contains(@class, 'update-components-text')]//span",
            ".//span[contains(@class, 'break-words')]",
            ".//div[contains(@data-test-id, 'post-text')]",
        ]
        
        for selector in selectors:
            try:
                content_element = post_element.find_element(By.XPATH, selector)
                text = content_element.text.strip()
                if text and len(text) > 10:  # Ensure it's substantial content
                    return text
            except:
                continue
        
        return None

    def save_results(self, results, keyword, formats=['csv', 'json']):
        """Save results in multiple formats"""
        if not results:
            print("❌ No results to save")
            return False

        timestamp = time.strftime('%Y%m%d_%H%M%S')
        base_filename = f"linkedin_posts_{keyword.replace(' ', '_')}_{timestamp}"
        
        saved_files = []
        
        try:
            # Save as CSV
            if 'csv' in formats:
                csv_filename = f"{base_filename}.csv"
                with open(csv_filename, mode="w", newline="", encoding="utf-8") as file:
                    fieldnames = ["Post Text", "Post URL", "Keyword", "Scraped At"]
                    writer = csv.DictWriter(file, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(results)
                saved_files.append(csv_filename)
            
            # Save as JSON
            if 'json' in formats:
                json_filename = f"{base_filename}.json"
                with open(json_filename, 'w', encoding='utf-8') as file:
                    json.dump(results, file, indent=2, ensure_ascii=False)
                saved_files.append(json_filename)
            
            for file in saved_files:
                print(f"✅ Saved {len(results)} posts to {file}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error saving results: {e}")
            return False

    def run_scraper(self, keyword, limit=50, max_scrolls=10, save_formats=['csv', 'json']):
        """Run the complete scraping process"""
        print("🚀 Starting LinkedIn Post Scraper")
        print("=" * 50)
        
        try:
            # Step 1: Login
            if not self.login_to_linkedin():
                print("❌ Cannot proceed without successful login")
                return False
            
            # Step 2: Search
            if not self.search_keyword(keyword):
                print("❌ Search failed")
                return False
            
            # Step 3: Scrape posts
            posts = self.scrape_posts(keyword, limit, max_scrolls)
            
            if not posts:
                print("❌ No matching posts found")
                return False
            
            # Step 4: Save results
            self.save_results(posts, keyword, save_formats)
            
            print(f"\n🎊 Successfully scraped {len(posts)} posts for keyword '{keyword}'!")
            return True
            
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            return False

    def close(self):
        """Close the browser"""
        if self.driver:
            self.driver.quit()
            print("🔒 Browser closed")


def main():
    """Main function with configuration"""
    
    # Configuration - Modify these settings
    config = {
        'keyword': 'Sales',           # Search keyword
        'limit': 30,                  # Number of posts to scrape
        'max_scrolls': 5,            # Maximum scroll iterations
        'headless': False,           # Run in headless mode
        'save_formats': ['csv', 'json']  # Output formats
    }
    
    print(f"Configuration:")
    print(f"  Keyword: {config['keyword']}")
    print(f"  Limit: {config['limit']} posts")
    print(f"  Max Scrolls: {config['max_scrolls']}")
    print(f"  Headless: {config['headless']}")
    print(f"  Save Formats: {config['save_formats']}")
    print("-" * 50)
    
    # Initialize scraper
    scraper = LinkedInPostScraper(headless=config['headless'])
    
    try:
        # Run scraping
        success = scraper.run_scraper(
            keyword=config['keyword'],
            limit=config['limit'],
            max_scrolls=config['max_scrolls'],
            save_formats=config['save_formats']
        )
        
        if success:
            print("\n✨ Scraping completed successfully!")
        else:
            print("\n💥 Scraping failed!")
            
    except KeyboardInterrupt:
        print("\n⏹️ Scraping interrupted by user")
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
    finally:
        scraper.close()


if __name__ == "__main__":
    main()