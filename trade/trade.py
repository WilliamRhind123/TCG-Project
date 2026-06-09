from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash
)

from flask_login import (
    login_required,
    current_user
)

from datetime import datetime

from models import (
    db,
    User,
    CollectionItem,
    Notification,
    TradeRequest
)

import json


trade_bp = Blueprint(
    "trade",
    __name__,
    template_folder="templates/trade"
)


with open("static/data/pokemon.json", "r", encoding="utf-8") as file:
    pokemon_data = json.load(file)

@trade_bp.route("/trade", methods=["GET", "POST"])
@login_required
def trade():

    search_name = ""

    results = []

    searched = False

    pokemon_exists = True

    if request.method == "POST":

        searched = True

        search_name = request.form["pokemon_name"].strip().lower()

        found_pokemon = None

        for pokemon in pokemon_data:

            if pokemon["name"]["english"].lower() == search_name:

                found_pokemon = pokemon

                break

        if not found_pokemon:

            pokemon_exists = False

        else:

            owners = CollectionItem.query.filter_by(
                pokemon_id=found_pokemon["id"]
            ).all()

            for item in owners:

                user = db.session.get(User, item.user_id)

                if user and user.id != current_user.id:

                    results.append({

                        "username": user.username,

                        "favourite_pokemon_id": user.favourite_pokemon_id,

                        "quantity": item.quantity,

                        "pokemon_name": found_pokemon["name"]["english"],

                        "pokemon_image":
                        f"/static/PokemonSpritesGen1/{found_pokemon['id']}.png"
                    })

    return render_template(

        "trade.html",

        results=results,

        searched=searched,

        search_name=search_name,

        pokemon_exists=pokemon_exists
    )


@trade_bp.route(
    "/request_trade/<receiver_username>/<pokemon_name>"
)
@login_required
def request_trade(receiver_username, pokemon_name):

    receiver = User.query.filter_by(
        username=receiver_username
    ).first_or_404()

    user_collection = CollectionItem.query.filter_by(
        user_id=current_user.id
    ).all()

    offered_pokemon = []

    for item in user_collection:

        for pokemon in pokemon_data:

            if pokemon["id"] == item.pokemon_id:

                offered_pokemon.append({

                    "id": pokemon["id"],

                    "name": pokemon["name"]["english"],

                    "quantity": item.quantity,

                    "image":
                    f"/static/PokemonSpritesGen1/{pokemon['id']}.png"

                })

                break

    return render_template(

        "request_trade.html",

        receiver=receiver,

        pokemon_name=pokemon_name,

        offered_pokemon=offered_pokemon
    )

@trade_bp.route("/send_trade_request", methods=["POST"])
@login_required
def send_trade_request():

    receiver_id = int(request.form["receiver_id"])

    requested_pokemon_name = request.form[
        "requested_pokemon_name"
    ]

    offered_pokemon_id = int(
        request.form["offered_pokemon_id"]
    )

    requested_pokemon = None

    for pokemon in pokemon_data:

        if pokemon["name"]["english"] == requested_pokemon_name:

            requested_pokemon = pokemon

            break

    if not requested_pokemon:

        flash("Pokemon not found.", "danger")

        return redirect(url_for("trade.trade"))

    trade_request = TradeRequest(

        sender_id=current_user.id,

        receiver_id=receiver_id,

        requested_pokemon_id=requested_pokemon["id"],

        offered_pokemon_id=offered_pokemon_id,

        status="pending"
    )

    db.session.add(trade_request)

    new_notification = Notification(

        recipient_id=receiver_id,

        sender_id=current_user.id,

        message=(
            f"{current_user.username} "
            f"sent you a trade request."
        ),

        image=(
            f"/static/PokemonSpritesGen1/"
            f"{offered_pokemon_id}.png"
        )
    )

    db.session.add(new_notification)

    db.session.commit()

    flash("Trade request sent!", "success")

    return redirect(url_for("trade.trade"))

def get_pokemon_name(pokemon_id):
    for pokemon in pokemon_data:
        if pokemon["id"] == int(pokemon_id):
            return pokemon["name"]["english"]
    return "Unknown"


def get_pokemon_image(pokemon_id):
    return f"/static/PokemonSpritesGen1/{pokemon_id}.png"


