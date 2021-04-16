
from django.urls import path, reverse_lazy
from . import views

app_name='colls'
urlpatterns = [
    path('', views.CollListView.as_view(), name='all'),
    path('coll/<int:pk>', views.CollDetailView.as_view(), name='coll_detail'),
    path('coll/create',
        views.CollCreateView.as_view(success_url=reverse_lazy('colls:all')), name='coll_create'),
    path('coll/<int:pk>/update',
        views.CollUpdateView.as_view(success_url=reverse_lazy('colls:all')), name='coll_update'),
    path('coll/<int:pk>/delete',
        views.CollDeleteView.as_view(success_url=reverse_lazy('colls:all')), name='coll_delete'),
    path('coll_picture/<int:pk>', views.stream_file, name='coll_picture'),
    path('coll/<int:pk>/comment',
        views.CommentCreateView.as_view(), name='coll_comment_create'),
    path('comment/<int:pk>/delete',
        views.CommentDeleteView.as_view(success_url=reverse_lazy('colls')), name='coll_comment_delete'),
    path('coll/<int:pk>/favorite',
        views.AddFavoriteView.as_view(), name='coll_favorite'),
    path('coll/<int:pk>/unfavorite',
        views.DeleteFavoriteView.as_view(), name='coll_unfavorite'),
]

