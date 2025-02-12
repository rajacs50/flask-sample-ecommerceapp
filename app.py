# app.py
from flask import Flask, render_template, request, redirect, url_for
import redis
import json
from datetime import datetime
import time
import uuid

app = Flask(__name__)

# Redis configuration
REDIS_CONFIG = {
    'host': 'localhost',
    'port': 6379,
    'db': 0,
    'decode_responses': True  # This ensures Redis returns strings instead of bytes
}

def get_redis_connection():
    try:
        return redis.Redis(**REDIS_CONFIG)
    except redis.RedisError as e:
        print(f"Error connecting to Redis: {e}")
        return None

# Initialize Redis with sorted set for timestamps and hash for items
def init_redis():
    r = get_redis_connection()
    if r:
        try:
            # Create a test key to verify connection
            r.set('test_connection', 'ok', ex=1)
            print("Redis connection successful")
        except redis.RedisError as e:
            print(f"Error initializing Redis: {e}")

# Helper function to format item for template
def format_item(item_id, item_data):
    data = json.loads(item_data)
    return {
        'id': item_id,
        'name': data['name'],
        'description': data['description'],
        'created_at': datetime.fromtimestamp(data['created_at']).strftime('%Y-%m-%d %H:%M:%S')
    }

# Routes
@app.route('/')
def index():
    r = get_redis_connection()
    items = []
    if r:
        try:
            # Get all items from Redis
            pattern = "item:*"
            item_keys = r.keys(pattern)
            
            # Get all items and their data
            items_data = []
            for key in item_keys:
                item_data = r.get(key)
                if item_data:
                    data = json.loads(item_data)
                    items_data.append((key, data['created_at'], item_data))
            
            # Sort by created_at timestamp (newest first)
            items_data.sort(key=lambda x: x[1], reverse=True)
            
            # Format items for template
            items = [
                format_item(key.split(':')[1], item_data)
                for key, _, item_data in items_data
            ]
            
        except redis.RedisError as e:
            print(f"Error fetching items: {e}")
            
    return render_template('index.html', items=items)

@app.route('/add', methods=['POST'])
def add_item():
    r = get_redis_connection()
    if r:
        try:
            name = request.form.get('name')
            description = request.form.get('description')
            
            # Generate unique ID
            item_id = str(uuid.uuid4())
            
            # Create item data
            item_data = {
                'name': name,
                'description': description,
                'created_at': time.time()
            }
            
            # Store in Redis
            r.set(f'item:{item_id}', json.dumps(item_data))
            
        except redis.RedisError as e:
            print(f"Error adding item: {e}")
            
    return redirect(url_for('index'))

@app.route('/delete/<item_id>')
def delete_item(item_id):
    r = get_redis_connection()
    if r:
        try:
            # Delete the item
            r.delete(f'item:{item_id}')
        except redis.RedisError as e:
            print(f"Error deleting item: {e}")
            
    return redirect(url_for('index'))

if __name__ == '__main__':
    init_redis()
    app.run(host="0.0.0.0", port=5005, debug=True)