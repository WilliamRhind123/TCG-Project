document.addEventListener("DOMContentLoaded", function () {
    attachLikeButtons();
    attachCommentForms();
    attachShowMoreButtons();
});

function attachLikeButtons() {
    const likeButtons = document.querySelectorAll(".feed-like-btn");

    likeButtons.forEach(button => {
        button.addEventListener("click", function () {
            const postId = this.dataset.postId;
            const postCard = document.getElementById("feed-post-" + postId);

            const heartIcon = postCard.querySelector(".feed-heart-icon");
            const likeCount = postCard.querySelector(".feed-like-count");

            fetch("/like_feed_post/" + postId, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-Requested-With": "XMLHttpRequest"
                }
            })
            .then(response => response.json())
            .then(data => {
                if (!data.success) {
                    return;
                }

                if (data.liked) {
                    heartIcon.src = "/static/hearts/FullHeart.png";
                } else {
                    heartIcon.src = "/static/hearts/EmptyHeart.png";
                }

                likeCount.textContent = data.like_count;
            })
            .catch(error => {
                console.error("Like error:", error);
            });
        });
    });
}

function attachCommentForms() {
    const commentForms = document.querySelectorAll(".feed-comment-form");

    commentForms.forEach(form => {
        form.addEventListener("submit", function (event) {
            event.preventDefault();

            const postId = this.dataset.postId;
            const postCard = document.getElementById("feed-post-" + postId);
            const input = this.querySelector(".feed-comment-input");
            const commentsList = postCard.querySelector(".feed-comments-list");
            const commentCount = postCard.querySelector(".feed-comment-count");

            fetch("/add_feed_comment/" + postId, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-Requested-With": "XMLHttpRequest"
                },
                body: JSON.stringify({
                    content: input.value
                })
            })
            .then(response => response.json())
            .then(data => {
                if (!data.success) {
                    alert(data.error);
                    return;
                }

                const newComment = document.createElement("div");
                newComment.className = "feed-comment";

                newComment.innerHTML = `
                    <img class="feed-comment-pic"
                         src="${data.comment.profile_pic}">

                    <div>
                        <strong>${data.comment.username}</strong>
                        <small>${data.comment.time}</small>
                        <p>${data.comment.content}</p>
                    </div>
                `;

                const hiddenComments =
                    postCard.querySelector(".hidden-comments");

                if (hiddenComments) {
                    hiddenComments.appendChild(newComment);
                } else {
                    commentsList.appendChild(newComment);
                }

                commentCount.textContent = data.comment_count;

                input.value = "";
            })
            .catch(error => {
                console.error("Comment error:", error);
            });
        });
    });
}

function attachShowMoreButtons() {
    const buttons = document.querySelectorAll(".show-more-comments-btn");

    buttons.forEach(button => {
        button.addEventListener("click", function () {
            const commentsSection = this.closest(".feed-comments-section");
            const hiddenComments = commentsSection.querySelector(".hidden-comments");

            if (hiddenComments.style.display === "none") {
                hiddenComments.style.display = "block";
                this.innerText = "Hide comments";
            } else {
                hiddenComments.style.display = "none";
                this.innerText = "Show all comments";
            }
        });
    });
}