from django.contrib import admin

from geeohdotnet import models


class ArticleAdmin(admin.ModelAdmin):
    list_display = ["id", "title", "description"]


class MottoAdmin(admin.ModelAdmin):
    list_display = ["motto", "priority", "hidden"]


admin.site.register(models.Article, ArticleAdmin)
admin.site.register(models.Motto, MottoAdmin)
