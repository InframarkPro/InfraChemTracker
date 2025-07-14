"""
Registration requests module for admin approval workflow

This module handles registration requests, including:
- Storing pending registration requests
- Admin approval/rejection of requests
- Email notifications (mock implementation)
"""
import streamlit as st
import json
import os
import uuid
from datetime import datetime
from utils.auth import hash_password, create_user

# File to store registration requests
REGISTRATION_REQUESTS_PATH = "saved_data/registration_requests.json"

def ensure_requests_db_exists():
    """Ensure the registration requests database file exists"""
    # Make sure the directory exists
    os.makedirs(os.path.dirname(REGISTRATION_REQUESTS_PATH), exist_ok=True)
    
    # Create the file if it doesn't exist
    if not os.path.exists(REGISTRATION_REQUESTS_PATH):
        with open(REGISTRATION_REQUESTS_PATH, 'w') as f:
            json.dump({"pending_requests": []}, f)

def get_requests():
    """Get all registration requests from database"""
    ensure_requests_db_exists()
    with open(REGISTRATION_REQUESTS_PATH, 'r') as f:
        return json.load(f)

def save_requests(requests_data):
    """Save registration requests to database"""
    ensure_requests_db_exists()
    with open(REGISTRATION_REQUESTS_PATH, 'w') as f:
        json.dump(requests_data, f, indent=2)

def create_registration_request(username, email, password):
    """
    Create a new registration request in the database
    
    Args:
        username: Requested username
        email: User's email address
        password: Plain-text password (will be hashed)
        
    Returns:
        tuple: (success, message)
    """
    # Load existing requests
    requests_data = get_requests()
    
    # Check if username or email already exists in pending requests
    for request in requests_data["pending_requests"]:
        if request["username"].lower() == username.lower():
            return False, "Username already exists in pending requests"
        if request["email"].lower() == email.lower():
            return False, "Email already exists in pending requests"
    
    # Create new request
    new_request = {
        "id": str(uuid.uuid4()),
        "username": username,
        "email": email,
        "password_hash": hash_password(password),
        "status": "pending",
        "requested_at": datetime.now().isoformat()
    }
    
    # Add request to database
    requests_data["pending_requests"].append(new_request)
    save_requests(requests_data)
    
    # Mock email notification to admin
    send_admin_notification(username, email)
    
    return True, "Registration request submitted. You will be notified when approved."

def send_admin_notification(username, email):
    """
    Send a notification to the admin about a new registration request
    
    This is a mock implementation. In a real system, this would send an email.
    
    Args:
        username: The requested username
        email: The user's email address
    """
    # In a real implementation, this would send an email to the admin
    print(f"New registration request from {username} ({email})")
    
    # Log the notification for reference
    log_file = "saved_data/registration_notifications.log"
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    with open(log_file, 'a') as f:
        f.write(f"{datetime.now().isoformat()} - New request: {username} ({email})\n")

def send_user_notification(email, status):
    """
    Send a notification to the user about their registration request status
    
    This is a mock implementation. In a real system, this would send an email.
    
    Args:
        email: The user's email address
        status: 'approved' or 'rejected'
    """
    # In a real implementation, this would send an email to the user
    print(f"Registration request {status} for user: {email}")
    
    # Log the notification for reference
    log_file = "saved_data/registration_notifications.log"
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    with open(log_file, 'a') as f:
        f.write(f"{datetime.now().isoformat()} - Request {status}: {email}\n")

def approve_request(request_id):
    """
    Approve a registration request
    
    Args:
        request_id: The ID of the request to approve
        
    Returns:
        tuple: (success, message)
    """
    # Load requests
    requests_data = get_requests()
    
    # Find the request
    for i, request in enumerate(requests_data["pending_requests"]):
        if request["id"] == request_id:
            # Create the user
            success, message = create_user(
                request["username"], 
                request["email"], 
                "", # Empty password because we'll use the hashed one
                theme="industrial"
            )
            
            if success:
                # Use the pre-hashed password
                from utils.auth import get_users, save_users
                users_data = get_users()
                for user in users_data["users"]:
                    if user["username"] == request["username"]:
                        user["password_hash"] = request["password_hash"]
                        save_users(users_data)
                        break
                
                # Remove the request
                requests_data["pending_requests"].pop(i)
                save_requests(requests_data)
                
                # Notify the user
                send_user_notification(request["email"], "approved")
                
                return True, f"User {request['username']} has been approved"
            else:
                return False, message
    
    return False, "Request not found"

def reject_request(request_id):
    """
    Reject a registration request
    
    Args:
        request_id: The ID of the request to reject
        
    Returns:
        tuple: (success, message)
    """
    # Load requests
    requests_data = get_requests()
    
    # Find the request
    for i, request in enumerate(requests_data["pending_requests"]):
        if request["id"] == request_id:
            # Store email for notification
            email = request["email"]
            username = request["username"]
            
            # Remove the request
            requests_data["pending_requests"].pop(i)
            save_requests(requests_data)
            
            # Notify the user
            send_user_notification(email, "rejected")
            
            return True, f"Registration request for {username} has been rejected"
    
    return False, "Request not found"

def get_pending_requests_count():
    """Get the number of pending registration requests"""
    requests_data = get_requests()
    return len(requests_data["pending_requests"])