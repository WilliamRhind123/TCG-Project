from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models import db, User, FeedPost, FeedLike, FeedComment, Notification


feed_bp = Blueprint(
    "feed",
    __name__,
    template_folder="templates/feed"
)


@feed_bp.route("/feed")
@login_required
def feed():
    posts = FeedPost.query.order_by(
        FeedPost.created_at.desc()
    ).all()

    return render_template(
        "feed.html",
        posts=posts
    )


@feed_bp.route("/create_feed_post", methods=["POST"])
@login_required
def create_feed_post():
    content = request.form.get("content")

    if not content or not content.strip():
        flash("Post cannot be empty.", "danger")
        return redirect(url_for("feed.feed"))

    new_post = FeedPost(
        content=content.strip(),
        user_id=current_user.id
    )

    db.session.add(new_post)
    db.session.commit()

    flash("Post created!", "success")

    return redirect(url_for("feed.feed"))


@feed_bp.route("/like_feed_post/<int:post_id>", methods=["POST"])
@login_required
def like_feed_post(post_id):
    post = FeedPost.query.get_or_404(post_id)

    existing_like = FeedLike.query.filter_by(
        user_id=current_user.id,
        post_id=post.id
    ).first()

    liked = False

    if existing_like:
        db.session.delete(existing_like)
    else:
        liked = True

        new_like = FeedLike(
            user_id=current_user.id,
            post_id=post.id
        )

        db.session.add(new_like)

        if post.user_id != current_user.id:
            notification = Notification(
                recipient_id=post.user_id,
                sender_id=current_user.id,
                message=f"{current_user.username} liked your feed post.",
                image=f"/static/PokemonSpritesGen1/{current_user.favourite_pokemon_id}.png"
            )

            db.session.add(notification)

    db.session.commit()

    return jsonify({
        "success": True,
        "liked": liked,
        "like_count": len(post.likes)
    })

@feed_bp.route("/add_feed_comment/<int:post_id>", methods=["POST"])
@login_required
def add_feed_comment(post_id):
    post = FeedPost.query.get_or_404(post_id)

    data = request.get_json()
    content = data.get("content", "")

    if not content or not content.strip():
        return jsonify({"success": False, "error": "Comment cannot be empty."})

    new_comment = FeedComment(
        content=content.strip(),
        user_id=current_user.id,
        post_id=post.id
    )

    db.session.add(new_comment)

    if post.user_id != current_user.id:
        notification = Notification(
            recipient_id=post.user_id,
            sender_id=current_user.id,
            message=f"{current_user.username} commented on your feed post.",
            image=f"/static/PokemonSpritesGen1/{current_user.favourite_pokemon_id}.png"
        )

        db.session.add(notification)

    db.session.commit()

    return jsonify({
        "success": True,
        "comment": {
            "username": current_user.username,
            "profile_pic": f"/static/PokemonSpritesGen1/{current_user.favourite_pokemon_id}.png",
            "content": new_comment.content,
            "time": new_comment.created_at.strftime("%d %b %Y %H:%M")
        },
        "comment_count": len(post.comments)
    })