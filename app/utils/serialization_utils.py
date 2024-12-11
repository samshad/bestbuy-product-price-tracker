from typing import Any, Dict, List


def serialize_mongo_data(data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Convert ObjectId to string for each document in the list.

    Args:
        data (List[Dict[str, Any]]): List of documents from MongoDB.

    Returns:
        List[Dict[str, Any]]: List of documents with ObjectId converted to string.
    """
    for document in data:
        if "_id" in document:
            document["_id"] = str(document["_id"])
    return data
