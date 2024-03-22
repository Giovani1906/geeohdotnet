"""
URL configuration for geeohdotnet project.
"""
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from geeohdotnet import pages

urlpatterns = [
    path('', pages.index),
    path('article/<int:article_id>/', pages.article),
    path('article/<int:article_id>/edit/', pages.edit),
    path('article/<int:article_id>/<slug:article_title>/', pages.article),
    path('article/<slug:article_title>/', pages.article_redirect),
    path('auth/', pages.auth),
    path('markdownify/', pages.markdownify),
    path('publish/', pages.publish)
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
