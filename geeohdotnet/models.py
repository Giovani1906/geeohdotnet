from django.db import models
from markdown2 import markdown


class Article(models.Model):
    id = models.IntegerField(primary_key=True, editable=False, null=False, unique=True)
    date = models.DateField(null=False)
    title = models.CharField(max_length=30, null=False, unique=True)
    description = models.CharField(max_length=60, null=False)
    content = models.TextField(null=False)

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
