from unittest.mock import patch
from datetime import datetime

from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

import pytz
from requests.exceptions import Timeout

from .. import tasks
from .. import models
from . import samples


User = get_user_model()


class FeedTestCase(APITestCase):
    def setUp(self):
        user = User.objects.create(username='root')
        self.client.force_authenticate(user=user)

    @patch('reader.serializers.requests.get')
    def test_can_create_feed(self, mock_get):
        mock_get.return_value.content = samples.valid_feed
        data = {'url': 'http://planet.ubuntu.com/rss20.xml'}
        response = self.client.post(reverse('feeds-list'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(models.Feed.objects.count(), 1)
        feed = models.Feed.objects.get(url=data['url'])
        self.assertEqual(feed.url, data['url'])
        self.assertEqual(feed.title, 'Planet Ubuntu')
        self.assertEqual(feed.unique_name, 'planet.ubuntu.com-rss20.xml')

    @patch('reader.serializers.requests.get')
    def test_feed_is_unique(self, mock_get):
        mock_get.return_value.content = samples.valid_feed
        data = {'url': 'http://planet.ubuntu.com/rss20.xml'}
        response = self.client.post(reverse('feeds-list'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = self.client.post(reverse('feeds-list'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEqual(models.Feed.objects.count(), 1)
        self.assertEqual(models.Feed.objects.get().url, data['url'])

    def test_invalid_request_returns_400(self):
        data = [
            {'url': 'abc'},
            {'url': 'google/rss.xml'},
            {'url': 'http://foo'},
        ]
        for datum in data:
            response = self.client.post(reverse('feeds-list'), datum)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn(b'valid URL', response.content)

    @patch('reader.serializers.requests.get')
    def test_invalid_feed_returns_400(self, mock_get):
        mock_get.return_value.content = samples.invalid_feed
        data = {'url': 'http://planet.ubuntu.com/rss20.xml'}
        response = self.client.post(reverse('feeds-list'), data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(b'No feed found', response.content)

    @patch('reader.serializers.requests.get')
    def test_timeout_during_creation_returns_400(self, mock_response):
        mock_response.side_effect = Timeout
        data = {'url': 'http://planet.ubuntu.com/rss20.xml'}
        response = self.client.post(reverse('feeds-list'), data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(b'resolving', response.content)


class EntryTestCase(APITestCase):
    fixtures = ['users', 'feeds']

    @patch('reader.tasks.requests.get')
    def test_can_index_entries(self, mock_response):
        mock_response.return_value.content = samples.valid_feed
        tasks.feed_indexer('http://feed.com', 1)
        entry = models.Entry.objects.first()
        self.assertEqual(entry.feed_id, 1)
        self.assertEqual(entry.title, 'Kees Cook: package hardening asymptote')
        self.assertEqual(entry.link,
                         'https://outflux.net/blog/archives/2019/06/27/'
                         'package-hardening-asymptote/')
        self.assertEqual(entry.summary,
                         '<p>Forever ago I set up tooling to generate '
                         'graphs representing the adoption</p>')
        self.assertEqual(entry.published_at,
                         datetime(2019, 6, 27, 22, 35, 9, tzinfo=pytz.UTC))

    @patch('reader.tasks.requests.get')
    def test_update_timeout_is_penalized(self, mock_response):
        from requests.exceptions import Timeout
        feed = models.Feed.objects.get(id=1)
        self.assertEqual(feed.priority, 0)
        mock_response.side_effect = Timeout
        tasks.feed_indexer('http://feed.com', 1)
        feed.refresh_from_db()
        self.assertEqual(feed.priority, 1)

    @patch('reader.tasks.requests.get')
    def test_successful_update_is_rewarded(self, mock_response):
        mock_response.return_value.content = samples.valid_feed
        feed = models.Feed.objects.get(id=1)
        feed.decrement_priority()
        tasks.feed_indexer('http://feed.com', 1)
        feed.refresh_from_db()
        self.assertEqual(feed.priority, 0)

    @patch('reader.tasks.requests.get')
    def test_feed_priorty_cannot_be_negative(self, mock_response):
        mock_response.return_value.content = samples.valid_feed
        feed = models.Feed.objects.get(id=1)
        self.assertEqual(feed.priority, 0)
        tasks.feed_indexer('http://feed.com', 1)
        feed.refresh_from_db()
        self.assertEqual(feed.priority, 0)

    @patch('reader.tasks.requests.get')
    def test_no_pubdate_current_time_is_used_instead(self, mock_response):
        mock_response.return_value.content = samples.invalid_feed_no_pubdate
        tasks.feed_indexer('http://feed.com', 1)
        entry = models.Entry.objects.first()
        self.assertEqual(entry.published_at.date(), datetime.now().date())


class BookmarkTestCase(APITestCase):
    fixtures = ['users', 'feeds', 'entries']

    def setUp(self):
        self.user = User.objects.get(username='root')
        self.client.force_authenticate(user=self.user)

    def test_can_bookmark_entry(self):
        data = {
            'entry': 1
        }
        response = self.client.post(reverse('bookmarks-list'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_can_unbookmark_entry(self):
        data = {
            'entry': 1
        }
        response = self.client.post(reverse('bookmarks-list'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data = {
            'entry': 1,
            'is_bookmarked': False,
        }
        response = self.client.put(reverse('bookmarks-detail',
                                           args=[response.data['id']]), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['is_bookmarked'], False)

    def test_bookmarks_are_private_to_each_user(self):
        data = {
            'entry': 1
        }
        response = self.client.post(reverse('bookmarks-list'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = self.client.get(reverse('bookmarks-list'))
        self.assertEqual(response.data['count'], 1)
        user = User.objects.get(username='mahan')
        self.client.force_authenticate(user=user)
        response = self.client.get(reverse('bookmarks-list'))
        self.assertEqual(response.data['count'], 0)


class ReadTestCase(APITestCase):
    fixtures = ['users', 'feeds', 'entries']

    def setUp(self):
        user = User.objects.get(username='root')
        self.client.force_authenticate(user=user)

    def test_can_set_entry_as_read(self):
        data = {
            'entry': 1
        }
        response = self.client.post(reverse('reads-list'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_can_unread_entry(self):
        data = {
            'entry': 1
        }
        response = self.client.post(reverse('reads-list'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data = {
            'entry': 1,
            'is_read': False,
        }
        response = self.client.put(reverse('reads-detail',
                                           args=[response.data['id']]), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        read = models.Read.objects.get(pk=response.data['id'])
        self.assertEqual(read.is_read, False)


class CommentTestCase(APITestCase):
    fixtures = ['users', 'feeds', 'entries']

    def setUp(self):
        user = User.objects.get(username='root')
        self.client.force_authenticate(user=user)

    def test_can_comment_on_entry(self):
        data = {
            'entry': 1,
            'content': 'sample content',
        }
        response = self.client.post(reverse('comments-list'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        comment = models.Comment.objects.first()
        self.assertEqual(comment.content, data['content'])
        self.assertEqual(comment.author.username, 'root')

    def test_users_can_see_each_others_comments(self):
        data = {
            'entry': 1,
            'content': 'sample content',
        }
        response = self.client.post(reverse('comments-list'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = self.client.get(reverse('comments-list'))
        comment1 = response.data
        user = User.objects.get(username='mahan')
        self.client.force_authenticate(user=user)
        response = self.client.get(reverse('comments-list'))
        comment2 = response.data
        self.assertDictEqual(comment1, comment2)


class UserRegistrationTestCase(APITestCase):
    def test_can_register_user(self):
        data = {
            'username': 'foo',
            'password': 'secret123',
            'password_repeat': 'secret123',
        }
        response = self.client.post(reverse('signup'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_weak_password_is_rejected(self):
        data = {
            'username': 'foo',
            'password': '123',
            'password_repeat': '123',
        }
        response = self.client.post(reverse('signup'), data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(b'short', response.content)

    def test_passwords_match(self):
        data = {
            'username': 'foo',
            'password': 'secret123',
            'password_repeat': 'secret12',
        }
        response = self.client.post(reverse('signup'), data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(b'match', response.content)
