from django.db import models
from django.contrib.auth.models import User # Tận dụng bảng User có sẵn của Django để đăng nhập

class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE) # Link với tài khoản đăng nhập
    phone = models.CharField(max_length=15, blank=True)
    address = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.user.username

    class Meta:
        app_label = 'store'
        db_table = 'customer'