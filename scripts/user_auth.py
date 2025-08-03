import pymongo
import redis
import bcrypt
import json
import uuid  # Used for generating unique session tokens
from pymongo.errors import ConnectionFailure
from bson.objectid import ObjectId

# --- Redis Configuration ---
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_DB = 0
SESSION_TTL_SECONDS = 3600  # Session token expires in 1 hour

# --- MongoDB Configuration ---
MONGO_URI = "mongodb://localhost:27017/"
MONGO_DB_NAME = "wurdo_db"
MONGO_COLLECTION_NAME = "users"

# --- Connectors ---
def connect_to_mongodb(uri, db_name, collection_name):
    """Connects to a MongoDB database and returns the collection object."""
    try:
        client = pymongo.MongoClient(uri)
        client.admin.command('ismaster')
        db = client[db_name]
        collection = db[collection_name]
        print("MongoDB connection: SUCCESS")
        return collection
    except ConnectionFailure as e:
        print(f"MongoDB connection: FAILED - {e}")
        return None

def connect_to_redis(host, port, db):
    """Connects to a Redis server and returns the client object."""
    try:
        r = redis.StrictRedis(host=host, port=port, db=db, decode_responses=True)
        r.ping()
        print("Redis connection: SUCCESS")
        return r
    except redis.exceptions.ConnectionError as e:
        print(f"Redis connection: FAILED - {e}")
        return None

# --- User Authentication and Authorization Functions ---
def hash_password(password):
    """Hashes a password using bcrypt."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt)

def check_password(password, hashed_password):
    """Checks a password against a stored hash."""
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password)

def register_user(mongo_collection, user_name, password):
    """
    Registers a new user.
    Returns a dictionary of the new user's data on success, or None on failure.
    """
    if mongo_collection.find_one({'user_name': user_name}):
        return {'status': 'error', 'message': f"Username '{user_name}' already exists."}

    hashed_password = hash_password(password)
    
    user_data = {
        'user_name': user_name,
        'password_hash': hashed_password.decode('utf-8'), # Store hash as a string
        'best_chain': {
            'start_word': None,
            'chain_length': 0,
            'words_in_chain': []
        },
        'total_score': 0,
        'games_played': 0
    }

    try:
        result = mongo_collection.insert_one(user_data)
        user_data['_id'] = str(result.inserted_id)
        # Remove the password hash before returning the data
        del user_data['password_hash']
        return {'status': 'success', 'user': user_data}
    except Exception as e:
        return {'status': 'error', 'message': f"Registration failed: {e}"}

def login_user(mongo_collection, redis_client, user_name, password):
    """
    Authenticates a user and creates a session token in Redis on success.
    Returns a dictionary with user data and a session token on success.
    """
    user_document = mongo_collection.find_one({'user_name': user_name})

    if not user_document:
        return {'status': 'error', 'message': f"Login failed: User '{user_name}' not found."}
    
    # Check the provided password against the stored hash
    if check_password(password, user_document['password_hash'].encode('utf-8')):
        # Login successful. Generate and store a session token in Redis.
        session_token = str(uuid.uuid4())
        user_id_str = str(user_document['_id'])
        
        # Store a mapping from the session token to the user's ID
        redis_client.setex(f"session:{session_token}", SESSION_TTL_SECONDS, user_id_str)
        
        # Remove the password hash from the document before returning
        del user_document['password_hash']
        user_document['_id'] = user_id_str
        
        return {'status': 'success', 'user': user_document, 'session_token': session_token}
    else:
        return {'status': 'error', 'message': f"Login failed: Incorrect password for user '{user_name}'."}

def get_user_from_session(mongo_collection, redis_client, session_token):
    """
    Verifies a session token and fetches the corresponding user's data from MongoDB.
    This is the core of authorization for subsequent API calls.
    """
    user_id = redis_client.get(f"session:{session_token}")
    if user_id:
        # Session token is valid. Fetch user data from MongoDB.
        user_document = mongo_collection.find_one({'_id': ObjectId(user_id)})
        if user_document:
            # Remove the password hash for security
            del user_document['password_hash']
            user_document['_id'] = str(user_document['_id'])
            return {'status': 'success', 'user': user_document}
    
    return {'status': 'error', 'message': 'Invalid or expired session token.'}

def logout_user(redis_client, session_token):
    """Deletes a session token from Redis to log the user out."""
    redis_client.delete(f"session:{session_token}")
    return {'status': 'success', 'message': 'Logged out successfully.'}

# --- Main Script Execution (for demonstration) ---
if __name__ == "__main__":
    users_collection = connect_to_mongodb(MONGO_URI, MONGO_DB_NAME, MONGO_COLLECTION_NAME)
    redis_client = connect_to_redis(REDIS_HOST, REDIS_PORT, REDIS_DB)
    
    if not users_collection or not redis_client:
        exit()
        
    # --- Register a new user ---
    print("\n--- TEST: Registering a new user ---")
    register_result = register_user(users_collection, "wurdo_player", "super-secret-password")
    print(register_result)

    # --- Login the new user ---
    print("\n--- TEST: Logging in a new user ---")
    login_result = login_user(users_collection, redis_client, "wurdo_player", "super-secret-password")
    print(login_result)
    
    session_token = login_result.get('session_token')

    # --- Verify the session token ---
    if session_token:
        print("\n--- TEST: Getting user from a valid session token ---")
        session_result = get_user_from_session(users_collection, redis_client, session_token)
        print(session_result)
    
        # --- Logout the user ---
        print("\n--- TEST: Logging out the user ---")
        logout_result = logout_user(redis_client, session_token)
        print(logout_result)
        
        # --- Verify the session is now invalid ---
        print("\n--- TEST: Trying to use the session token after logout ---")
        invalid_session_result = get_user_from_session(users_collection, redis_client, session_token)
        print(invalid_session_result)
