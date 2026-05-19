from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('profile/', views.profile, name='profile'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('', views.rooms_view, name='rooms'),
    path('room/<int:pk>/', views.room_detail, name='detail'),
    path('book/<int:pk>/', views.book_view, name='book'),
    path('my/', views.my_bookings, name='my_bookings'),
    path('cancel/<int:pk>/', views.cancel_booking, name='cancel_booking'),
    path('review/<int:pk>/', views.add_review, name='add_review'),
    path('admin-panel/', views.admin_panel, name='admin_panel'),
    # path('edit/<int:pk>/', views.edit_item, name='edit_item'),
    path('delete/<int:pk>/', views.delete_item, name='delete_item'),
    path('change-status/<int:pk>/', views.change_status, name='change_status'),
]



