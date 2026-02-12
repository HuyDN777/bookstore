from django.urls import path
from controllers.orderController import views

urlpatterns = [
    path('add/<int:book_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.view_cart, name='view_cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/update/<int:item_id>/', views.update_cart_item, name='update_cart_item'),
    path('checkout/', views.checkout, name='checkout'),
    path('process/<int:payment_id>/<int:shipping_id>/', views.process_order, name='process_order'),
    path('detail/<int:order_id>/', views.order_detail, name='order_detail'),
    path('history/', views.order_history, name='order_history'),
]