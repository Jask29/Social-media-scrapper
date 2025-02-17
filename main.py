import re
import sys
from insta_scraper import main as insta_main
from yt_scraper import main as yt_main
from fb_scraper import main as fb_main

def identify_platform_and_process(url):
    """
    Identifies the platform of the provided URL (Instagram or YouTube)
    and delegates the processing to the respective scraper.

    Parameters:
    url: str - The input URL provided by the user.
    """
    try:
        # Check if the URL belongs to YouTube
        if re.search(r"(youtube\.com|youtu\.be)", url, re.IGNORECASE):
            print("YouTube URL detected.")
            yt_main(url)  # Call YouTube scraper's main function
        # Check if the URL belongs to Instagram
        elif re.search(r"(instagram\.com)", url, re.IGNORECASE):
            print("Instagram URL detected.")
            insta_main(url)  # Call Instagram scraper's main function
        # Check if the URL belongs to Facebook
        elif re.search(r"(facebook\.com)", url, re.IGNORECASE):
            print("Facebook URL detected.")
            fb_main(url)  # Call Facebook scraper's main function   
        else:
            print("Invalid URL or unsupported platform.")
    except Exception as e:
        print(f"Error identifying platform: {e}")
        sys.exit(1)

def main():
    """
    Main function for handling the input and processing based on platform.
    """
    print("Welcome to the Social Media Scraper!")
    url = input("Enter a URL (YouTube or Instagram): ").strip()
    identify_platform_and_process(url)

if __name__ == "__main__":
    main()
