import os
from random import choice

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView, FormView, ListView

from geeohdotnet import forms, models


class ExtraContext:
    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context["css_age"] = f'?v={os.path.getmtime("static/style.css"):.0f}'
        mottos = models.Motto.objects.all()
        context["motto"] = (
            choice(mottos) if mottos else "I just don't know what went wrong!"
        )
        return context


class ArticleListView(ExtraContext, ListView):
    model = models.Article
    context_object_name = "article_list"


class ArticleView(ExtraContext, DetailView):
    model = models.Article


class ArticlePublishFormView(ExtraContext, LoginRequiredMixin, FormView):
    form_class = forms.ArticleForm
    template_name = "geeohdotnet/article_publish.html"

    def post(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        article = form.save_article()
        files = form.cleaned_data["article_files"]
        for f in files:
            path = os.path.join(settings.MEDIA_ROOT, f"{article.id}/{f.name}")
            with open(path, "wb") as art_file:
                art_file.write(f.read())
        self.success_url = f"/article/{article.id}/"
        return super().form_valid(form)
