from django import forms
from django.shortcuts import get_object_or_404

from geeohdotnet.models import Article


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result


class ArticleForm(forms.Form):
    title = forms.CharField(max_length=30, required=False)
    description = forms.CharField(max_length=60, required=False)
    content = forms.CharField(widget=forms.Textarea, required=False)
    thumb = forms.FileField(required=False)
    banner = forms.FileField(required=False)
    article_files = MultipleFileField(required=False)

    def save_article(self) -> Article:
        kwargs = {
            "title": self.cleaned_data["title"],
            "description": self.cleaned_data["description"],
            "thumb": self.cleaned_data["thumb"],
            "banner": self.cleaned_data["banner"],
            "content": self.cleaned_data["content"],
        }

        article = Article(**kwargs)
        article.save()

        return article

    def update_article(self, pk: int) -> Article:
        article = get_object_or_404(Article, pk=pk)

        if self.cleaned_data["title"] != "":
            article.title = self.cleaned_data["title"]
        if self.cleaned_data["description"] != "":
            article.description = self.cleaned_data["description"]
        if self.cleaned_data["thumb"]:
            article.thumb = self.cleaned_data["thumb"]
        if self.cleaned_data["banner"]:
            article.banner = self.cleaned_data["banner"]
        if (
            self.cleaned_data["content"] != ""
            or self.cleaned_data["content"] != article.content
        ):
            article.content = self.cleaned_data["content"]

        article.save()

        return article
