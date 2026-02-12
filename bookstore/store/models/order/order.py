from django.db import models
from store.models.customer.customer import Customer
from store.models.book.book import Book

# --- Phần Giỏ hàng ---
class Cart(models.Model):
    customer = models.OneToOneField(Customer, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'store'
        db_table = 'cart'

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    class Meta:
        app_label = 'store'
        db_table = 'cart_item'

# --- Phần Đặt hàng ---
class Payment(models.Model):
    method_name = models.CharField(max_length=50) # Ví dụ: COD, MOMO
    status = models.CharField(max_length=50, default='Pending')

    class Meta:
        app_label = 'store'
        db_table = 'payment'

class Shipping(models.Model):
    method_name = models.CharField(max_length=50) # Ví dụ: Giao nhanh, Hỏa tốc
    fee = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        app_label = 'store'
        db_table = 'shipping'

class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, null=True)
    shipping = models.ForeignKey(Shipping, on_delete=models.SET_NULL, null=True)
    total_price = models.DecimalField(max_digits=12, decimal_places=2)
    order_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, default='Processing')

    class Meta:
        app_label = 'store'
        db_table = 'order'

class OrderDetail(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2) # Giá tại thời điểm mua

    class Meta:
        app_label = 'store'
        db_table = 'order_detail'