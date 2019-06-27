import time 
import uuid
import logging
from datetime import datetime

from django.utils.text import slugify

import pytz
import requests
import feedparser
from requests.exceptions import Timeout
from celery import group, shared_task, current_app

from . import models


logger = logging.getLogger(__name__)


@shared_task
def feed_indexer_coordinator(priority):
    if priority == 'HIGH':
        feeds_count = models.Feed.objects.filter(priority=0).count()
    elif priority == 'MEDIUM':
        feeds_count = models.Feed.objects.filter(priority=1).count()
    elif priority == 'LOW':
        feeds_count = models.Feed.objects.filter(priority__gte=2).count()
    else:
        raise ValueError('Proirity not provided')

    def interval_seq(start, stop, step=1):
        i = start
        while (i + step) < stop:
            yield i, i+step
            i += step
        if i < stop:
            yield i, stop

    node_count = len(current_app.control.ping())
    group(feed_url_distributor.s(priority, i, j)
          for i, j in interval_seq(0, feeds_count, node_count)).delay()


@shared_task
def feed_url_distributor(priority, beg, end):
    if priority == 'HIGH':
        feeds = models.Feed.objects.filter(priority=0)[beg:end]
    elif priority == 'MEDIUM':
        feeds = models.Feed.objects.filter(priority=1)[beg:end]
    elif priority == 'LOW':
        feeds = models.Feed.objects.filter(priority__gte=2)[beg:end]
    else:
        raise ValueError('Proirity not provided')
    group(feed_indexer.s(feed.url, feed.id) for feed in feeds).delay()


@shared_task
def feed_indexer(url, feed_id):
    feed = models.Feed.objects.get(pk=feed_id)
    try:
        resp = requests.get(url, timeout=2)
        feed.increment_priority()
    except Timeout:
        logger.warning(
            'Timeout during indexing: feed_id: {}'.format(feed_id)
        )
        feed.decrement_priority()
        return

    parsed = feedparser.parse(resp.content)
    # If feed is malformed
    if parsed.bozo == 1:
        feed.decrement_priority()
        logger.warning(
            'Feed is malformed: feed_id: {}'.format(feed_id)
        )
        return
    else:
        feed.increment_priority()

    # Replace time.struct_time with datetime.datetime
    for entry in parsed.entries:
        published_time = time.gmtime(time.time())
        for attr in ('published_parsed', 'updated_parsed', 'created_parsed'):
            try:
                published_time = getattr(entry, attr)
                break
            except AttributeError:
                continue
        entry.published_parsed = datetime.fromtimestamp(
            time.mktime(published_time)).replace(tzinfo=pytz.UTC)

    last_entry = (
        models.Entry.objects
        .filter(feed_id=feed_id).order_by('-published_at').first()
    )

    def make_entry(entry, feed_id):
        return models.Entry(
            feed_id=feed_id,
            slug='-'.join([slugify(entry.title)[:47], uuid.uuid4().hex[:16]]),
            title=entry.title,
            subtitle=entry.get('subtitle', ''),
            link=entry.link,
            author=entry.get('author', ''),
            summary=entry.get('summary', ''),
            content=entry.get('content', ''),
            published_at=entry.published_parsed
        )

    if last_entry:
        new_entries = [make_entry(entry, feed_id) for entry in parsed.entries
                       if entry.published_parsed > last_entry.published_at]
    else:
        new_entries = [make_entry(entry, feed_id) for entry in parsed.entries]
    models.Entry.objects.bulk_create(new_entries)
