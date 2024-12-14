
from django.urls import path

from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("newPost", views.newPost, name="newPost"),
    path("profile/<int:user_id>", views.profile, name="profile"),
    path("unFollow", views.unFollow, name="unFollow"),
    path("follow", views.follow, name="follow"),
    path("following", views.following, name="following"),
    path("edit/<int:id>", views.edit, name="edit"),
    
    path('likePost/<int:post_id>/', views.likePost, name='likePost'),
    path('unLikePost/<int:post_id>/', views.unLikePost, name='unLikePost'),

    path('delete_post/<int:post_id>/', views.delete_post, name='delete_post'),


    
    path('post/<int:post_id>/comments/', views.comment_post, name='postComment'),
    path('post/<int:post_id>/comment/', views.add_comment, name='add_comment'),

]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)