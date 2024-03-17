import os
import json
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


def get_articles() -> list:
    try:
        data = open('articles/index.json', 'rb').read()
        return json.loads(data)['articles']
    except FileNotFoundError:
        data = json.dumps({'articles': []}).encode('utf-8')
        if not os.path.exists('articles'):
            os.mkdir('articles')
        open('articles/index.json', 'wb').write(data)
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

    article_raw = open(f'articles/{article_id}.md', 'r', encoding='utf-8').read()
    article_md = markdown(article_raw, extras=md_extra)
    context = get_context(page='article', article=article_data, content=article_md)

    return render(request, 'article.html', context)


def article_redirect(request: HttpRequest, article_title: str):
    article_data = find(lambda a: slugify(a['title']) == article_title, get_articles())
    if not article_data:
        raise Http404
    return redirect(f'/article/{article_data["id"]}/{article_title}/')


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
        date = datetime.datetime.utcnow()
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
        open(f'media/{article_id}/thumbnail.png', 'wb').write(files['thumbnail'][0].read())
        open(f'media/{article_id}/banner.png', 'wb').write(files['banner'][0].read())
        if 'article-files' in files:
            for file in files['article-files']:
                open(f'media/{article_id}/{file.name}', 'wb').write(file.read())
        open(f'articles/{article_id}.md', 'wb').write(article_data.pop('content').encode('utf-8'))
        open(f'articles/index.json', 'wb').write(json.dumps({'articles': articles}).encode('utf-8'))

        return redirect(f'/article/{article_id}/')
