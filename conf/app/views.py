import re, os
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.conf import settings
from django.core.paginator import Paginator
from django.contrib.auth.password_validation import validate_password
from .models import Room, Booking, Status, User

def logout_view(request): logout(request); return redirect('login')

def login_view(request):
    if request.method == 'POST':
        u = authenticate(request, username=request.POST['username'], password=request.POST['password'])
        if u: login(request, u); return redirect('rooms')
        return render(request, 'login.html', {'error': 'Неверные данные'})
    return render(request, 'login.html')

def register_view(request):
    if request.method == 'POST':
        u, p = request.POST['username'], request.POST['password']
        phone = request.POST.get('phone', '')
        if not re.match(r'^[a-zA-Z0-9]{6,}', u):
            return render(request, 'register.html', {'error': 'Логин: латиница и цифры, минимум 6 символов'})
        if phone and not re.match(r'^8\(\d{3}\)\d{3}-\d{2}-\d{2}', phone):
            return render(request, 'register.html', {'error': 'Телефон: формат 8(XXX)XXX-XX-XX'})
        try: validate_password(p)
        except Exception as e: return render(request, 'register.html', {'error': e.messages[0]})
        if User.objects.filter(username=u).exists():
            return render(request, 'register.html', {'error': 'Имя уже занято'})
        avatar = request.FILES.get('avatar')
        if avatar and avatar.size > 300 * 1024:
            return render(request, 'register.html', {'error': 'Аватар: максимум 300KB'})
        user = User.objects.create_user(u, password=p, first_name=request.POST.get('first_name', ''), last_name=request.POST.get('last_name', ''), patronymic=request.POST.get('patronymic', ''), phone=phone, email=request.POST.get('email', ''))
        if avatar: user.avatar = avatar; user.save()
        login(request, user); return redirect('items')
    return render(request, 'register.html')

def rooms_view(request):
    q = request.GET.get('q', '')
    sort = request.GET.get('sort', 'id')
    if sort not in ('id', 'name', 'capacity', '-capacity'): sort = 'id'
    qs = (Room.objects.filter(name__icontains=q) | Room.objects.filter(location__icontains=q) if q else Room.objects.all()).order_by(sort)
    page = Paginator(qs, 5).get_page(request.GET.get('page'))
    carousel_dir = os.path.join(settings.MEDIA_ROOT, 'carousel')
    carousel_images = []
    if os.path.isdir(carousel_dir):
        for f in sorted(os.listdir(carousel_dir)):
            if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')): carousel_images.append(settings.MEDIA_URL + 'carousel/' + f)
    return render(request, 'rooms.html', {'rooms': page, 'q': q, 'sort': sort, 'carousel_images': carousel_images})

def room_detail(request, pk):
    room = get_object_or_404(Room, pk=pk)
    reviews = Booking.objects.filter(room=room).exclude(review='').select_related('user')
    return render(request, 'detail.html', {'room': room, 'reviews': reviews})

@login_required
def profile(request):
    if request.method == 'POST':
        u = request.user
        u.first_name = request.POST.get('first_name', '')
        u.last_name = request.POST.get('last_name', '')
        u.patronymic = request.POST.get('patronymic', '')
        u.phone = request.POST.get('phone', '')
        u.email = request.POST.get('email', '')
        if request.FILES.get('avatar'): u.avatar = request.FILES['avatar']
        u.save(); return redirect('profile')
    return render(request, 'profile.html')

@login_required
def book_view(request, pk):
    room = get_object_or_404(Room, pk=pk)
    if not room.is_available(): return redirect('rooms')
    if request.method == 'POST':
        Booking.objects.create(room=room, user=request.user, date=request.POST['date'], time=request.POST.get('time', ''), payment=request.POST.get('payment', ''), comment=request.POST.get('comment', ''), status=Status.objects.get(name='Новая'))
        return redirect('profile')
    return render(request, 'book.html', {'room': room})

@login_required
def my_bookings(request):
    return render(request, 'profile.html', {'bookings': Booking.objects.filter(user=request.user).select_related('room', 'status')})

@login_required
def cancel_booking(request, pk):
    b = get_object_or_404(Booking, pk=pk, user=request.user)
    if b.can_cancel: b.delete()
    return redirect('my_bookings')

@login_required
@require_POST
def add_review(request, pk):
    b = get_object_or_404(Booking, pk=pk, user=request.user)
    if b.status and b.status.name == 'Завершена': b.review = request.POST.get('review', ''); b.save()
    return redirect('my_bookings')

@login_required
def admin_panel(request):
    if not request.user.is_staff: return redirect('rooms')
    error = None
    if request.method == 'POST' and 'add_item' in request.POST:
        if Room.objects.filter(name=request.POST['name']).exists(): error = 'Такое название уже существует'
        else:
            room = Room(name=request.POST['name'], category=request.POST['category'], capacity=request.POST.get('capacity', 0))
            if request.FILES.get('image'): room.image = request.FILES['image']
            room.save(); return redirect('admin_panel')
    bookings = Booking.objects.select_related('room', 'user', 'status').all()
    status_filter = request.GET.get('status_filter')
    if status_filter: bookings = bookings.filter(status__pk=status_filter)
    return render(request, 'admin_panel.html', {'bookings': bookings, 'statuses': Status.objects.all(), 'error': error})

@login_required
def edit_item(request, pk):
    if not request.user.is_staff: return redirect('items')
    room = get_object_or_404(Room, pk=pk)
    if request.method == 'POST':
        room.name = request.POST['name']; room.location = request.POST['location']
        room.capacity = request.POST.get('capacity', 0)
        if request.FILES.get('image'): room.image = request.FILES['image']
        room.save(); return redirect('admin_panel')
    return render(request, 'edit_item.html', {'room': room})

@login_required
def delete_item(request, pk):
    if request.user.is_staff: get_object_or_404(Room, pk=pk).delete()
    return redirect('admin_panel')

@login_required
@require_POST
def change_status(request, pk):
    if not request.user.is_staff: return redirect('items')
    b = get_object_or_404(Booking, pk=pk)
    b.status = get_object_or_404(Status, pk=request.POST['status'])
    b.save()
    return redirect('admin_panel')

