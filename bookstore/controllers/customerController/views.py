from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from store.models.customer.customer import Customer

def register(request):
    """Đăng ký tài khoản khách hàng mới"""
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        phone = request.POST.get('phone', '')
        address = request.POST.get('address', '')
        
        # Kiểm tra validation
        if password != password_confirm:
            messages.error(request, 'Mật khẩu xác nhận không khớp!')
            return render(request, 'customer/register.html')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Tên đăng nhập đã tồn tại!')
            return render(request, 'customer/register.html')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email đã được sử dụng!')
            return render(request, 'customer/register.html')
        
        # Tạo user mới
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )
        
        # Tạo customer profile
        Customer.objects.create(
            user=user,
            phone=phone,
            address=address
        )
        
        messages.success(request, 'Đăng ký thành công! Vui lòng đăng nhập.')
        return redirect('customer_login')
    
    return render(request, 'customer/register.html')

def customer_login(request):
    """Đăng nhập khách hàng"""
    if request.user.is_authenticated:
        return redirect('book_home')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Chào mừng {username}!')
            next_url = request.GET.get('next', 'book_home')
            return redirect(next_url)
        else:
            messages.error(request, 'Tên đăng nhập hoặc mật khẩu không đúng!')
    
    return render(request, 'customer/login.html')

@login_required
def customer_logout(request):
    """Đăng xuất"""
    logout(request)
    messages.success(request, 'Đã đăng xuất thành công!')
    return redirect('book_home')

@login_required
def profile(request):
    """Xem và chỉnh sửa thông tin cá nhân"""
    customer, created = Customer.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        customer.phone = request.POST.get('phone', '')
        customer.address = request.POST.get('address', '')
        customer.save()
        
        # Cập nhật email nếu có
        if request.POST.get('email'):
            request.user.email = request.POST.get('email')
            request.user.save()
        
        messages.success(request, 'Cập nhật thông tin thành công!')
        return redirect('customer_profile')
    
    context = {
        'customer': customer,
        'user': request.user
    }
    return render(request, 'customer/profile.html', context)
