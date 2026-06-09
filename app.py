from flask import Flask, render_template, jsonify, request
from flask_login import LoginManager, login_required, current_user
import os
import json

from models import db, User, CollectionItem, Notification, TradeRequest
from auth.auth import auth_bp
from trade.trade import trade_bp
from feed.feed import feed_bp

app = Flask(__name__)

folder_path = os.path.dirname(os.path.abspath(__file__))

app.config["SECRET_KEY"] = "secret-key"
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{folder_path}/database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


app.register_blueprint(auth_bp)
app.register_blueprint(trade_bp)
app.register_blueprint(feed_bp)


with open("static/data/pokemon.json", "r", encoding="utf-8") as file:
    pokemon_data = json.load(file)


@app.context_processor
def inject_notifications():

    if current_user.is_authenticated:

        recent_notifications = Notification.query.filter_by(
            recipient_id=current_user.id
        ).order_by(
            Notification.created_at.desc()
        ).limit(5).all()

        unread_notification_count = Notification.query.filter_by(
            recipient_id=current_user.id,
            is_read=False
        ).count()

        return {
            "recent_notifications": recent_notifications,
            "unread_notification_count": unread_notification_count
        }

    return {
        "recent_notifications": [],
        "unread_notification_count": 0
    }


@app.route("/")
@login_required
def index():
    return render_template("index.html")


@app.route("/collection")
@login_required
def collection():
    user_collection = CollectionItem.query.filter_by(
        user_id=current_user.id
    ).all()

    owned = {}

    for item in user_collection:
        owned[int(item.pokemon_id)] = item.quantity

    total_pokemon = sum(owned.values())
    unique_pokemon = len(owned)
    completion_percentage = round((unique_pokemon / 151) * 100)

    most_owned_item = None
    newest_item = None

    if user_collection:
        most_owned_item = max(user_collection, key=lambda item: item.quantity)
        newest_item = max(user_collection, key=lambda item: item.created_at)

    def find_pokemon_name(pokemon_id):
        for pokemon in pokemon_data:
            if pokemon["id"] == int(pokemon_id):
                return pokemon["name"]["english"]
        return "Unknown"

    most_owned_name = find_pokemon_name(most_owned_item.pokemon_id) if most_owned_item else "None"
    newest_name = find_pokemon_name(newest_item.pokemon_id) if newest_item else "None"

    return render_template(
        "collection.html",
        pokemon_list=pokemon_data,
        owned=owned,
        total_pokemon=total_pokemon,
        unique_pokemon=unique_pokemon,
        completion_percentage=completion_percentage,
        most_owned_name=most_owned_name,
        newest_name=newest_name
    )


@app.route("/get_pokemon", methods=["POST"])
@login_required
def get_pokemon():
    data = request.json
    pokemon_name = data.get("name")

    for pokemon in pokemon_data:
        if pokemon["name"]["english"].lower() == pokemon_name.lower():
            return jsonify({
                "success": True,
                "pokemon": {
                    "id": pokemon["id"],
                    "name": pokemon["name"]["english"],
                    "type": pokemon["type"],
                    "species": pokemon["species"],
                    "description": pokemon["description"],
                    "height": pokemon["profile"]["height"],
                    "weight": pokemon["profile"]["weight"],
                    "image": f"/static/PokemonSpritesGen1/{pokemon['id']}.png"
                }
            })

    return jsonify({"success": False})


