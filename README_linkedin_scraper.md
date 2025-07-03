# LinkedIn Scraping Automation

A comprehensive Python automation tool for scraping LinkedIn posts using Selenium WebDriver. This tool automates the entire process of logging into LinkedIn, searching for specific content, scrolling through posts, and extracting post data including content, author information, and engagement metrics.

## 🚀 Features

- **Automated Login**: Secure login to LinkedIn using credentials
- **Smart Search**: Search for specific topics or keywords
- **Intelligent Scrolling**: Automatically scroll to load more posts
- **Data Extraction**: Scrape post content, author names, post links, and engagement metrics
- **Multiple Output Formats**: Save data in CSV, JSON, or Excel formats
- **Error Handling**: Robust error handling and retry mechanisms
- **Headless Mode**: Option to run without browser window for production environments

## 📋 Requirements

- Python 3.7+
- Chrome browser installed
- LinkedIn account

## 🛠️ Installation

1. **Clone or download the project files**

2. **Install required dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Setup credentials**:
   - Copy `.env.example` to `.env`
   - Add your LinkedIn credentials to `.env`:
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

## 🔧 Configuration

### Environment Variables (.env file)
```bash
# LinkedIn Credentials
LINKEDIN_EMAIL=your-email@example.com
LINKEDIN_PASSWORD=your-password-here

# Optional Configuration
SEARCH_QUERY=artificial intelligence
MAX_POSTS=30
SCROLL_COUNT=3
```

## 💻 Usage

### Option 1: Quick Start (Recommended)
```bash
python run_scraper.py
```

### Option 2: Using the LinkedInScraper Class Directly
```python
from linkedin_scraper import LinkedInScraper

# Initialize scraper
scraper = LinkedInScraper(headless=False)

# Run complete automation
scraper.run_full_scraping(
    email=None,  # Uses .env file
    password=None,  # Uses .env file
    query="artificial intelligence",
    max_posts=30,
    scroll_count=3
)

# Clean up
scraper.close()
```

### Option 3: Step-by-Step Control
```python
from linkedin_scraper import LinkedInScraper

scraper = LinkedInScraper()

# Step 1: Login
scraper.login()

# Step 2: Search
scraper.search_posts("machine learning")

# Step 3: Scroll to load more posts
scraper.scroll_and_load_posts(scroll_count=5)

# Step 4: Scrape posts
scraper.scrape_posts(max_posts=50)

# Step 5: Save data
scraper.save_data(filename="my_linkedin_data", format="csv")

# Clean up
scraper.close()
```

## 📊 Output Data

The scraper extracts the following information for each post:

| Field | Description |
|-------|-------------|
| `index` | Post index number |
| `content` | Post text content |
| `author` | Post author name |
| `post_link` | Direct link to the post |
| `likes` | Number of likes/reactions |
| `comments` | Comment count or text |
| `timestamp` | Post timestamp (when available) |
| `scraped_at` | When the data was scraped |

### Output Formats

- **CSV**: `linkedin_posts_YYYYMMDD_HHMMSS.csv`
- **JSON**: `linkedin_posts_YYYYMMDD_HHMMSS.json`
- **Excel**: `linkedin_posts_YYYYMMDD_HHMMSS.xlsx`

## ⚙️ Configuration Options

### LinkedInScraper Parameters
```python
scraper = LinkedInScraper(
    headless=False  # Set to True for headless mode
)
```

### Scraping Parameters
```python
scraper.run_full_scraping(
    email="your-email@example.com",      # LinkedIn email
    password="your-password",            # LinkedIn password
    query="search term",                 # Search query
    max_posts=50,                       # Maximum posts to scrape
    scroll_count=5                      # Number of scroll iterations
)
```

## 🛡️ Security Considerations

1. **Never commit credentials to version control**
2. **Use environment variables for sensitive data**
3. **Consider using LinkedIn's official API for production use**
4. **Respect LinkedIn's terms of service and rate limits**
5. **Be mindful of scraping frequency to avoid account restrictions**

## 🔧 Troubleshooting

### Common Issues

1. **Login fails**:
   - Check credentials in `.env` file
   - Verify LinkedIn account is not locked
   - Try logging in manually first

2. **No posts found**:
   - Verify search query returns results manually
   - Check if LinkedIn's UI has changed (may need selector updates)
   - Try different search terms

3. **Chrome driver issues**:
   - Update Chrome browser to latest version
   - Clear browser cache and cookies
   - Try running in headless mode

4. **Rate limiting**:
   - Reduce scroll count and max posts
   - Add longer delays between requests
   - Use headless mode to be less detectable

### Debug Mode
For debugging, you can enable verbose output:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📝 Example Workflow

1. **Setup**:
   ```bash
   pip install -r requirements.txt
   cp .env.example .env
   # Edit .env with your credentials
   ```

2. **Run scraping**:
   ```bash
   python run_scraper.py
   ```

3. **Check output**:
   - Look for `linkedin_posts_*.csv` files
   - Open in Excel or any CSV viewer

## ⚠️ Important Notes

- This tool is for educational and research purposes
- Always respect LinkedIn's Terms of Service
- Use responsibly and avoid overwhelming LinkedIn's servers
- Consider using LinkedIn's official API for commercial applications
- Be aware that excessive scraping may result in account restrictions

## 🤝 Contributing

Feel free to submit issues, feature requests, or pull requests to improve this tool.

## 📄 License

This project is provided as-is for educational purposes. Please ensure compliance with LinkedIn's Terms of Service and applicable laws in your jurisdiction.