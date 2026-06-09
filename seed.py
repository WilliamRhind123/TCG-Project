from app import app
from models import db, User, CollectionItem
from werkzeug.security import generate_password_hash
from datetime import datetime
import random


with app.app_context():

    #Clear data
    CollectionItem.query.delete()
    User.query.delete()

    db.session.commit()

    #Premade users

    users = [

        User(
            username="Red",
            password=generate_password_hash("123"),
            favourite_pokemon_id=6
        ),

        User(
            username="Blue",
            password=generate_password_hash("123"),
            favourite_pokemon_id=9
        ),

        User(
            username="Misty",
            password=generate_password_hash("123"),
            favourite_pokemon_id=121
        ),

        User(
            username="Brock",
            password=generate_password_hash("123"),
            favourite_pokemon_id=95
        ),

        User(
            username="Gary",
            password=generate_password_hash("123"),
            favourite_pokemon_id=130
        ),

        User(
            username="Master",
            password=generate_password_hash("123"),
            favourite_pokemon_id=150
        )

    ]

    for user in users:
        db.session.add(user)

    db.session.commit()

    #Pokemon collections

    collections = {

        "Red": [
            1, 4, 6, 7, 25, 39, 94, 150
        ],

        "Blue": [
            7, 8, 9, 54, 55, 131, 143
        ],

        "Misty": [
            54, 55, 60, 61, 62, 120, 121, 131
        ],

        "Brock": [
            74, 75, 76, 95, 111, 112
        ],

        "Gary": [
            1, 2, 3, 25, 26, 58, 59, 130
        ],

        "Master": list(range(1, 152))

    }

    #Add collection items

    for username, pokemon_ids in collections.items():

        user = User.query.filter_by(username=username).first()

        for pokemon_id in pokemon_ids:

            item = CollectionItem(

                user_id=user.id,

                pokemon_id=pokemon_id,

                quantity=random.randint(1, 5),

                created_at=datetime.utcnow()

            )

            db.session.add(item)

    db.session.commit()

    print("Database seeded successfully!")