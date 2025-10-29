from flask_frozen import Freezer
from app import app, load_posts  # ajuste se seu loader tiver outro nome

freezer = Freezer(app)

@freezer.register_generator
def post_detail():
    # Gera TODAS as rotas dinâmicas /post/<post_id>
    posts, _ = load_posts()
    for p in posts:
        yield {"post_id": p["post_id"]}

if __name__ == "__main__":
    freezer.freeze()  # saída padrão: ./build
