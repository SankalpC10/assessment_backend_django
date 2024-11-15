# TODO There's certainly more than one way to do this task, so take your pick.
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Post, Comment


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username']


class CommentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'text', 'timestamp', 'user']


class PostSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    comments = serializers.SerializerMethodField()
    comment_count = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ['id', 'text', 'timestamp', 'user', 'comments', 'comment_count']

    def get_comments(self, obj):
        comments = obj.comments.order_by('-timestamp')[:3]
        return CommentSerializer(comments, many=True).data

    def get_comment_count(self, obj):
        return obj.comments.count()

    def create(self, validated_data):
        # For testing, assign to the first user in the database
        user = User.objects.first()
        return Post.objects.create(user=user, **validated_data)


class PostCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['id', 'text', 'timestamp']
        read_only_fields = ['id', 'timestamp']

    def create(self, validated_data):
        # For testing, assign to the first user in the database
        user = User.objects.first()
        return Post.objects.create(user=user, **validated_data)


class CommentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'text', 'timestamp', 'post']
        read_only_fields = ['id', 'timestamp']

    def create(self, validated_data):
        user = User.objects.first()
        return Comment.objects.create(user=user, **validated_data)
