import json
import os
from random import choice

from django.views.generic import DetailView, ListView

from geeohdotnet import models

with open("mottos.json", "rb") as f:
    mottos = json.loads(f.read())


class ExtraContext:
    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context["css_age"] = f'?v={int(os.path.getmtime("static/style.css"))}'
        context["motto"] = choice(mottos["mottos"])
        return context


class ArticleListView(ExtraContext, ListView):
    model = models.Article


class ArticleView(ExtraContext, DetailView):
    model = models.Article
