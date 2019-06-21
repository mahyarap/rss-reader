from django.db.models import Prefetch

from rest_framework import generics
from rest_framework import viewsets
from rest_framework import permissions

from . import models
from . import serializers


class FeedViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.FeedSerializer

    def get_queryset(self):
        queryset = (
            models.Feed.objects
            .filter(subscribers=self.request.user)
            .all()
            .prefetch_related('subscribers')
            .prefetch_related('entry_set')
        )
        unique_name = self.request.query_params.get('unique_name')
        if unique_name:
            queryset = queryset.filter(unique_name=unique_name)
        return queryset


class EntryViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.EntrySerializer

    def get_queryset(self):
        owner = self.request.user
        queryset = (
            models.Entry.objects
            .all()
            .prefetch_related(
                Prefetch('read_set',
                         queryset=models.Read.objects.filter(owner=owner))
            )
            .prefetch_related(
                Prefetch('bookmark_set',
                         queryset=models.Bookmark.objects.filter(owner=owner))
            )
            .order_by('id')
        )
        feed_id = self.request.query_params.get('feed')
        if feed_id:
            queryset = queryset.filter(feed_id=feed_id)

        bookmarks = self.request.query_params.get('bookmarked')
        if bookmarks:
            queryset = queryset.filter(bookmark__owner=self.request.user)

        field = self.request.query_params.get('order_by')
        if field:
            queryset = queryset.order_by(field)
        return queryset


class ReadViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.ReadSerializer

    def get_queryset(self):
        queryset = models.Read.objects.filter(owner=self.request.user)
        entry_id = self.request.query_params.get('entry')
        if entry_id:
            queryset = queryset.filter(entry_id=entry_id)
        return queryset


class BookmarkViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.BookmarkSerializer

    def get_queryset(self):
        queryset = (
            models.Bookmark.objects
            .filter(owner=self.request.user).order_by('id')
        )
        entry_id = self.request.query_params.get('entry')
        if entry_id:
            queryset = queryset.filter(entry_id=entry_id)
        return queryset


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.CommentSerializer

    def get_queryset(self):
        queryset = models.Comment.objects.all().order_by('id')
        entry_id = self.request.query_params.get('entry')
        if entry_id:
            queryset = queryset.filter(entry_id=entry_id)
        return queryset


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.UserSerializer

    def get_queryset(self):
        queryset = models.User.objects.filter(pk=self.request.user.id)
        return queryset


class SignUpView(generics.CreateAPIView):
    serializer_class = serializers.UserRegistrationSerializer
    permission_classes = (permissions.AllowAny,)
