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

# ... (all your existing code from user_auth.py) ...

def update_user_game_stats(mongo_collection, redis_client, user_id, new_score_data):
    """
    Updates a user's game statistics in MongoDB and invalidates the Redis cache.

    Args:
        mongo_collection: The MongoDB collection object.
        redis_client: The Redis client object.
        user_id (str): The ID of the user to update.
        new_score_data (dict): A dictionary containing the results of a single game.
            Example: {
                'game_chain': {'start_word': 'cat', 'chain_length': 3, 'words_in_chain': ['cat', 'at', 'a']},
                'game_score': 150
            }
    
    Returns:
        bool: True on successful update, False otherwise.
    """
    # 1. Fetch the user's current stats to compare
    user_document = mongo_collection.find_one({'_id': ObjectId(user_id)})
    if not user_document:
        print(f"Error: User with ID {user_id} not found.")
        return False
    
    current_best_chain_length = user_document['best_chain']['chain_length']
    new_chain_data = new_score_data['game_chain']
    new_chain_length = new_chain_data['chain_length']
    new_total_score = user_document['total_score'] + new_score_data['game_score']
    new_games_played = user_document['games_played'] + 1
    
    # Prepare the update document
    update_doc = {
        '$set': {
            'total_score': new_total_score,
            'games_played': new_games_played
        }
    }

    # 2. Check if the new chain is a new high score
    if new_chain_length > current_best_chain_length:
        update_doc['$set']['best_chain'] = new_chain_data
        print(f"New high score! Updating best chain for user {user_id}.")

    try:
        # 3. Update the document in MongoDB
        result = mongo_collection.update_one({'_id': ObjectId(user_id)}, update_doc)
        
        if result.modified_count == 1:
            # 4. Invalidate the Redis cache
            redis_client.delete(f"user:{user_id}")
            print(f"User stats for {user_id} updated in MongoDB and cache invalidated.")
            return True
        else:
            print(f"User stats for {user_id} not modified.")
            return False
    except Exception as e:
        print(f"Failed to update user stats for {user_id}: {e}")
        return False

# --- Example of how to use the new function in your main script block ---
if __name__ == "__main__":
    # ... (your existing main script to connect and log in) ...
    users_collection = connect_to_mongodb(MONGO_URI, MONGO_DB_NAME, MONGO_COLLECTION_NAME)
    redis_client = connect_to_redis(REDIS_HOST, REDIS_PORT, REDIS_DB)

    if users_collection and redis_client:
        # --- Simulating a game session and updating score ---
        print("\n--- Simulating a game session and score update ---")
        
        # Assume a user is logged in and we have their user_id
        # Let's find the user we registered earlier
        user_name = "wurdo_player"
        existing_user = users_collection.find_one({'user_name': user_name})
        if existing_user:
            user_id = str(existing_user['_id'])
            
            # --- Scenario 1: A new high score ---
            game_results_1 = {
                'game_chain': {
                    'start_word': 'wurdo',
                    'chain_length': 5,
                    'words_in_chain': ['wurdo', 'urdo', 'rdo', 'do', 'o']
                },
                'game_score': 200
            }
            print(f"\nSubmitting first game results for user {user_id}...")
            update_user_game_stats(users_collection, redis_client, user_id, game_results_1)
            
            # --- Scenario 2: A score that is NOT a high score ---
            game_results_2 = {
                'game_chain': {
                    'start_word': 'less',
                    'chain_length': 4,
                    'words_in_chain': ['less', 'ess', 'ss', 's']
                },
                'game_score': 100
            }
            print(f"\nSubmitting second game results (not a high score)...")
            update_user_game_stats(users_collection, redis_client, user_id, game_results_2)

            # --- Verify the updates by fetching the user's data ---
            print("\n--- Verifying the final user stats ---")
            final_stats = users_collection.find_one({'_id': ObjectId(user_id)})
            if final_stats:
                # Remove password hash for safe printing
                del final_stats['password_hash']
                print(final_stats)
  
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
