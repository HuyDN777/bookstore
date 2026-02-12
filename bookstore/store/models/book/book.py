from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

    class Meta:
        app_label = 'store'
        db_table = 'category'

class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2) # Dùng Decimal cho tiền tệ chuẩn hơn Float
    stock_quantity = models.IntegerField(default=0)
    image_url = models.CharField(max_length=500, blank=True) # Link ảnh bìa sách
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True) # Quan hệ 1-N

    def __str__(self):
        return self.title

    class Meta:
        app_label = 'store'
        db_table = 'book'

class Rating(models.Model):
    score = models.IntegerField()
    comment = models.TextField()
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    # customer sẽ được link sau khi tạo file customer
    # created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'store'
        db_table = 'rating'