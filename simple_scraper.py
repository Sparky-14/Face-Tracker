#!/usr/bin/env python3
"""
Simple LinkedIn Post Scraper - Easy to use version
Just update your credentials and keyword, then run!
"""

from linkedin_scraper_improved import LinkedInPostScraper

def quick_scrape():
    """Quick scraping function - just modify the settings below"""
    
    # 🔧 CONFIGURATION - UPDATE THESE SETTINGS
    KEYWORD = "artificial intelligence"      # What to search for
    MAX_POSTS = 25                          # How many posts to find
    MAX_SCROLLS = 5                         # How many times to scroll
    HEADLESS = False                        # Set True to hide browser window
    
    # 📧 CREDENTIALS - Add to .env file or update here
    EMAIL = ""                              # Your LinkedIn email (leave empty to use .env)
    PASSWORD = ""                           # Your LinkedIn password (leave empty to use .env)
    
    print("🤖 LinkedIn Post Scraper - Quick Run")
    print("=" * 45)
    print(f"🎯 Searching for: '{KEYWORD}'")
    print(f"📊 Target posts: {MAX_POSTS}")
    print(f"📜 Max scrolls: {MAX_SCROLLS}")
    print(f"👁️ Headless mode: {HEADLESS}")
    print("-" * 45)
    
    # Initialize scraper
    scraper = LinkedInPostScraper(headless=HEADLESS)
    
    # Override credentials if provided
    if EMAIL and PASSWORD:
        scraper.USERNAME = EMAIL
        scraper.PASSWORD = PASSWORD
    
    try:
        # Run the scraper
        success = scraper.run_scraper(
            keyword=KEYWORD,
            limit=MAX_POSTS,
            max_scrolls=MAX_SCROLLS,
            save_formats=['csv', 'json']
        )
        
        if success:
            print(f"\n🎉 Success! Check your files for the scraped data.")
            print(f"📁 Look for: linkedin_posts_{KEYWORD.replace(' ', '_')}_*.csv")
        else:
            print(f"\n❌ Scraping failed. Check your credentials and try again.")
            
    except KeyboardInterrupt:
        print("\n⏹️ Stopped by user")
    except Exception as e:
        print(f"\n💥 Error: {e}")
    finally:
        scraper.close()

if __name__ == "__main__":
    quick_scrape()