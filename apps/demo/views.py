# TODO There's certainly more than one way to do this task, so take your pick.

from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework import status
from .serializers import PostSerializer
from rest_framework import generics
from drf_yasg.utils import swagger_auto_schema
from django.shortcuts import get_object_or_404
from drf_yasg import openapi
from .models import Post
from .serializers import PostCreateSerializer, CommentCreateSerializer


class PostPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class PostViewSet(viewsets.ModelViewSet):
    serializer_class = PostSerializer
    pagination_class = PostPagination

    def get_queryset(self):
        return Post.objects.select_related('user').prefetch_related(
            'comments__user'
        ).order_by('-timestamp')

    @swagger_auto_schema(
        operation_description="Get a paginated list of posts with their latest 3 comments",
        manual_parameters=[
            openapi.Parameter(
                'page',
                openapi.IN_QUERY,
                description="Page number",
                type=openapi.TYPE_INTEGER
            ),
            openapi.Parameter(
                'page_size',
                openapi.IN_QUERY,
                description="Number of posts per page",
                type=openapi.TYPE_INTEGER
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Create a new post",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['text'],
            properties={
                'text': openapi.Schema(type=openapi.TYPE_STRING)
            }
        ),
        responses={
            201: PostSerializer
        }
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)


class CreatePostView(generics.CreateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostCreateSerializer

    @swagger_auto_schema(
        operation_description="Create a new post",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['text'],
            properties={
                'text': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='The content of the post'
                )
            }
        ),
        responses={
            201: PostCreateSerializer,
            400: 'Bad Request - Invalid data'
        }
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class CreateCommentView(generics.CreateAPIView):
    serializer_class = CommentCreateSerializer

    @swagger_auto_schema(
        operation_description="Create a new comment on a post",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['text'],
            properties={
                'text': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='The content of the comment'
                )
            }
        ),
        responses={
            201: CommentCreateSerializer,
            404: 'Post not found',
            400: 'Bad Request - Invalid data'
        }
    )
    def post(self, request, post_id, *args, **kwargs):
        post = get_object_or_404(Post, id=post_id)

        # Add post_id to the request data
        request.data['post'] = post.id

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)