@app.route("/add_to_collection", methods=["POST"])
@login_required
def add_to_collection():

    data = request.json

    pokemon_id = int(data.get("pokemon_id"))

    item = CollectionItem.query.filter_by(
        user_id=current_user.id,
        pokemon_id=pokemon_id
    ).first()

    is_new_pokemon = False

    if item:
        item.quantity += 1

    else:
        is_new_pokemon = True

        item = CollectionItem(
            user_id=current_user.id,
            pokemon_id=pokemon_id,
            quantity=1
        )

        db.session.add(item)

    db.session.commit()

    user_collection = CollectionItem.query.filter_by(
        user_id=current_user.id
    ).all()

    achievement_messages = []

    scanned_pokemon = None

    for pokemon in pokemon_data:
        if pokemon["id"] == pokemon_id:
            scanned_pokemon = pokemon
            break

    #Type badges 

    if scanned_pokemon and is_new_pokemon:

        for poke_type in scanned_pokemon["type"]:

            unique_type_count = 0

            for collection_item in user_collection:

                for pokemon in pokemon_data:

                    if pokemon["id"] == int(collection_item.pokemon_id):

                        if poke_type in pokemon["type"]:

                            unique_type_count += 1

                        break

            badge_level = None

            if unique_type_count == 1:
                badge_level = "Bronze"

            elif unique_type_count == 3:
                badge_level = "Silver"

            elif unique_type_count == 5:
                badge_level = "Gold"

            if badge_level:

                achievement_message = (
                    f"You have achieved your {badge_level} "
                    f"unique {poke_type} type badge!"
                )

                achievement_messages.append(achievement_message)

                new_notification = Notification(
                    recipient_id=current_user.id,
                    message=achievement_message,
                    image=f"/static/Types/Icon/{poke_type}.png"
                )

                db.session.add(new_notification)

    #Unique Pokemon Badges

    unique_count = len(user_collection)

    unique_badge = None
    unique_image = None

    if unique_count == 5:
        unique_badge = "Bronze"
        unique_image = "/static/Badges/Unique/UniqueBronze.png"

    elif unique_count == 50:
        unique_badge = "Silver"
        unique_image = "/static/Badges/Unique/UniqueSilver.png"

    elif unique_count == 100:
        unique_badge = "Gold"
        unique_image = "/static/Badges/Unique/UniqueGold.png"

    if unique_badge and is_new_pokemon:

        achievement_message = (
            f"You have achieved your {unique_badge} "
            f"Unique Pokémon badge!"
        )

        achievement_messages.append(achievement_message)

        new_notification = Notification(
            recipient_id=current_user.id,
            message=achievement_message,
            image=unique_image
        )

        db.session.add(new_notification)

    #Collector badges 

    total_count = sum(collection_item.quantity for collection_item in user_collection)

    collector_badge = None
    collector_image = None

    if total_count == 30:
        collector_badge = "Bronze"
        collector_image = "/static/Badges/Collector/CollectorBronze.png"

    elif total_count == 500:
        collector_badge = "Silver"
        collector_image = "/static/Badges/Collector/CollectorSilver.png"

    elif total_count == 2000:
        collector_badge = "Gold"
        collector_image = "/static/Badges/Collector/CollectorGold.png"

    if collector_badge:

        achievement_message = (
            f"You have achieved your {collector_badge} "
            f"Collector badge!"
        )

        achievement_messages.append(achievement_message)

        new_notification = Notification(
            recipient_id=current_user.id,
            message=achievement_message,
            image=collector_image
        )

        db.session.add(new_notification)

    db.session.commit()

    return jsonify({
        "success": True,
        "quantity": item.quantity,
        "achievement_messages": achievement_messages
    })

@app.route("/profile")
@login_required
def profile():

    user_collection = CollectionItem.query.filter_by(
        user_id=current_user.id
    ).all()

    owned = {}

    for item in user_collection:
        owned[int(item.pokemon_id)] = item.quantity

    unique_pokemon_count = len(owned)
    total_pokemon_count = sum(owned.values())

    type_counts = {}
    type_pokemon = {}

    for item in user_collection:

        for pokemon in pokemon_data:

            if pokemon["id"] == int(item.pokemon_id):

                for poke_type in pokemon["type"]:

                    if poke_type not in type_counts:
                        type_counts[poke_type] = 0
                        type_pokemon[poke_type] = []

                    type_counts[poke_type] += 1

                    type_pokemon[poke_type].append({
                        "name": pokemon["name"]["english"],
                        "id": pokemon["id"],
                        "quantity": item.quantity
                    })

                break

    accepted_trades = TradeRequest.query.filter(
        (
            (TradeRequest.sender_id == current_user.id) |
            (TradeRequest.receiver_id == current_user.id)
        ) &
        (TradeRequest.status == "accepted")
    ).count()

    trade_badge = None
    trade_badge_image = None
    trade_ring = None

    if accepted_trades >= 20:
        trade_badge = "Gold"
        trade_badge_image = "/static/Badges/Trader/Gold.png"
        trade_ring = "gold-ring"

    elif accepted_trades >= 10:
        trade_badge = "Silver"
        trade_badge_image = "/static/Badges/Trader/Silver.png"
        trade_ring = "silver-ring"

    elif accepted_trades >= 5:
        trade_badge = "Bronze"
        trade_badge_image = "/static/Badges/Trader/Bronze.png"
        trade_ring = "bronze-ring"

    return render_template(
        "profile.html",
        type_counts=type_counts,
        type_pokemon=type_pokemon,
        pokemon_data=pokemon_data,
        owned=owned,
        unique_pokemon_count=unique_pokemon_count,
        total_pokemon_count=total_pokemon_count,
        accepted_trades=accepted_trades,
        trade_badge=trade_badge,
        trade_badge_image=trade_badge_image,
        trade_ring=trade_ring,
    )

@app.route("/user/<username>")
@login_required
def public_profile(username):
    viewed_user = User.query.filter_by(username=username).first_or_404()

    user_collection = CollectionItem.query.filter_by(
        user_id=viewed_user.id
    ).all()

    owned = {}

    for item in user_collection:
        owned[int(item.pokemon_id)] = item.quantity

    return render_template(
        "public_profile.html",
        viewed_user=viewed_user,
        pokemon_data=pokemon_data,
        owned=owned
    )

@app.route("/clear_notifications", methods=["POST"])
@login_required
def clear_notifications():

    Notification.query.filter_by(
        recipient_id=current_user.id,
        is_read=False
    ).update({"is_read": True})

    db.session.commit()

    return jsonify({"success": True}) 

@app.errorhandler(404)
def not_found(e):
    return render_template("404.html"), 404


if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=True)