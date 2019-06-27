import logging
from urllib.parse import urlparse

from django.db import transaction
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

from rest_framework import serializers

import requests
import feedparser
from requests.exceptions import Timeout, ConnectionError
from requests.utils import prepend_scheme_if_needed

from . import tasks
from . import models


User = get_user_model()
logger = logging.getLogger(__name__)


class FeedSerializer(serializers.ModelSerializer):
    title = serializers.CharField(max_length=128, required=False)
    unique_name = serializers.CharField(max_length=200, required=False)
    priority = serializers.IntegerField(required=False)
    unread_count = serializers.SerializerMethodField()

    class Meta:
        model = models.Feed
        fields = (
            'id', 'subscribers', 'unique_name', 'title', 'url', 'priority',
            'created_at', 'updated_at', 'unread_count'
        )
        validators = []

    def to_internal_value(self, data):
        data['subscribers'] = [self.context['request'].user.id]
        url = data.get('url')
        if url:
            data['url'] = prepend_scheme_if_needed(data['url'], 'http')
        return super().to_internal_value(data)

    @transaction.atomic
    def create(self, validated_data):
        subscribers = validated_data.pop('subscribers')
        try:
            resp = requests.get(validated_data['url'], timeout=3)
        except Timeout:
            logger.warning(
                'Timeout during creating feed: {}'.format(validated_data['url'])
            )
            raise serializers.ValidationError(
                {'none_field_errors': ['Error resolving URL']}
            )
        except ConnectionError:
            logger.warning(
                'Connection error during creating feed: {}'.format(
                    validated_data['url'])
            )
            raise serializers.ValidationError(
                {'none_field_errors': ['Error resolving URL']}
            )

        parsed_feed = feedparser.parse(resp.content)
        if parsed_feed.bozo == 1:
            logger.warning(
                'Feed is malformed: {}'.format(validated_data['url'])
            )
            raise serializers.ValidationError(
                {'none_field_errors': ['No feed found']}
            )
        parsed_url = urlparse(validated_data['url'])
        unique_name = (parsed_url.netloc + parsed_url.path).replace('/', '-')
        feed, created = models.Feed.objects.get_or_create(
            unique_name=unique_name,
            defaults={'title': parsed_feed.feed.title,
                      'url': validated_data['url']}
        )
        feed.subscribers.add(*subscribers)
        tasks.feed_indexer.delay(feed.url, feed.id)
        return feed

    def get_unread_count(self, obj):
        user = self.context['request'].user
        all_entries = obj.entry_set.count()
        reads = models.Entry.objects.filter(feed=obj,
                                            read__owner=user,
                                            read__is_read=True).count()
        return all_entries - reads


class EntrySerializer(serializers.ModelSerializer):
    is_read = serializers.SerializerMethodField()
    is_bookmarked = serializers.SerializerMethodField()

    class Meta:
        model = models.Entry
        fields = (
            'id', 'feed', 'slug', 'title', 'subtitle', 'link', 'author',
            'content', 'summary', 'created_at', 'published_at', 'is_read',
            'is_bookmarked',
        )

    def get_is_read(self, obj):
        return obj.read_set.exists()

    def get_is_bookmarked(self, obj):
        return obj.bookmark_set.exists()


class BookmarkSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Bookmark
        fields = (
            'id', 'owner', 'entry', 'is_bookmarked',
        )

    def to_internal_value(self, data):
        data['owner'] = self.context['request'].user.id
        return super().to_internal_value(data)


class ReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Read
        fields = (
            'id', 'owner', 'entry', 'is_read',
        )

    def to_internal_value(self, data):
        data['owner'] = self.context['request'].user.id
        return super().to_internal_value(data)


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=128, write_only=True)
    password_repeat = serializers.CharField(max_length=128, write_only=True)

    class Meta:
        model = User
        fields = (
            'username', 'password', 'password_repeat',
        )

    def validate(self, data):
        if data['password'] != data['password_repeat']:
            raise serializers.ValidationError('Passwords do not match')
        validate_password(data['password'])
        data.pop('password_repeat')
        return data

    def create(self, validated_data):
        user = User.objects.create(username=validated_data['username'])
        user.set_password(validated_data['password'])
        user.save()
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id', 'username', 'first_name', 'last_name', 'email',
        )


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Comment
        fields = (
            'id', 'author', 'entry', 'content', 'created_at', 'updated_at',
        )

    def to_internal_value(self, data):
        data['author'] = self.context['request'].user.id
        return super().to_internal_value(data)

    def to_representation(self, obj):
        comment = super().to_representation(obj)
        user = UserSerializer(instance=obj.author)
        comment['author'] = user.data
        return comment
