def get_user(user_id):
    users = {
        "user1": {"region": "India", "age": 7},
        "user2": {"region": "India", "age": 16},
        "user3": {"region": "India", "age": 25},
        "user4": {"region": "USA", "age": 10},
        "user5": {"region": "USA", "age": 30},
    }

    if user_id not in users:
        raise ValueError("Invalid user")

    return users[user_id]