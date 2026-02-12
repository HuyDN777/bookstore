from django.urls import path
from controllers.customerController import views

urlpatterns = [
    path('register/', views.register, name='customer_register'),
    path('login/', views.customer_login, name='customer_login'),
    path('logout/', views.customer_logout, name='customer_logout'),
    path('profile/', views.profile, name='customer_profile'),
]
