from facebook_scraper import get_profile, get_posts
import re

# Function to scrape user info
def get_user_info(username):
    """Fetch user profile details by username."""
    try:
        user_info = get_profile(username, cookies="cookies.json")  # Provide cookies file if required
        return user_info
    except Exception as e:
        print(f"Error fetching user info: {e}")
        return None

# Function to fetch user following (Facebook doesn't directly expose this info)
def get_user_following(username):
    """Fetch user's following list (not supported by facebook-scraper)."""
    print("Fetching following list is not supported by facebook-scraper.")
    return None

# Function to fetch user followers (Facebook doesn't directly expose this info)
def get_user_followers(username):
    """Fetch user's followers list (not supported by facebook-scraper)."""
    print("Fetching followers list is not supported by facebook-scraper.")
    return None

# Function to get media insights
def get_media_insights(media_url):
    """Fetch media insights for a Facebook post."""
    try:
        for post in get_posts(post_urls=[media_url], cookies="cookies.txt"):
            return {
                "Post ID": post.get("post_id"),
                "Text": post.get("post_text"),
                "Time": post.get("time"),
                "Likes": post.get("likes"),
                "Shares": post.get("shares"),
                "Comments": post.get("comments"),
                "Reactions": post.get("reactions"),
            }
    except Exception as e:
        print(f"Error fetching media insights: {e}")
        return None

# Function to fetch media comments
def get_media_comments(media_url):
    """Fetch comments from a Facebook post."""
    try:
        for post in get_posts(post_urls=[media_url], cookies="cookies.txt"):
            return post.get("comments_full")  # Full comments, if available
    except Exception as e:
        print(f"Error fetching media comments: {e}")
        return None

# Function to fetch media likers (Facebook doesn't directly expose this info)
def get_media_likers(media_url):
    """Fetch users who liked a Facebook post (not supported by facebook-scraper)."""
    print("Fetching likers is not supported by facebook-scraper.")
    return None

# Function to identify URL type and process it
def identify_url_type_and_process(cl, url):
    """Identify whether the URL is for a user or post and process accordingly."""
    try:
        if "facebook.com/" in url:
            # Check for user profile URL
            if re.search(r"facebook\.com/([a-zA-Z0-9._-]+)(?:/)?$", url):
                username = re.search(r"facebook\.com/([a-zA-Z0-9._-]+)(?:/)?$", url).group(1)
                print(f"Fetching details for user: {username}")
                user_info = get_user_info(username)
                if user_info:
                    print("------------------------------------------------------------------------------------------------")
                    print("------------------------------------------------------------------------------------------------")
                    print("User Info:", user_info)

                following = get_user_following(username)
                if following:
                    print("------------------------------------------------------------------------------------------------")
                    print("------------------------------------------------------------------------------------------------")
                    print("Following List:", following)

                followers = get_user_followers(username)
                if followers:
                    print("------------------------------------------------------------------------------------------------")
                    print("------------------------------------------------------------------------------------------------")
                    print("Followers List:", followers)

            # Check for post URL
            elif re.search(r"facebook\.com/.*/posts/\d+", url):
                print("------------------------------------------------------------------------------------------------")
                print("------------------------------------------------------------------------------------------------")
                print(f"Fetching details for post: {url}")
                media_insights = get_media_insights(url)
                if media_insights:
                    print("------------------------------------------------------------------------------------------------")
                    print("------------------------------------------------------------------------------------------------")
                    print("Media Insights:", media_insights)

                media_comments = get_media_comments(url)
                if media_comments:
                    print("------------------------------------------------------------------------------------------------")
                    print("------------------------------------------------------------------------------------------------")
                    print("Media Comments:", media_comments)

                media_likers = get_media_likers(url)
                if media_likers:
                    print("------------------------------------------------------------------------------------------------")
                    print("------------------------------------------------------------------------------------------------")
                    print("Media Likers:", media_likers)
            else:
                print("Invalid Facebook URL format.")
        else:
            print("Invalid URL. Not a Facebook URL.")
    except Exception as e:
        print(f"Error processing URL: {e}")

# Main function
def main(url=None):
    """Main function to drive the Facebook scraper."""
    # Placeholder for authentication if needed in the future
    cl = None  # Not needed for facebook-scraper, but keeping for consistency
    if not url:
        print("------------------------------------------------------------------------------------------------")
        print("------------------------------------------------------------------------------------------------")
        url = input("Enter a Facebook URL (post or user profile): ").strip()
        
    identify_url_type_and_process(cl, url)

# Run the program
if __name__ == "__main__":
    main()
