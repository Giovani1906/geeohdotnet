from django.db import models
from django.utils import timezone
from markdown2 import markdown

from geeohdotnet.storage import OverwriteStorage


def _gen_pk():
    date = timezone.now()
    i = 1
    pk = int(f"{date.year}{date.month:02d}{date.day:02d}{i:02d}"[2:])
    while True:
        try:
            if Article.objects.get(pk=pk):
                i += 1
                pk = int(f"{date.year}{date.month:02d}{date.day:02d}{i:02d}"[2:])
        except models.ObjectDoesNotExist:
            break
    return pk


def _thumb_loc(instance, filename):
    return f'{instance.id}/thumb.{filename.split('.')[1]}'


def _banner_loc(instance, filename):
    return f'{instance.id}/banner.{filename.split('.')[1]}'


class Article(models.Model):
    id = models.IntegerField(
        default=_gen_pk, primary_key=True, editable=False, unique=True
    )
    date = models.DateField(default=timezone.now)
    title = models.CharField(max_length=30, unique=True)
    description = models.CharField(max_length=60)
    thumb = models.FileField(storage=OverwriteStorage, upload_to=_thumb_loc)
    banner = models.FileField(storage=OverwriteStorage, upload_to=_banner_loc)
    content = models.TextField()

    def __str__(self):
        return f"[{self.id}] {self.title}"

    @property
    def content_formatted(self):
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
        return markdown(self.content, extras=extras)


class Motto(models.Model):
    motto = models.CharField(max_length=40, unique=True)

    def __str__(self):
        return self.motto
