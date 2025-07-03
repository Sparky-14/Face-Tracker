#!/usr/bin/env python3
"""
Simple script to run LinkedIn scraping automation
Usage: python run_scraper.py
"""

from linkedin_scraper import LinkedInScraper
import os

def main():
    print("🤖 LinkedIn Scraping Automation")
    print("=" * 40)
    
    # Configuration - modify these as needed
    config = {
        'search_query': 'python programming',  # Change this to your search term
        'max_posts': 25,                       # Number of posts to scrape
        'scroll_count': 3,                     # How many times to scroll down
        'headless': False,                     # Set to True to run without browser window
        'output_format': ['csv', 'json']       # Output formats
    }
    
    print(f"Search Query: {config['search_query']}")
    print(f"Max Posts: {config['max_posts']}")
    print(f"Scroll Count: {config['scroll_count']}")
    print(f"Headless Mode: {config['headless']}")
    print("-" * 40)
    
    # Initialize scraper
    scraper = LinkedInScraper(headless=config['headless'])
    
    try:
        # Run the scraping automation
        success = scraper.run_full_scraping(
            email=None,  # Will use LINKEDIN_EMAIL from .env
            password=None,  # Will use LINKEDIN_PASSWORD from .env
            query=config['search_query'],
            max_posts=config['max_posts'],
            scroll_count=config['scroll_count']
        )
        
        if success:
            print("\n🎊 Scraping completed successfully!")
            print("Check the output files for your data.")
        else:
            print("\n❌ Scraping failed. Please check your credentials and try again.")
            
    except KeyboardInterrupt:
        print("\n⏹️ Scraping interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
    finally:
        scraper.close()

if __name__ == "__main__":
    main()