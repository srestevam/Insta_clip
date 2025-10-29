import os
from pathlib import Path
from flask import Flask, render_template, url_for
import pandas as pd
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "data" / "posts.xlsx"

# 1) (opcional, mas recomendado se você pretende congelar com Frozen-Flask)
#    static_url_path garante rota /static estável; FREEZER_RELATIVE_URLS ajuda no GitHub Pages.
app = Flask(__name__, static_url_path="/static")
app.config.update(FREEZER_RELATIVE_URLS=True)

# ---------- (NOVIDADE) Helpers p/ normalizar célula do Excel e resolver caminho de imagem ----------

def _norm_cell(val) -> str:
    """Normaliza valor vindo do Excel: vazios/NaN viram '', demais viram str.strip()."""
    if val is None:
        return ""
    # pandas pode trazer NaN como float
    try:
        if pd.isna(val):
            return ""
    except Exception:
        pass
    return str(val).strip()

def resolve_img(raw, is_avatar: bool = False) -> str:
    """
    Recebe o que veio do Excel (URL externa, '/static/...' ou vazio) e
    devolve uma URL pronta para <img src="...">:
      - vazio → placeholder local (avatars/default.png ou images/placeholder.png)
      - '/static/...' → usa url_for('static', filename=...)
      - 'static/...' (sem barra inicial) → também aceito
      - http(s)://... → retorna como está (prefira https em produção)
      - caso não reconheça → fallback para placeholder
    """
    raw = _norm_cell(raw)
    if raw == "":
        return url_for("static", filename="avatars/default.png" if is_avatar else "images/placeholder.png")

    if raw.startswith("/static/"):
        return url_for("static", filename=raw.replace("/static/", "", 1))

    if raw.startswith("static/"):
        return url_for("static", filename=raw.replace("static/", "", 1))

    if raw.startswith("http://") or raw.startswith("https://"):
        return raw

    # Se cair aqui, melhor garantir funcionamento com placeholder:
    return url_for("static", filename="avatars/default.png" if is_avatar else "images/placeholder.png")

# ---------- (NOVIDADE) Chave de ordenação estável ----------
def sort_key(p: dict):
    """
    Ordena por post_datetime desc; quando não houver data,
    considera Timestamp.min. Para manter estabilidade entre itens
    sem data (ou com a mesma data), usamos -source_index como desempate.
    (reverse=True abaixo inverterá a tupla inteira; por isso usamos índice negativo.)
    """
    dt = p.get("post_datetime")
    if not isinstance(dt, pd.Timestamp) or pd.isna(dt):
        dt = pd.Timestamp.min
    return (dt, -p.get("source_index", 0))

# ================================== CARGA DOS DADOS ==================================

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
                return pd.NaT
        df["post_datetime"] = df["post_datetime"].apply(_parse_dt)

    posts = []
    # ---------- (AJUSTE) enumerate para ter source_index (ordem original da planilha) ----------
    for i, (_, row) in enumerate(df.iterrows()):
        comments = [_norm_cell(row.get(f"comment_{k}", "")) for k in range(1, 11)]
        comments = [c for c in comments if c]

        # ---------- (AJUSTE) usar resolve_img para avatar e imagem do post ----------
        avatar_url = resolve_img(row.get("actor_avatar_url", ""), is_avatar=True)
        post_img_url = resolve_img(row.get("post_image_url", ""), is_avatar=False)

        post = {
            "source_index": i,  # para estabilidade da ordenação
            "post_id": _norm_cell(row["post_id"]) or str(i),
            "actor_username": _norm_cell(row["actor_username"]) or "usuario",
            "actor_name": _norm_cell(row["actor_name"]) or _norm_cell(row["actor_username"]) or "Usuário",
            "actor_avatar_url": avatar_url,
            "actor_bio": _norm_cell(row["actor_bio"]),
            "actor_followers": int(row["actor_followers"]),
            "actor_following": int(row["actor_following"]),
            "post_image_url": post_img_url,
            "post_caption": _norm_cell(row["post_caption"]),
            "post_datetime": row["post_datetime"],
            "likes": int(row["likes"]),
            "comments_count": int(row["comments_count"]),
            "shares_count": int(row["shares_count"]),
            "comments": comments,
        }
        posts.append(post)

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
                "latest_post_image": p["post_image_url"],
            }
        actors[key]["total_posts"] += 1
        actors[key]["total_likes"] += p["likes"]
        actors[key]["total_shares"] += p["shares_count"]
        actors[key]["latest_post_image"] = p["post_image_url"]

    return posts, actors

# ================================== ROTAS ==================================

# (Se você adotou a versão "sem clamp" na legenda no relatório, remova o clamp_text/prepare_for_report)

@app.route("/report")
def report():
    posts, _ = load_posts()

    # ---------- (AJUSTE) ordenação idêntica e estável ----------
    posts = sorted(posts, key=sort_key, reverse=True)

    # Se quiser sem cortes na legenda, NÃO aplique clamp aqui.
    # Se quiser "duas colunas por página", use o template/CSS de relatório que te enviei.
    pages = [posts[i:i+2] for i in range(0, len(posts), 2)]
    now_str = datetime.now().strftime("%d/%m/%Y %H:%M")
    return render_template("report.html", pages=pages, generated_at=now_str)

@app.route("/")
def index():
    posts, _ = load_posts()

    # ---------- (AJUSTE) ordenação idêntica e estável ----------
    posts_sorted = sorted(posts, key=sort_key, reverse=True)

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
