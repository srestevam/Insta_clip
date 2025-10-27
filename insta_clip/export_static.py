from pathlib import Path
import shutil
import pandas as pd
from jinja2 import Environment, FileSystemLoader, select_autoescape

BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "data" / "posts.xlsx"
TEMPLATES_DIR = BASE_DIR / "templates_static"
STATIC_DIR = BASE_DIR / "static"
DIST_DIR = BASE_DIR / "dist"

def load_posts():
    if not DATA_FILE.exists():
        return [], {}
    df = pd.read_excel(DATA_FILE, sheet_name=0, engine="openpyxl")
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
    for ncol in ["likes","comments_count","shares_count","actor_followers","actor_following"]:
        df[ncol] = pd.to_numeric(df[ncol], errors="coerce").fillna(0).astype(int)

    posts = []
    for idx, row in df.iterrows():
        comments = [row.get(f"comment_{i}", "") for i in range(1, 11)]
        comments = [c for c in comments if isinstance(c, str) and c.strip()]
        posts.append({
            "post_id": str(row["post_id"]) if str(row["post_id"]).strip() else str(idx),
            "actor_username": row["actor_username"] or "usuario",
            "actor_name": row["actor_name"] or row["actor_username"] or "Usuário",
            "actor_avatar_url": row["actor_avatar_url"],
            "actor_bio": row["actor_bio"] or "",
            "actor_followers": int(row["actor_followers"]),
            "actor_following": int(row["actor_following"]),
            "post_image_url": row["post_image_url"],
            "post_caption": row["post_caption"] or "",
            "likes": int(row["likes"]),
            "comments_count": int(row["comments_count"]),
            "shares_count": int(row["shares_count"]),
            "comments": comments
        })

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
        if p["post_image_url"]:
            actors[key]["latest_post_image"] = p["post_image_url"]
    return posts, actors

def main():
    posts, actors = load_posts()

    if DIST_DIR.exists():
        shutil.rmtree(DIST_DIR)
    (DIST_DIR/"post").mkdir(parents=True, exist_ok=True)
    (DIST_DIR/"profiles").mkdir(parents=True, exist_ok=True)

    shutil.copytree(STATIC_DIR, DIST_DIR/"static")

    env = Environment(
        loader=FileSystemLoader(str(TEMPLATES_DIR)),
        autoescape=select_autoescape(['html', 'xml'])
    )

    # Raiz do site
    index_tpl = env.get_template("index.html")
    (DIST_DIR/"index.html").write_text(
        index_tpl.render(posts=posts, static_prefix="static/", root_prefix="", title="Clipping AZUVER — Feed"),
        encoding="utf-8"
    )

    profiles_tpl = env.get_template("profiles.html")
    (DIST_DIR/"profiles"/"index.html").write_text(
        profiles_tpl.render(actors=actors, static_prefix="static/", root_prefix="", title="Perfis"),
        encoding="utf-8"
    )

    post_tpl = env.get_template("post.html")
    for p in posts:
        (DIST_DIR/"post"/f"{p['post_id']}.html").write_text(
            post_tpl.render(post=p, static_prefix="../static/", root_prefix="../", title=f"Post • {p['actor_username']}"),
            encoding="utf-8"
        )

    print("Snapshot gerado em:", DIST_DIR)

if __name__ == "__main__":
    main()
