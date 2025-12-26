import os
import pymongo
from dotenv import load_dotenv

load_dotenv()

MONGO_URL = os.getenv('MONGO_URL')
DB_NAME = os.getenv('DB_NAME')

if not MONGO_URL or not DB_NAME:
    print("Error: MONGO_URL or DB_NAME not found in environment variables.")
    exit(1)

client = pymongo.MongoClient(MONGO_URL)
db = client[DB_NAME]

def remove_duplicates(collection_name):
    print(f"Checking {collection_name} for duplicates...")
    collection = db[collection_name]
    
    # Aggregation pipeline to find duplicates by 'id'
    pipeline = [
        {"$group": {
            "_id": "$id",
            "ids": {"$push": "$_id"},
            "count": {"$sum": 1}
        }},
        {"$match": {
            "count": {"$gt": 1}
        }}
    ]
    
    duplicates = list(collection.aggregate(pipeline))
    
    total_removed = 0
    if not duplicates:
        print(f"No duplicates found in {collection_name}.")
    
    for doc in duplicates:
        # Keep the first one (usually the oldest if _id is ObjectId and implicit sort, but here order doesn't strictly matter if data is identical)
        # To be safe, we keep the FIRST one in the array returned by $push
        ids_to_remove = doc['ids'][1:]
        
        if ids_to_remove:
            result = collection.delete_many({"_id": {"$in": ids_to_remove}})
            total_removed += result.deleted_count
            print(f"Removed {result.deleted_count} duplicates for id: {doc['_id']}")
        
    print(f"Total duplicates removed from {collection_name}: {total_removed}")
    
    # Create unique index to prevent future duplicates
    print(f"Creating unique index on 'id' for {collection_name}...")
    try:
        collection.create_index("id", unique=True)
        print("Index created.")
    except Exception as e:
        print(f"Error creating index: {e}")

if __name__ == "__main__":
    # Run for relevant collections
    remove_duplicates("courses")
    remove_duplicates("videos")
    remove_duplicates("quizzes")
    print("\nDone.")
