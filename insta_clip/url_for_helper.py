from flask import url_for

def resolve_img(path: str, is_avatar: bool = False) -> str:
    # vazio → placeholder local
    if not path or str(path).strip() == "":
        return url_for("static", filename="avatars/default.png" if is_avatar else "images/placeholder.png")
    # caminho local começando com /static/
    if str(path).startswith("/static/"):
        return url_for("static", filename=str(path).replace("/static/", "", 1))
    # URL externa (precisa ser https no Pages)
    return str(path)
