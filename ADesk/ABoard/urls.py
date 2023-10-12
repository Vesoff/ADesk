from django.shortcuts import redirect
from django.urls import path
from .views import PList, PostDetail, PSearchList, PostCreate, PostUpdate, PostDelete, Comments, CommentPost, \
   comment_accept, comment_delete

urlpatterns = [
   path('board/', PList.as_view(), name='board_list'),
   path('board/<int:pk>', PostDetail.as_view(), name='boardpost_detail'),
   path('board/search/', PSearchList.as_view(), name='post_search'),
   path('board/create/', PostCreate.as_view(), name='post_create'),
   path('board/<int:pk>/edit/', PostUpdate.as_view(), name='post_update'),
   path('board/<int:pk>/delete/', PostDelete.as_view(), name='post_delete'),
   path('comments', Comments.as_view(), name='comments'),
   path('comments/<int:pk>', Comments.as_view(), name='comments'),
   path('comment/<int:pk>', CommentPost.as_view(), name='comment'),
   path('comment/accept/<int:pk>', comment_accept),
   path('comment/delete/<int:pk>', comment_delete),
   path('', lambda request: redirect('board_list', permanent=False))
]
