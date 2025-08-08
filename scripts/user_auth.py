import pymongo
import redis
import bcrypt
import json
import uuid
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
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

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
        'password_hash': hashed_password.decode('utf-8'),
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
    
    if check_password(password, user_document['password_hash']):
        session_token = str(uuid.uuid4())
        user_id_str = str(user_document['_id'])
        
        redis_client.setex(f"session:{session_token}", SESSION_TTL_SECONDS, user_id_str)
        
        del user_document['password_hash']
        user_document['_id'] = user_id_str
        
        return {'status': 'success', 'user': user_document, 'session_token': session_token}
    else:
        return {'status': 'error', 'message': f"Login failed: Incorrect password for user '{user_name}'."}

def get_user_from_session(mongo_collection, redis_client, session_token):
    """
    Verifies a session token and fetches the corresponding user's data from MongoDB.
    """
    user_id = redis_client.get(f"session:{session_token}")
    if user_id:
        user_document = mongo_collection.find_one({'_id': ObjectId(user_id)})
        if user_document:
            del user_document['password_hash']
            user_document['_id'] = str(user_document['_id'])
            return {'status': 'success', 'user': user_document}
    
    return {'status': 'error', 'message': 'Invalid or expired session token.'}

def logout_user(redis_client, session_token):
    """Deletes a session token from Redis to log the user out."""
    redis_client.delete(f"session:{session_token}")
    return {'status': 'success', 'message': 'Logged out successfully.'}

# --- User Stats Update Function ---
def update_user_game_stats(mongo_collection, redis_client, user_id, new_score_data):
    """
    Updates a user's game statistics in MongoDB and invalidates the Redis cache.
    """
    user_document = mongo_collection.find_one({'_id': ObjectId(user_id)})
    if not user_document:
        return False
    
    current_best_chain_length = user_document['best_chain']['chain_length']
    new_chain_data = new_score_data['game_chain']
    new_chain_length = new_chain_data['chain_length']
    new_total_score = user_document['total_score'] + new_score_data['game_score']
    new_games_played = user_document['games_played'] + 1
    
    update_doc = {
        '$set': {
            'total_score': new_total_score,
            'games_played': new_games_played
        }
    }

    if new_chain_length > current_best_chain_length:
        update_doc['$set']['best_chain'] = new_chain_data
        print(f"New high score! Updating best chain for user {user_id}.")

    try:
        result = mongo_collection.update_one({'_id': ObjectId(user_id)}, update_doc)
        
        if result.modified_count == 1:
            redis_client.delete(f"user:{user_id}")
            print(f"User stats for {user_id} updated in MongoDB and cache invalidated.")
            return True
        else:
            return False
    except Exception as e:
        print(f"Failed to update user stats for {user_id}: {e}")
        return False

# --- Main Script Execution (for demonstration) ---
if __name__ == "__main__":
    users_collection = connect_to_mongodb(MONGO_URI, MONGO_DB_NAME, MONGO_COLLECTION_NAME)
    redis_client = connect_to_redis(REDIS_HOST, REDIS_PORT, REDIS_DB)
    
    if not users_collection or not redis_client:
        exit()

    print("\n--- TEST: Registering a new user ---")
    register_result = register_user(users_collection, "wurdo_player", "super-secret-password")
    print(register_result)

    print("\n--- TEST: Logging in a new user ---")
    login_result = login_user(users_collection, redis_client, "wurdo_player", "super-secret-password")
    print(login_result)
    session_token = login_result.get('session_token')

    if session_token:
        print("\n--- TEST: Simulating a game session and score update ---")
        user_id = login_result['user']['_id']
        game_results_1 = {
            'game_chain': {
                'start_word': 'wurdo',
                'chain_length': 5,
                'words_in_chain': ['wurdo', 'urdo', 'rdo', 'do', 'o']
            },
            'game_score': 200
        }
        update_user_game_stats(users_collection, redis_client, user_id, game_results_1)

        print("\n--- Verifying the updated user stats ---")
        updated_user = get_user_from_session(users_collection, redis_client, session_token)
        print(updated_user)
