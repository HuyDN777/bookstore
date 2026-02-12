from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from decimal import Decimal
from store.models.book.book import Book
from store.models.order.order import Cart, CartItem, Order, OrderDetail, Payment, Shipping
from store.models.customer.customer import Customer

# Hàm thêm vào giỏ hàng
@login_required(login_url='/customer/login/')
def add_to_cart(request, book_id):
    book = get_object_or_404(Book, pk=book_id)
    
    # Kiểm tra tồn kho
    if book.stock_quantity <= 0:
        messages.error(request, 'Sách này đã hết hàng!')
        return redirect('book_detail', book_id=book_id)
    
    customer, created = Customer.objects.get_or_create(user=request.user)
    cart, created = Cart.objects.get_or_create(customer=customer)
    
    cart_item, created = CartItem.objects.get_or_create(cart=cart, book=book)
    
    if not created:
        # Kiểm tra số lượng trong giỏ không vượt quá tồn kho
        if cart_item.quantity >= book.stock_quantity:
            messages.warning(request, f'Chỉ còn {book.stock_quantity} cuốn trong kho!')
        else:
            cart_item.quantity += 1
            cart_item.save()
            messages.success(request, 'Đã thêm vào giỏ hàng!')
    else:
        cart_item.quantity = 1
        cart_item.save()
        messages.success(request, 'Đã thêm vào giỏ hàng!')
        
    return redirect('view_cart')

# Hàm xóa khỏi giỏ hàng
@login_required(login_url='/customer/login/')
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, pk=item_id)
    # Kiểm tra quyền sở hữu
    if cart_item.cart.customer.user != request.user:
        messages.error(request, 'Bạn không có quyền thực hiện thao tác này!')
        return redirect('view_cart')
    
    cart_item.delete()
    messages.success(request, 'Đã xóa khỏi giỏ hàng!')
    return redirect('view_cart')

# Hàm cập nhật số lượng
@login_required(login_url='/customer/login/')
def update_cart_item(request, item_id):
    cart_item = get_object_or_404(CartItem, pk=item_id)
    if cart_item.cart.customer.user != request.user:
        messages.error(request, 'Bạn không có quyền thực hiện thao tác này!')
        return redirect('view_cart')
    
    quantity = int(request.POST.get('quantity', 1))
    if quantity <= 0:
        cart_item.delete()
        messages.success(request, 'Đã xóa khỏi giỏ hàng!')
    elif quantity > cart_item.book.stock_quantity:
        messages.warning(request, f'Chỉ còn {cart_item.book.stock_quantity} cuốn trong kho!')
    else:
        cart_item.quantity = quantity
        cart_item.save()
        messages.success(request, 'Đã cập nhật giỏ hàng!')
    
    return redirect('view_cart')

# Hàm xem giỏ hàng
@login_required(login_url='/customer/login/')
def view_cart(request):
    try:
        customer = Customer.objects.get(user=request.user)
        cart = Cart.objects.get(customer=customer)
        items = CartItem.objects.filter(cart=cart)
        total_price = sum(item.book.price * item.quantity for item in items)
    except:
        items = []
        total_price = 0
        
    context = {
        'items': items,
        'total': total_price
    }
    return render(request, 'cart/view_cart.html', context)

# Hàm checkout - chọn phương thức thanh toán và shipping
@login_required(login_url='/customer/login/')
def checkout(request):
    customer = Customer.objects.get(user=request.user)
    cart = Cart.objects.get(customer=customer)
    items = CartItem.objects.filter(cart=cart)
    
    if not items.exists():
        messages.warning(request, 'Giỏ hàng của bạn đang trống!')
        return redirect('view_cart')
    
    # Kiểm tra tồn kho
    for item in items:
        if item.quantity > item.book.stock_quantity:
            messages.error(request, f'Sách "{item.book.title}" chỉ còn {item.book.stock_quantity} cuốn!')
            return redirect('view_cart')
    
    # Lấy các phương thức thanh toán và shipping
    payment_methods = Payment.objects.all()
    shipping_methods = Shipping.objects.all()
    
    # Nếu chưa có, tạo mặc định
    if not payment_methods.exists():
        Payment.objects.create(method_name='COD', status='Available')
        Payment.objects.create(method_name='MoMo', status='Available')
        Payment.objects.create(method_name='VNPay', status='Available')
        payment_methods = Payment.objects.all()
    
    if not shipping_methods.exists():
        Shipping.objects.create(method_name='Giao hàng tiêu chuẩn', fee=Decimal('20000'))
        Shipping.objects.create(method_name='Giao hàng nhanh', fee=Decimal('35000'))
        Shipping.objects.create(method_name='Giao hàng hỏa tốc', fee=Decimal('50000'))
        shipping_methods = Shipping.objects.all()
    
    # Tính tổng tiền
    subtotal = sum(item.book.price * item.quantity for item in items)
    
    if request.method == 'POST':
        payment_id = request.POST.get('payment_method')
        shipping_id = request.POST.get('shipping_method')
        
        if not payment_id or not shipping_id:
            messages.error(request, 'Vui lòng chọn phương thức thanh toán và vận chuyển!')
        else:
            return redirect('process_order', payment_id=payment_id, shipping_id=shipping_id)
    
    context = {
        'items': items,
        'subtotal': subtotal,
        'payment_methods': payment_methods,
        'shipping_methods': shipping_methods,
        'customer': customer
    }
    return render(request, 'order/checkout.html', context)

# Hàm xử lý đặt hàng
@login_required(login_url='/customer/login/')
@transaction.atomic
def process_order(request, payment_id, shipping_id):
    customer = Customer.objects.get(user=request.user)
    cart = Cart.objects.get(customer=customer)
    items = CartItem.objects.filter(cart=cart)
    
    if not items.exists():
        messages.error(request, 'Giỏ hàng trống!')
        return redirect('view_cart')
    
    payment = get_object_or_404(Payment, pk=payment_id)
    shipping = get_object_or_404(Shipping, pk=shipping_id)
    
    # Tính tổng tiền
    subtotal = sum(item.book.price * item.quantity for item in items)
    total_price = subtotal + shipping.fee
    
    # Tạo đơn hàng
    order = Order.objects.create(
        customer=customer,
        payment=payment,
        shipping=shipping,
        total_price=total_price,
        status='Processing'
    )
    
    # Tạo chi tiết đơn hàng và cập nhật tồn kho
    for item in items:
        OrderDetail.objects.create(
            order=order,
            book=item.book,
            quantity=item.quantity,
            price=item.book.price
        )
        
        # Giảm tồn kho
        item.book.stock_quantity -= item.quantity
        item.book.save()
    
    # Xóa giỏ hàng
    items.delete()
    
    messages.success(request, f'Đặt hàng thành công! Mã đơn hàng: #{order.id}')
    return redirect('order_detail', order_id=order.id)

# Hàm xem chi tiết đơn hàng
@login_required(login_url='/customer/login/')
def order_detail(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    
    # Kiểm tra quyền sở hữu
    if order.customer.user != request.user:
        messages.error(request, 'Bạn không có quyền xem đơn hàng này!')
        return redirect('book_home')
    
    order_items = OrderDetail.objects.filter(order=order)
    
    context = {
        'order': order,
        'order_items': order_items
    }
    return render(request, 'order/order_detail.html', context)

# Hàm xem lịch sử đơn hàng
@login_required(login_url='/customer/login/')
def order_history(request):
    customer = Customer.objects.get(user=request.user)
    orders = Order.objects.filter(customer=customer).order_by('-order_date')
    
    context = {
        'orders': orders
    }
    return render(request, 'order/order_history.html', context)