from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from django.views.decorators.cache import cache_page

from geeohdotnet import views

urlpatterns = [
    path("", views.ArticleListView.as_view(), name="index"),
    path("auth/", views.auth, name="auth"),
    path("admin/", admin.site.urls, name="admin"),
    path("article/<int:pk>/", views.ArticleDetailView.as_view(), name="article-id"),
    path(
        "article/<int:pk>/edit/",
        views.ArticleEditFormView.as_view(),
        name="article-edit",
    ),
    path(
        "article/<int:pk>/<slug:slug>/",
        views.ArticleDetailView.as_view(),
        name="article-id-slug",
    ),
    path(
        "article/<slug:slug>/", views.ArticleDetailView.as_view(), name="article-slug"
    ),
    path("feed/", cache_page(None, key_prefix="feed")(views.AtomFeed()), name="feed"),
    path("markdownify/", views.markdownify),
    path("publish/", views.ArticlePublishFormView.as_view(), name="article-publish"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
