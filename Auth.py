# Auth.py contains the classes in order to use the authentication methods in the FastAPIDecorator.
# This file also allows you to add new users to the credentials file.

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import json
import bcrypt 
from typing import Dict

class UserCredentialsDB:
    """
    A class for managing user credentials, including storing, loading, and validating user credentials.

    Attributes:
        filepath (str): The path to the file where user credentials are stored. Here, it's user_credentials.json.
        credentials (Dict[str, str]): A dictionary to store user credentials, with usernames as keys and hashed passwords as values.

    Methods:
        add_user(username, password): Adds a new user with a hashed password to the credentials dictionary and saves it to the file.
        validate_user(username, password): Validates a user's credentials against the stored hashed password.
        save_credentials(): Saves the current state of the credentials dictionary to a file.
        load_credentials(): Loads credentials from a file into the credentials dictionary.
        delete_user(username, password): Removes the user if the password matches from credentials dictionary and saves the updated file.

    """
    def __init__(self, filepath='user_credentials.json'):
        self.filepath = filepath
        self.credentials: Dict[str, str] = {}
        self.credentials = self.load_credentials()

    def add_user(self, username: str, password: str):
        hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        self.credentials[username] = hashed_password.decode('utf-8')
        self.save_credentials()

    def validate_user(self, username: str, password: str) -> bool:
        hashed_password = self.credentials.get(username)
        if hashed_password:
            return bcrypt.checkpw(password.encode(), hashed_password.encode('utf-8'))
        return False

    def save_credentials(self):
        with open(self.filepath, 'w') as file:
            json.dump(self.credentials, file)

    def load_credentials(self):
        try:
            with open(self.filepath, 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            return {}
    
    def delete_user(self, username: str, password: str):
        if self.validate_user(username, password):
            del self.credentials[username]
            self.save_credentials()
            return True
        return False
    
################# USE CASES #################
user_db = UserCredentialsDB()
security = HTTPBasic()


def get_current_user(credentials: HTTPBasicCredentials = Depends(security)):
    """
    Authenticates a user based on HTTP Basic Credentials.
    Args:
        credentials (HTTPBasicCredentials): The credentials provided in the request.
    Returns:
        str: The username of the authenticated user.
    Raises:
        HTTPException: If authentication fails, it raises a 401 Unauthorized error with a detailed message.
    This function is designed to be used as a dependency in FastAPI route handlers to enforce authentication.
    """
    
    if not user_db.validate_user(credentials.username, credentials.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Incorrect username or password",
                            headers={"WWW-Authenticate": "Basic"})

    return credentials.username


# Database handling : adding users to the database
user_db.add_user("Meghna", "M272")
user_db.add_user("user1", "password1")
user_db.add_user("TEST", "test1")

# Deleting users to the database
user_db.delete_user("TEST", "test1")

