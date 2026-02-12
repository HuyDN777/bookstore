from django.contrib import admin
# Import các model từ các gói bạn đã chia
from store.models.book.book import Book, Category
from store.models.customer.customer import Customer
from store.models.order.order import Order, Payment, Shipping

# Đăng ký model để nó hiện trong trang Admin
admin.site.register(Category)
admin.site.register(Book)
admin.site.register(Customer)
admin.site.register(Order)
admin.site.register(Payment)
admin.site.register(Shipping)