from instagrapi import Client
import re
import json
import os

def login_to_instagram():
    """Login to Instagram using provided credentials."""
    print("------------------------------------------------------------------------------------------------")
    print("------------------------------------------------------------------------------------------------")
    Username = input("Enter your Instagram username: ")
    Password = input("Enter your Instagram password: ")
    print("------------------------------------------------------------------------------------------------")
    print("------------------------------------------------------------------------------------------------")
    print("Logging in....")
    print("Please wait...")
    cl = Client()
    try:
        cl.login(Username, Password)
        print("\nLogin successful!\n")
        print("------------------------------------------------------------------------------------------------")
        print("------------------------------------------------------------------------------------------------")
    except Exception as e:
        print(f"Error logging in: {e}")
        return None
    
    return cl

def save_to_file(data, filename):
    """
    Save the data to a JSON file.

    Parameters:
    data: The data to save.
    filename: Name of the file to save the data in.
    """
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"Data saved to {filename}")
    except Exception as e:
        print(f"Error saving data to file: {e}")

def get_user_info(cl,username):
    """Get information about a user by their username."""
    try:
        user_info = cl.user_info_by_username(username).model_dump()
        return user_info
    except Exception as e:
        print(f"Error fetching user info: {e}")

def get_user_following(cl,username):
    """Get the list of accounts a user is following."""
    try:
        user_id = cl.user_id_from_username(username)
        following = cl.user_following(user_id)
        return following
    except Exception as e:
        print(f"Error fetching following list: {e}")

def get_user_followers(cl,username):
    """Get the list of followers of a user."""
    try:
        user_id = cl.user_id_from_username(username)
        followers = cl.user_followers(user_id)
        return followers
    except Exception as e:
        print(f"Error fetching followers list: {e}")

def get_media_insights(cl,media_url):
    """Get insights of a specific media by its URL."""
    try:
        media_pk = cl.media_pk_from_url(media_url)
        insights = cl.insights_media(media_pk)
        return insights
    except Exception as e:
        print(f"Error fetching media insights: {e}")

def get_media_comments(cl,media_url):
    """Get the list of comments on a specific media by its URL."""
    try:
        media_id = cl.media_id(cl.media_pk_from_url(media_url))
        comments = cl.media_comments(media_id)
        return  comments
    except Exception as e:
        print(f"Error fetching media comments: {e}")

def get_media_likers(cl,media_url):
    """Get the list of users who liked a specific media by its URL."""
    try:
        media_id = cl.media_id(cl.media_pk_from_url(media_url))
        likers = cl.media_likers(media_id)
        return likers
    except Exception as e:
        print(f"Error fetching media likers: {e}")

def identify_url_type_and_process(cl, url):
    """
    Identifies if the URL is an Instagram post or account and processes it accordingly.

    Parameters:
    cl: Logged-in Instagram client instance.
    url: URL provided by the user.
    """
    try:
        # Check if it's a post URL
        if "/p/" in url or "/reel/" in url:
            media_url = url
            print("URL identified as a post/reel.")
            print("------------------------------------------------------------------------------------------------")
            print("------------------------------------------------------------------------------------------------")
            
            # Call post-related functions
            media_insights = get_media_insights(cl, media_url)
            media_comments = get_media_comments(cl, media_url)
            media_likers = get_media_likers(cl, media_url)
            
            print("\nPost Insights:")
            print(media_insights)
            print("------------------------------------------------------------------------------------------------")
            print("------------------------------------------------------------------------------------------------")
            print("\nPost Comments:")
            print(media_comments)
            print("------------------------------------------------------------------------------------------------")
            print("------------------------------------------------------------------------------------------------")
            print("\nPost Likers:")
            print(media_likers)
            print("------------------------------------------------------------------------------------------------")
            print("------------------------------------------------------------------------------------------------")
            # Save the outputs to JSON files
            save_to_file(media_insights, "post_insights.json")
            save_to_file(media_comments, "post_comments.json")
            save_to_file(media_likers, "post_likers.json")
        # Check if it's an account URL
        elif "instagram.com/" in url and "/p/" not in url and "/reel/" not in url:
            # Extract username from the account URL
            match = re.search(r"instagram\.com/([^/?]+)", url)
            if match:
                username = match.group(1)
                print("URL identified as an Instagram account.")
                
                # Call account-related functions
                user_info = get_user_info(cl, username)
                user_following = get_user_following(cl, username)
                user_followers = get_user_followers(cl, username)
                
                print("\nUser Info:")
                print(user_info)
                print("------------------------------------------------------------------------------------------------")
                print("------------------------------------------------------------------------------------------------")
                print("\nUser Following:")
                print(user_following)
                print("------------------------------------------------------------------------------------------------")
                print("------------------------------------------------------------------------------------------------")
                print("\nUser Followers:")
                print(user_followers)
                print("------------------------------------------------------------------------------------------------")
                print("------------------------------------------------------------------------------------------------")

                # Save the outputs to JSON files
                save_to_file(user_info, f"{username}_info.json")
                save_to_file(user_following, f"{username}_following.json")
                save_to_file(user_followers, f"{username}_followers.json")
            else:
                print("Invalid Instagram account URL.")
        else:
            print("Invalid URL format. Please provide a valid Instagram URL.")

    except Exception as e:
        print(f"Error processing the URL: {e}")

def main(url = None):
    """Main function to drive the script."""
    cl = login_to_instagram()
    if not cl:
        return
    
    # If no URL is provided, ask the user for it
    if not url:
        url = input("Enter the Instagram URL (post or account): ").strip()
    
    # Identify the type of URL and process accordingly
    identify_url_type_and_process(cl, url)

if __name__ == "__main__":
    main()

