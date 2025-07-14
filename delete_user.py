"""
Script to delete a specific user from the users.json database
"""
import json
import os

USER_DB_PATH = "saved_data/users.json"

def delete_user(username):
    """
    Delete a user by username
    
    Args:
        username: Username to delete
        
    Returns:
        bool: True if user was deleted, False if not found
    """
    # Make sure the file exists
    if not os.path.exists(USER_DB_PATH):
        print(f"User database file not found at {USER_DB_PATH}")
        return False
    
    # Load user data
    with open(USER_DB_PATH, 'r') as f:
        users_data = json.load(f)
    
    # Look for user to delete
    initial_count = len(users_data["users"])
    users_data["users"] = [user for user in users_data["users"] 
                         if user["username"].lower() != username.lower()]
    
    # Check if user was found and deleted
    if len(users_data["users"]) < initial_count:
        # Save updated data
        with open(USER_DB_PATH, 'w') as f:
            json.dump(users_data, f, indent=2)
        print(f"User '{username}' deleted successfully")
        return True
    else:
        print(f"User '{username}' not found")
        return False

if __name__ == "__main__":
    delete_user("Nobody")