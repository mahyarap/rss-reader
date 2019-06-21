from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()


class Feed(models.Model):
    subscribers = models.ManyToManyField(User)
    unique_name = models.CharField(max_length=200, db_index=True)
    title = models.CharField(max_length=128)
    url = models.URLField(db_index=True)
    priority = models.IntegerField(default=0, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=True, db_index=True)

    class Meta:
        unique_together = ('url', 'unique_name')

    def __str__(self):
        return self.url

    def increment_priority(self):
        if self.priority > 0:
            self.priority -= 1
            self.save()
        return self.priority

    def decrement_priority(self):
        self.priority += 1
        self.save()
        return self.priority


class Entry(models.Model):
    feed = models.ForeignKey('Feed', on_delete=models.CASCADE)
    slug = models.SlugField(max_length=64, allow_unicode=True)
    title = models.CharField(max_length=256)
    subtitle = models.CharField(max_length=256)
    link = models.URLField()
    author = models.CharField(max_length=128, blank=True)
    content = models.TextField(blank=True)
    summary = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    published_at = models.DateTimeField(db_index=True)

    class Meta:
        verbose_name_plural = 'entries'

    def __str__(self):
        return self.slug


class Read(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    entry = models.ForeignKey('Entry', on_delete=models.CASCADE)
    is_read = models.BooleanField(default=True)

    class Meta:
        unique_together = ('owner', 'entry')


class Bookmark(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    entry = models.ForeignKey('Entry', on_delete=models.CASCADE)
    is_bookmarked = models.BooleanField(default=True)

    class Meta:
        unique_together = ('owner', 'entry')


class Comment(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    entry = models.ForeignKey('Entry', on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=True, db_index=True)
