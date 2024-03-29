from django.contrib import admin

from geeohdotnet import models


class ArticleAdmin(admin.ModelAdmin):
    list_display = ["id", "title", "description"]


admin.site.register(models.Motto)
admin.site.register(models.Article, ArticleAdmin)
