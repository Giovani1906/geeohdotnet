import os
import json
import datetime

from django.shortcuts import render, redirect
from django.http import Http404, HttpRequest, HttpResponse, QueryDict
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from markdown2 import markdown

md_extra = [
    'break-on-newline', 'code-friendly', 'fenced-code-blocks',
    'footnotes', 'smarty-pants', 'spoiler', 'strike', 'tables'
]


def find(predicate, items):
    for item in items:
        if predicate(item):
            return item
    return None


def get_articles() -> list:
    try:
        data = open('articles/index.json', 'rb').read()
        return json.loads(data)['articles']
    except FileNotFoundError:
        data = json.dumps('{"articles":[]}').encode('utf-8')
        os.mkdir('articles')
        open('articles/index.json', 'wb').write(data)
        return []


def index(request: HttpRequest):
    context = {
        'articles': get_articles(),
        'css_age': f'?v={int(os.path.getmtime("static/style.css"))}'
    }
    return render(request, 'index.html', context)


def article(request: HttpRequest, article_id: int):
    article_data = find(lambda a: a['id'] == article_id, get_articles())
    if not article_data:
        raise Http404
    article_raw = open(f'articles/{article_id}.md', 'r', encoding='utf-8').read()
    article_md = markdown(article_raw, extras=md_extra)
    context = {
        'article': article_data, 'content': article_md, 'css_age': f'?v={int(os.path.getmtime("static/style.css"))}'
    }

    return render(request, 'article.html', context)


def auth(request: HttpRequest):
    context = {'css_age': f'?v={int(os.path.getmtime("static/style.css"))}'}
    if request.method == 'GET':
        return render(request, 'auth.html', context)
    elif request.method == 'POST':
        if request.user.is_authenticated:
            logout(request)
            return redirect('/auth')
        user = authenticate(username=request.POST['username'], password=request.POST['password'])
        if user is not None:
            login(request, user)
            url = request.GET.get('next')
            if url:
                return redirect(url)
            return redirect('/auth')
        else:
            context['message'] = 'Bad username and/or password.'
            return render(request, 'message.html', context, status=401)
    else:
        return render(request, '405.html', context, status=405)


@login_required
def markdownify(request: HttpRequest):
    if request.method == 'POST':
        return HttpResponse(markdown(request.POST['content'], extras=md_extra))
    else:
        context = {'css_age': f'?v={int(os.path.getmtime("static/style.css"))}'}
        return render(request, '405.html', context, status=405)


@login_required
def publish(request: HttpRequest):
    if request.method == 'GET':
        context = {'css_age': f'?v={int(os.path.getmtime("static/style.css"))}'}
        return render(request, 'publish.html', context)
    elif request.method == 'POST':
        date = datetime.datetime.utcnow()
        articles = get_articles()
        iteration = 1
        article_id = int(f'{date.year}{date.month}{date.day}{iteration:02d}'[2:])
        while True:
            if find(lambda a: a['id'] == article_id, articles):
                iteration += 1
                article_id = int(f'{date.year}{date.month}{date.day}{iteration:02d}'[2:])
            else:
                break

        article_data = {
            'id': article_id,
            'date': f'{date.year}-{date.month}-{date.day}',
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
            for f in files['article-files']:
                open(f'media/{article_id}/{f.name}', 'wb').write(f.read())
        open(f'articles/{article_id}.md', 'wb').write(article_data.pop('content').encode('utf-8'))
        open(f'articles/index.json', 'wb').write(json.dumps({"articles": articles}).encode('utf-8'))

        return redirect(f'/article/{article_id}/')