@trade_bp.route("/trade_requests")
@login_required
def trade_requests():

    incoming_requests = TradeRequest.query.filter_by(
        receiver_id=current_user.id,
        status="pending"
    ).order_by(
        TradeRequest.created_at.desc()
    ).all()

    return render_template(
        "trade_requests.html",
        incoming_requests=incoming_requests,
        get_pokemon_name=get_pokemon_name,
        get_pokemon_image=get_pokemon_image
    )


@trade_bp.route("/accept_trade/<int:trade_id>", methods=["POST"])
@login_required
def accept_trade(trade_id):

    trade = TradeRequest.query.get_or_404(trade_id)

    if trade.receiver_id != current_user.id:
        flash("You cannot accept this trade.", "danger")
        return redirect(url_for("trade.trade_requests"))

    sender_offered_item = CollectionItem.query.filter_by(
        user_id=trade.sender_id,
        pokemon_id=trade.offered_pokemon_id
    ).first()

    receiver_requested_item = CollectionItem.query.filter_by(
        user_id=trade.receiver_id,
        pokemon_id=trade.requested_pokemon_id
    ).first()

    if not sender_offered_item or not receiver_requested_item:
        flash("Trade failed because one Pokémon is missing.", "danger")
        return redirect(url_for("trade.trade_requests"))

    sender_offered_item.quantity -= 1
    receiver_requested_item.quantity -= 1

    if sender_offered_item.quantity <= 0:
        db.session.delete(sender_offered_item)

    if receiver_requested_item.quantity <= 0:
        db.session.delete(receiver_requested_item)

    sender_gets = CollectionItem.query.filter_by(
        user_id=trade.sender_id,
        pokemon_id=trade.requested_pokemon_id
    ).first()

    if sender_gets:
        sender_gets.quantity += 1
    else:
        sender_gets = CollectionItem(
            user_id=trade.sender_id,
            pokemon_id=trade.requested_pokemon_id,
            quantity=1
        )
        db.session.add(sender_gets)

    receiver_gets = CollectionItem.query.filter_by(
        user_id=trade.receiver_id,
        pokemon_id=trade.offered_pokemon_id
    ).first()

    if receiver_gets:
        receiver_gets.quantity += 1
    else:
        receiver_gets = CollectionItem(
            user_id=trade.receiver_id,
            pokemon_id=trade.offered_pokemon_id,
            quantity=1
        )
        db.session.add(receiver_gets)

    trade.status = "accepted"
    trade.completed_at = datetime.utcnow()

    sender_user = db.session.get(User, trade.sender_id)

    notification = Notification(
        recipient_id=trade.sender_id,
        sender_id=current_user.id,
        message=(
            f"{current_user.username} accepted your trade request. "
            f"You received {get_pokemon_name(trade.requested_pokemon_id)}."
        ),
        image=get_pokemon_image(trade.requested_pokemon_id)
    )

    db.session.add(notification)
    db.session.commit()

    flash("Trade accepted!", "success")

    return redirect(url_for("trade.trade_requests"))


@trade_bp.route("/decline_trade/<int:trade_id>", methods=["POST"])
@login_required
def decline_trade(trade_id):

    trade = TradeRequest.query.get_or_404(trade_id)

    if trade.receiver_id != current_user.id:
        flash("You cannot decline this trade.", "danger")
        return redirect(url_for("trade.trade_requests"))

    trade.status = "declined"
    trade.completed_at = datetime.utcnow()

    notification = Notification(
        recipient_id=trade.sender_id,
        sender_id=current_user.id,
        message=(
            f"{current_user.username} declined your trade request "
            f"for {get_pokemon_name(trade.requested_pokemon_id)}."
        ),
        image=get_pokemon_image(trade.requested_pokemon_id)
    )

    db.session.add(notification)
    db.session.commit()

    flash("Trade declined.", "warning")

    return redirect(url_for("trade.trade_requests"))


@trade_bp.route("/trade_history")
@login_required
def trade_history():

    trades = TradeRequest.query.filter(
        (TradeRequest.sender_id == current_user.id) |
        (TradeRequest.receiver_id == current_user.id)
    ).order_by(
        TradeRequest.created_at.desc()
    ).all()

    return render_template(
        "trade_history.html",
        trades=trades,
        get_pokemon_name=get_pokemon_name,
        get_pokemon_image=get_pokemon_image
    )