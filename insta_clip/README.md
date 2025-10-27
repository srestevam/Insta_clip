
# Clipping Insta-like (Flask + Excel)

Este projeto cria uma página web simples, no estilo do Instagram, para apresentar um **clipping** de postagens de atores da sua simulação.  
Todos os dados são lidos de um único arquivo **Excel** (uma postagem por linha).

## Como rodar

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/macOS
source .venv/bin/activate

pip install -r requirements.txt
python app.py
```

Acesse: http://localhost:5000

## Estrutura do Excel (`data/posts.xlsx`)

- Uma única planilha com **uma linha por postagem** e as seguintes colunas (campos **obrigatórios** marcados com `*`):

| Coluna | Descrição |
|---|---|
| `post_id` | Identificador único da postagem (texto ou número). |
| `actor_username`* | @usuário do ator (ex.: `mpl_topazio`). |
| `actor_name` | Nome público (ex.: `Movimento Peruíbe Livre`). |
| `actor_avatar_url` | URL da foto de perfil (ou deixe em branco para usar o placeholder). |
| `actor_bio` | Bio/descrição do ator. |
| `actor_followers` | Nº de seguidores deste ator (para a página de perfis). |
| `actor_following` | Nº de seguindo deste ator (para a página de perfis). |
| `post_image_url` | URL da imagem do post (ou deixe em branco para placeholder). |
| `post_caption` | Legenda do post. |
| `post_datetime` | Data/hora do post (qualquer formato reconhecido pelo Excel). |
| `likes`* | Número de curtidas. |
| `comments_count`* | Número total de comentários (pode ser maior que 10). |
| `shares_count`* | Número de compartilhamentos. |
| `comment_1` … `comment_10` | **Exatamente 10** comentários exemplificativos da postagem (texto). |

> Observação: a página de **Perfis** é construída ao agrupar por `actor_username` e usando a primeira ocorrência dos campos do ator (bio, avatar, etc.).

## Páginas
- **Feed** (`/`): lista as postagens com imagem, legenda, curtidas, nº de comentários e compartilhamentos.
- **Detalhe da Postagem** (`/post/<post_id>`): mostra a postagem e os **10 comentários exemplificativos**.
- **Perfis** (`/profiles`): catálogo dos atores (nome, @usuário, avatar, bio, nº de posts, seguidores, seguindo e uma miniatura do post mais recente).

## Personalização Rápida
- Estilos em `static/styles.css`.
- Imagens de placeholder em `static/images/placeholder.png` e `static/avatars/default.png`.
- Substitua `data/posts.xlsx` pelos seus dados reais.

## Licença
Livre para uso nos seus exercícios/simulações.
