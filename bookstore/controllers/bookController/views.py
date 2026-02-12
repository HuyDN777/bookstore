from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from store.models.book.book import Book, Category

def index(request):
    """Trang chủ với danh sách sách và tìm kiếm"""
    books = Book.objects.all()
    search_query = request.GET.get('search', '')
    category_id = request.GET.get('category', '')
    
    # Tìm kiếm theo tên sách, tác giả
    if search_query:
        books = books.filter(
            Q(title__icontains=search_query) | 
            Q(author__icontains=search_query)
        )
    
    # Lọc theo danh mục
    if category_id:
        books = books.filter(category_id=category_id)
    
    # Lấy tất cả danh mục để hiển thị filter
    categories = Category.objects.all()
    
    context = {
        'books': books,
        'categories': categories,
        'search_query': search_query,
        'selected_category': int(category_id) if category_id else None
    }
    
    return render(request, 'book/index.html', context)

def detail(request, book_id):
    """Chi tiết sách với gợi ý sách tương tự.

    Ưu tiên gợi ý theo thứ tự:
    1. Cùng tác giả
    2. Cùng danh mục
    3. Các sách khác bất kỳ (để đủ tối đa 4 cuốn)
    """
    book = get_object_or_404(Book, pk=book_id)
    
    # 1. Ưu tiên sách cùng tác giả
    same_author = Book.objects.filter(author=book.author).exclude(pk=book_id)

    # 2. Sau đó tới sách cùng danh mục (nhưng khác tác giả & chưa nằm trong same_author)
    same_category = Book.objects.filter(category=book.category).exclude(
        Q(pk=book_id) | Q(author=book.author)
    )

    recommended_list = list(same_author[:4])  # bắt đầu với sách cùng tác giả

    # Nếu chưa đủ 4 cuốn thì thêm sách cùng danh mục
    if len(recommended_list) < 4:
        remaining = 4 - len(recommended_list)
        same_category = same_category.exclude(
            pk__in=[b.id for b in recommended_list]
        )[:remaining]
        recommended_list.extend(list(same_category))

    # Nếu vẫn chưa đủ thì lấy thêm vài sách bất kỳ khác để đủ 4
    if len(recommended_list) < 4:
        remaining = 4 - len(recommended_list)
        other_books = Book.objects.exclude(
            pk__in=[book.id] + [b.id for b in recommended_list]
        )[:remaining]
        recommended_list.extend(list(other_books))
    
    context = {
        'book': book,
        'recommended_books': recommended_list
    }
    return render(request, 'book/detail.html', context)

def search(request):
    """Trang tìm kiếm nâng cao"""
    books = Book.objects.all()
    search_query = request.GET.get('q', '')
    category_id = request.GET.get('category', '')
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')
    
    # Tìm kiếm theo tên sách, tác giả
    if search_query:
        books = books.filter(
            Q(title__icontains=search_query) | 
            Q(author__icontains=search_query)
        )
    
    # Lọc theo danh mục
    if category_id:
        books = books.filter(category_id=category_id)
    
    # Lọc theo giá
    if min_price:
        books = books.filter(price__gte=min_price)
    if max_price:
        books = books.filter(price__lte=max_price)
    
    categories = Category.objects.all()
    
    context = {
        'books': books,
        'categories': categories,
        'search_query': search_query,
        'selected_category': int(category_id) if category_id else None,
        'min_price': min_price,
        'max_price': max_price
    }
    
    return render(request, 'book/search.html', context)