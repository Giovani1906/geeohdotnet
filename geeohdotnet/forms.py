from django import forms

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
    title = forms.CharField(max_length=30)
    description = forms.CharField(max_length=60)
    content = forms.CharField(widget=forms.Textarea)
    thumb = forms.FileField(allow_empty_file=False)
    banner = forms.FileField(allow_empty_file=False)
    article_files = MultipleFileField(allow_empty_file=True)

    def save_article(self):
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
