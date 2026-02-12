from django.urls import path
from controllers.bookController import views

urlpatterns = [
    path('', views.index, name='book_home'),
    path('detail/<int:book_id>/', views.detail, name='book_detail'),
    path('search/', views.search, name='book_search'),
]