from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path

from geeohdotnet import views

urlpatterns = [
    path("", views.ArticleListView.as_view(), name="index"),
    path("admin/", admin.site.urls, name="admin"),
    path("article/<int:pk>/", views.ArticleView.as_view(), name="article-id"),
    path(
        "article/<int:pk>/<slug:slug>/",
        views.ArticleView.as_view(),
        name="article-id-slug",
    ),
    path("article/<slug:slug>/", views.ArticleView.as_view(), name="article-slug"),
    path("publish/", views.ArticlePublishFormView.as_view(), name="publish"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
