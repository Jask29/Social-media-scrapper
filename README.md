# Social Media Scraper

This project is designed to scrape data from various social media platforms including Instagram, YouTube, and Facebook. The project utilizes different tools and libraries tailored to each platform to extract useful information, such as user details, followers, following, media insights, and more.

## Features
- Instagram Scraping:
    - Login to Instagram.
    - Fetch user details, followers, and following.
    - Extract media insights, comments, and likers.

- YouTube Scraping:
    - Fetch details of videos and channels.
    - Extract video comments with replies.
    - fetch_channel_data function can be used to gather more data. (In main we have called fetch_channel_details.)
    - similarly, fetch_video_comments can be used to retrieve less info of comments.( we have used scrape_comment_with_replies)

- Facebook Scraping:
    - Fetch user details, followers, and following.
    - Extract media insights, comments, and likers using Scrapy(under developement)
    
- Main Application:
    - Identifies the platform based on the provided URL.
    - Routes the URL to the appropriate scraper for processing.
    - Consolidates outputs into structured files (e.g., CSV, JSON).

## Project Structure

project/
├── insta_scraper.py        # Instagram scraping functionality
├── yt_scraper.py           # YouTube scraping functionality
├── fb_scraper.py           # Facebook scraper using facevook-scrapper
├── fb_scrap/             # Facebook scraping using Scrapy (under development)
│   ├── spiders/
│   │   ├── following_spider.py
│   │   ├── followers_spider.py
│   |   └── media_likers_spider.py
├── main.py                # Main entry point of the application
├── requirements.txt       # Required Python libraries
└── README.md              # Project documentation

## How to Setup
- For Youtube scraping: 
    - Go to https://console.cloud.google.com/ (Search YouTube Data API v3).
    - Click on Enable And Click Credential And Click Api Key.
    - After clicking Create Credential, Copy "api_key" from there. (Although one is already given, kindly don't misuse it)

- For Insta scraping:
    - You will need loginn credentials of an account.

## How to Use
- Install Dependencies:
    - Install all required Python libraries using pip:
    - pip install -r requirements.txt

- Run the Main Script
    - Execute the main script to process URLs:
    - python main.py
    - Enter a social media URL when prompted. The script will identify the platform and route the URL to the appropriate scraper.

- The final output will be stored in a CSV/JSON file same directory path.

## Requirements
- Python 3.5+

## Supported Platforms
- Instagram: Uses instagrapi for authenticated scraping.
- YouTube: Uses googleapiclient to interact with the YouTube Data API.
- Facebook: Uses facebook-scraper and Scrapy (this is under development) for dynamic data extraction.

## Limitations
- Rate Limits: APIs and websites enforce rate limits. Ensure to handle limits gracefully or use authenticated sessions.
- Dynamic Content: Facebook pages with heavy JavaScript reliance may require scrapy-playwright for rendering.
- Legal Compliance: Scraping may violate terms of service. Use responsibly and ensure compliance with laws and platform policies.

## Dependencies
- Python 3.8+

## Key Libraries:
- instagrapi
- googleapiclient
- scrapy
- pandas
- requests
- isodate

## Note:
To scrape unsupported features like getting user followers, following, and media likers from Facebook using Scrapy, we need to construct a Scrapy project that interacts with Facebook pages and parses relevant HTML data. Since Facebook employs dynamic loading and sophisticated anti-scraping measures, this requires careful handling of headers, cookies, and possibly JavaScript execution (via libraries like scrapy-splash or scrapy-playwright).
1. setup a scrapy project
2. define scrapy spiders (three of them are defined)
3. Run the spiders (save cookies in a file)
