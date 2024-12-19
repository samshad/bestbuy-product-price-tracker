import redis
from redis.exceptions import ConnectionError  # Correct import for ConnectionError


# Connect to Redis Server
def connect_redis():
    """Connect to the running Redis server."""
    try:
        client = redis.Redis(
            host="localhost",  # Redis server hostname
            port=6379,  # Redis server port
            db=0,  # Default Redis database
            decode_responses=True,  # Decode byte responses into strings
        )
        # Test connection
        client.ping()
        print("✅ Connected to Redis successfully!")
        return client
    except ConnectionError as e:
        print("❌ Could not connect to Redis:", e)
        return None


# Perform CRUD operations on Redis
def test_redis(client):
    print("\n🔧 Testing Redis CRUD Operations\n")

    # 1. Create/Set key-value pair
    print("➕ Setting key: 'name' -> 'Alice'")
    client.set("name", "Alice")

    # 2. Read/Get key
    value = client.get("name")
    print(f"🔍 Getting key 'name': {value}")

    # 3. Update key (overwrite the value)
    print("🔄 Updating key: 'name' -> 'Bob'")
    client.set("name", "Bob")
    value = client.get("name")
    print(f"🔍 Getting updated key 'name': {value}")

    # 4. Delete key
    print("🗑️ Deleting key: 'name'")
    client.delete("name")
    value = client.get("name")
    print(f"🔍 Getting deleted key 'name': {value}")

    # 5. Working with lists
    print("\n📋 Testing Lists in Redis")
    client.rpush("fruits", "apple", "banana", "cherry")  # Push multiple items
    print("➕ Pushed ['apple', 'banana', 'cherry'] into list 'fruits'")
    fruits = client.lrange("fruits", 0, -1)
    print(f"🔍 Contents of 'fruits' list: {fruits}")

    # Pop an item
    removed_item = client.lpop("fruits")
    print(f"🗑️ Removed first item from 'fruits': {removed_item}")
    fruits = client.lrange("fruits", 0, -1)
    print(f"🔍 Updated contents of 'fruits' list: {fruits}")


# Main function
if __name__ == "__main__":
    redis_client = connect_redis()
    # if redis_client:
    #     test_redis(redis_client)

    redis_client.set("id", 1)
    print(redis_client.get("id"))  # Output: b'1'

    redis_client.set("id", 2)
    redis_client.set("id", 3)

    redis_client.set("phone", {"abc": 123, "def": 456, "ghi": 789})
