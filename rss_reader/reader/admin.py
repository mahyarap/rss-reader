from django.contrib import admin

from . import models


admin.site.register(models.Read)
admin.site.register(models.Feed)
admin.site.register(models.Entry)
admin.site.register(models.Bookmark)
