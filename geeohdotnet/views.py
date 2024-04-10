import os
from random import choice

from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.syndication.views import Feed
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.feedgenerator import Atom1Feed
from django.utils.text import slugify
from django.views.generic import DetailView, FormView, ListView
from markdown2 import markdown

from geeohdotnet import forms, models


def get_context(**kwargs) -> dict:
    mottos = models.Motto.objects.all()
    context = {
        "css_age": f'?v={os.path.getmtime("static/style.css"):.0f}',
        "motto": choice(mottos) if mottos else "I just don't know what went wrong!",
    }
    context.update(**kwargs)
    return context


def auth(request: HttpRequest):
    context = get_context()
    if request.method == "GET":
        return render(request, "geeohdotnet/auth.html", context)
    elif request.method == "POST":
        if request.user.is_authenticated:
            logout(request)
            return redirect("/auth/")

        kwargs = {
            "request": request,
            "username": request.POST["username"],
            "password": request.POST["password"],
        }
        user = authenticate(**kwargs)
        if user is not None:
            login(request, user)
            if "next" in request.GET:
                return redirect(request.GET["next"])
            return redirect("/auth/")
        else:
            context["title"] = "Unauthorized"
            context["message"] = "Bad username and/or password."
            return render(request, "message.html", context, status=401)
    else:
        return render(request, "405.html", context, status=405)


@login_required
def markdownify(request: HttpRequest):
    if request.method == "POST":
        extras = [
            "break-on-newline",
            "code-friendly",
            "fenced-code-blocks",
            "footnotes",
            "smarty-pants",
            "spoiler",
            "strike",
            "tables",
        ]
        return HttpResponse(markdown(request.POST["content"], extras=extras))
    else:
        return render(request, "405.html", get_context(), status=405)


class ExtraContext:
    def get_context_data(self, *, object_list=None, **kwargs):
        context = get_context(**super().get_context_data(**kwargs))
        context["page_type"] = self.__class__.__name__

        if isinstance(self, ArticleEditFormView):
            article = get_object_or_404(models.Article, pk=self.kwargs.get("pk", None))
            context["article"] = article
            assets = os.listdir(os.path.join(settings.MEDIA_ROOT, f"{article.id}/"))
            assets.remove("banner.png")
            assets.remove("thumb.png")
            context["assets"] = assets

        return context


class ArticleListView(ExtraContext, ListView):
    model = models.Article
    context_object_name = "article_list"


class ArticleDetailView(ExtraContext, DetailView):
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
        if isinstance(self, ArticleEditFormView):
            article = form.update_article(pk=self.kwargs.get("pk", None))
            for k, v in form.data.items():
                if v == "to-be-deleted":
                    path = os.path.join(settings.MEDIA_ROOT, f"{article.id}/{k}")
                    os.remove(path)
        else:
            article = form.save_article()

        for f in form.cleaned_data["article_files"]:
            path = os.path.join(settings.MEDIA_ROOT, f"{article.id}/{f.name}")
            with open(path, "wb") as art_file:
                art_file.write(f.read())

        self.success_url = f"/article/{article.id}/"

        return super().form_valid(form)


class ArticleEditFormView(ArticlePublishFormView):
    template_name = "geeohdotnet/article_edit.html"


class Atom2Feed(Atom1Feed):
    content_type = "text/xml"

    def add_item_elements(self, handler, item):
        super().add_item_elements(handler, item)
        if "content" in item:
            handler.addQuickElement("content", item["content"], {"type": "html"})


class AtomFeed(Feed):
    feed_type = Atom2Feed
    title = "geeoh.net"
    link = "/"
    subtitle = "A place where I ramble about random stuff. Mostly tech related."
    language = "en"

    @staticmethod
    def items():
        return reversed(models.Article.objects.all())

    def item_guid(self, item: models.Article) -> int:
        return item.id

    def item_title(self, item: models.Article) -> str:
        return item.title

    def item_description(self, item: models.Article) -> str:
        return item.description

    def item_link(self, item: models.Article) -> str:
        return f"/article/{item.id}/{slugify(item.title)}/"

    def item_extra_kwargs(self, item: models.Article) -> dict[str, str]:
        return {"content": item.content_formatted}
