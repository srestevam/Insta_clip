
import os
from pathlib import Path
from flask import Flask, render_template, url_for
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "data" / "posts.xlsx"

app = Flask(__name__)

def load_posts():
    if not DATA_FILE.exists():
        return [], {}

    df = pd.read_excel(DATA_FILE, sheet_name=0, engine="openpyxl")
    # Normalize expected columns
    expected = [
        "post_id","actor_username","actor_name","actor_avatar_url","actor_bio",
        "actor_followers","actor_following","post_image_url","post_caption",
        "post_datetime","likes","comments_count","shares_count",
        "comment_1","comment_2","comment_3","comment_4","comment_5",
        "comment_6","comment_7","comment_8","comment_9","comment_10"
    ]
    for col in expected:
        if col not in df.columns:
            df[col] = None

    df = df.fillna("")
    # Ensure numeric
    for ncol in ["likes","comments_count","shares_count","actor_followers","actor_following"]:
        df[ncol] = pd.to_numeric(df[ncol], errors="coerce").fillna(0).astype(int)

    # Parse datetime if provided
    if "post_datetime" in df.columns:
        def _parse_dt(x):
            try:
                return pd.to_datetime(x)
            except Exception:
                return ""
        df["post_datetime"] = df["post_datetime"].apply(_parse_dt)

    posts = []
    for _, row in df.iterrows():
        comments = [row.get(f"comment_{i}", "") for i in range(1, 11)]
        comments = [c for c in comments if isinstance(c, str) and c.strip()]
        posts.append({
            "post_id": str(row["post_id"]) if row["post_id"] != "" else str(_),
            "actor_username": row["actor_username"] or "usuario",
            "actor_name": row["actor_name"] or row["actor_username"] or "Usuário",
            "actor_avatar_url": row["actor_avatar_url"] or url_for("static", filename="avatars/default.png"),
            "actor_bio": row["actor_bio"] or "",
            "actor_followers": int(row["actor_followers"]),
            "actor_following": int(row["actor_following"]),
            "post_image_url": row["post_image_url"] or url_for("static", filename="images/placeholder.png"),
            "post_caption": row["post_caption"] or "",
            "post_datetime": row["post_datetime"],
            "likes": int(row["likes"]),
            "comments_count": int(row["comments_count"]),
            "shares_count": int(row["shares_count"]),
            "comments": comments
        })

    # Build actor profiles
    actors = {}
    for p in posts:
        key = p["actor_username"]
        if key not in actors:
            actors[key] = {
                "actor_username": key,
                "actor_name": p["actor_name"],
                "actor_avatar_url": p["actor_avatar_url"],
                "actor_bio": p["actor_bio"],
                "actor_followers": p["actor_followers"],
                "actor_following": p["actor_following"],
                "total_posts": 0,
                "total_likes": 0,
                "total_shares": 0,
                "latest_post_image": p["post_image_url"]
            }
        actors[key]["total_posts"] += 1
        actors[key]["total_likes"] += p["likes"]
        actors[key]["total_shares"] += p["shares_count"]
        # Keep the newest preview image if possible
        actors[key]["latest_post_image"] = p["post_image_url"]

    return posts, actors

@app.route("/")
def index():
    posts, _ = load_posts()
    # sort by datetime desc if available, else as-is
    try:
        posts_sorted = sorted(posts, key=lambda x: (x["post_datetime"] if x["post_datetime"] != "" else pd.Timestamp.min), reverse=True)
    except Exception:
        posts_sorted = posts
    return render_template("index.html", posts=posts_sorted)

@app.route("/post/<post_id>")
def post_detail(post_id):
    posts, _ = load_posts()
    post = next((p for p in posts if str(p["post_id"]) == str(post_id)), None)
    if not post:
        return render_template("not_found.html"), 404
    return render_template("post.html", post=post)

@app.route("/profiles")
def profiles():
    _, actors = load_posts()
    return render_template("profiles.html", actors=actors)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
