from rest_framework import routers

from . import views


router = routers.SimpleRouter()

router.register(r'users', views.UserViewSet, basename='users')
router.register(r'feeds', views.FeedViewSet, basename='feeds')
router.register(r'reads', views.ReadViewSet, basename='reads')
router.register(r'entries', views.EntryViewSet, basename='entries')
router.register(r'comments', views.CommentViewSet, basename='comments')
router.register(r'bookmarks', views.BookmarkViewSet, basename='bookmarks')

urlpatterns = router.urls
