import os
import firebase_admin
from firebase_admin import firestore, credentials


try:
    # Attempt to get the path from an environment variable for better security

    # Example: SERVICE_ACCOUNT_KEY_PATH = 'path/to/your/serviceAccountKey.json'
    SERVICE_ACCOUNT_KEY_PATH = os.environ.get('FIREBASE_SERVICE_ACCOUNT_KEY', 'serviceAccountKey.json')
    if not os.path.exists(SERVICE_ACCOUNT_KEY_PATH):
        print(f"ERROR: Firebase service account key not found at {SERVICE_ACCOUNT_KEY_PATH}")
        db = None # Set db to None if initialization fails
    else:
        cred = credentials.Certificate(SERVICE_ACCOUNT_KEY_PATH)
        app = firebase_admin.initialize_app(cred)
        db = firestore.client()
        print("Firebase initialized successfully.")

except Exception as e:
    print(f"ERROR: Could not initialize Firebase: {e}")
    db = None # Set db to None if initialization fails

USERS_COLLECTION = 'discord_users'

# --- Function to Save User Data ---
def save_user_data(user_id: str, data: dict):
    """
    Saves or updates data for a specific Discord user in Firestore.

    Args:
        user_id (str): The unique Discord user ID. This will be the document ID.
        data (dict): A dictionary containing the user's information.
                     Example: {'goal': 'Run a marathon', 'situation': '3 months to prepare'}
    """
    if db is None:
        print("Database not initialized. Cannot save data.")
        return
    try:
        user_doc_ref = db.collection(USERS_COLLECTION).document(user_id)
        # merge=True allows updating specific fields without overwriting the whole document
        user_doc_ref.set(data, merge=True)
        print(f"Data for user '{user_id}' saved successfully: {data}")
    except Exception as e:
        print(f"Error saving data for user '{user_id}': {e}")

# --- Function to Get User Data ---
def get_user_data(user_id: str):
    """
    Retrieves data for a specific Discord user from Firestore.

    Args:
        user_id (str): The unique Discord user ID.

    Returns:
        dict or None: A dictionary containing the user's data if found, otherwise None.
    """
    if db is None:
        print("Database not initialized. Cannot retrieve data.")
        return None
    try:
        user_doc_ref = db.collection(USERS_COLLECTION).document(user_id)
        doc = user_doc_ref.get()
        if doc.exists:
            data = doc.to_dict()
            print(f"Data for user '{user_id}' retrieved successfully: {data}")
            return data
        else:
            print(f"No data found for user '{user_id}'.")
            return None
    except Exception as e:
        print(f"Error retrieving data for user '{user_id}': {e}")
        return None

