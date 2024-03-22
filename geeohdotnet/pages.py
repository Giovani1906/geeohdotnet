import os
import orjson as json
import hashlib
import datetime

from django.utils.text import slugify
from django.conf import settings
from django.shortcuts import render, redirect
from django.http import Http404, HttpRequest, HttpResponse, QueryDict
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from markdown2 import markdown
from random import choice

md_extra = [
    'break-on-newline', 'code-friendly', 'fenced-code-blocks',
    'footnotes', 'smarty-pants', 'spoiler', 'strike', 'tables'
]

with open('mottos.json', 'rb') as f:
    mottos = json.loads(f.read())


def find(predicate, items):
    for item in items:
        if predicate(item):
            return item
    return None


def get_context(**kwargs) -> dict:
    context = {'css_age': f'?v={int(os.path.getmtime("static/style.css"))}', 'motto': choice(mottos['mottos'])}
    context.update(**kwargs)
    return context


def get_articles() -> list[dict[str, str | int]]:
    try:
        with open('articles/index.json', 'rb') as data:
            return json.loads(data.read())['articles']
    except FileNotFoundError:
        if not os.path.exists('articles'):
            os.mkdir('articles')
        with open('articles/index.json', 'wb') as data:
            data.write(json.dumps({'articles': []}))
        return []


def _hash(text: str) -> str:
    hashed_data = hashlib.sha3_512(text.encode('utf8') + settings.SECRET_KEY.encode('utf8'))
    return hashed_data.hexdigest()


def index(request: HttpRequest):
    return render(request, 'index.html', get_context(articles=get_articles()))


def article(request: HttpRequest, article_id: int = None, article_title: str = None):
    article_data = find(lambda a: a['id'] == article_id, get_articles())

    if not article_data:
        raise Http404
    if article_title and article_title != slugify(article_data['title']):
        return redirect(f'/article/{article_id}/')

    with open(f'articles/{article_id}.md', 'rb') as article_raw:
        article_md = markdown(article_raw.read().decode('utf-8'), extras=md_extra)
    context = get_context(page='article', article=article_data, content=article_md)

    return render(request, 'article.html', context)


def article_redirect(request: HttpRequest, article_title: str):
    article_data = find(lambda a: slugify(a['title']) == article_title, get_articles())
    if not article_data:
        raise Http404
    return redirect(f'/article/{article_data['id']}/{article_title}/')


def auth(request: HttpRequest):
    if request.method == 'GET':
        return render(request, 'auth.html', get_context(page='authenticate'))
    elif request.method == 'POST':
        if request.user.is_authenticated:
            logout(request)
            return redirect('/auth/')

        kwargs = {
            'request': request,
            'username': request.POST['username'],
            'password': _hash(request.POST['password'])
        }
        user = authenticate(**kwargs)
        if user is not None:
            login(request, user)
            url = request.GET.get('next')
            if url:
                return redirect(url)
            return redirect('/auth/')
        else:
            context = get_context(message='Bad username and/or password.')
            return render(request, 'message.html', context, status=401)
    else:
        return render(request, '405.html', get_context(), status=405)


@login_required
def markdownify(request: HttpRequest):
    if request.method == 'POST':
        return HttpResponse(markdown(request.POST['content'], extras=md_extra))
    else:
        return render(request, '405.html', get_context(), status=405)


@login_required
def publish(request: HttpRequest):
    if request.method == 'GET':
        return render(request, 'publish.html', get_context(page='publish'))
    elif request.method == 'POST':
        date = datetime.datetime.now(datetime.UTC)
        articles = get_articles()
        iteration = 1
        article_id = int(f'{date.year}{date.month:02d}{date.day:02d}{iteration:02d}'[2:])
        while True:
            if find(lambda a: a['id'] == article_id, articles):
                iteration += 1
                article_id = int(f'{date.year}{date.month:02d}{date.day:02d}{iteration:02d}'[2:])
            else:
                break

        article_data = {
            'id': article_id,
            'date': f'{date.year}-{date.month:02d}-{date.day:02d}',
            'title': request.POST['title'],
            'description': request.POST['description'],
            'content': request.POST['content']
        }
        articles.insert(0, article_data)

        files = QueryDict(mutable=True)
        files.update(request.FILES)
        files = dict(files)
        os.makedirs(f'media/{article_id}')
        with open(f'media/{article_id}/thumbnail.png', 'wb') as thumbnail:
            thumbnail.write(files['thumbnail'][0].read())
        with open(f'media/{article_id}/banner.png', 'wb') as banner:
            banner.write(files['banner'][0].read())
        if 'article-files' in files:
            for file in files['article-files']:
                with open(f'media/{article_id}/{file.name}', 'wb') as art_file:
                    art_file.write(file.read())
        with open(f'articles/{article_id}.md', 'wb') as article_raw:
            article_raw.write(article_data.pop('content').encode('utf-8'))
        with open(f'articles/index.json', 'wb') as index_raw:
            index_raw.write(json.dumps({'articles': articles}))

        return redirect(f'/article/{article_id}/')
    else:
        return render(request, '405.html', get_context(), status=405)


@login_required
def edit(request: HttpRequest, article_id: int = None):
    if request.method == 'GET':
        article_data = find(lambda a: a['id'] == article_id, get_articles())

        if not article_data:
            raise Http404

        article_assets = os.listdir(f'media/{article_id}/')
        article_assets.remove('banner.png')
        article_assets.remove('thumbnail.png')

        with open(f'articles/{article_id}.md', 'rb') as article_raw:
            kwargs = {
                'page': 'edit',
                'article': article_data,
                'content': article_raw.read().decode('utf-8'),
                'assets': article_assets,
            }

        return render(request, 'edit.html', get_context(**kwargs))
    elif request.method == 'POST':
        articles = get_articles()
        article_data = dict(find(lambda a: a['id'] == article_id, articles))

        if not article_data:
            raise Http404

        article_index = articles.index(article_data)

        for k, v in request.POST.items():
            if k == 'title' and v != '':
                article_data['title'] = v
            elif k == 'description' and v != '':
                article_data['description'] = v
            elif v == 'to-be-deleted':
                os.remove(f'media/{article_id}/{k}')

        files = QueryDict(mutable=True)
        files.update(request.FILES)
        files = dict(files)

        if 'thumbnail' in files:
            with open(f'media/{article_id}/thumbnail.png', 'wb') as thumbnail:
                thumbnail.write(files['thumbnail'][0].read())
        if 'banner' in files:
            with open(f'media/{article_id}/banner.png', 'wb') as banner:
                banner.write(files['banner'][0].read())
        if 'article-files' in files:
            for file in files['article-files']:
                with open(f'media/{article_id}/{file.name}', 'wb') as art_file:
                    art_file.write(file.read())
        with open(f'articles/{article_id}.md', 'rb') as article_raw:
            if request.POST['content'] != '' or request.POST['content'] != article_raw.read().decode('utf-8'):
                with open(f'articles/{article_id}.md', 'wb') as replace_raw:
                    replace_raw.write(request.POST['content'].encode('utf-8'))

        if article_data != articles[article_index]:
            articles[article_index] = article_data
            with open(f'articles/index.json', 'wb') as index_raw:
                index_raw.write(json.dumps({'articles': articles}))

        return redirect(f'/article/{article_id}/')
    else:
        return render(request, '405.html', get_context(), status=405)
