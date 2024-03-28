from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from geeohdotnet import views

urlpatterns = [
    path("", views.ArticleListView.as_view(), name="index"),
    path("article/<int:pk>/", views.ArticleView.as_view(), name="article"),
    path("article/<int:pk>/<slug:slug>/", views.ArticleView.as_view(), name="article"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
