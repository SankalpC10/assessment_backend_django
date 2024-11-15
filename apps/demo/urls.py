from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'posts', views.PostViewSet, basename='post')

urlpatterns = [
    path('', include(router.urls)),
    path('posts/<uuid:post_id>/comments/', views.CreateCommentView.as_view(), name='create-comment')
]