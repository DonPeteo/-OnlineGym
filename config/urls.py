"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from core import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.program_list, name='program_list'),
    path('program/<int:id>/', views.program_detail, name='program_detail'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='core/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('program/<int:id>/buy/', views.buy_program, name='buy_program'),
    path('program/<int:id>/checkout/',views.create_checkout_session,name='create_checkout_session'),
    path('program/<int:id>/success/',views.payment_success,name='payment_success'),
    path('my-programs/', views.my_programs, name='my_programs'),
    path('password-change/',auth_views.PasswordChangeView.as_view(template_name='core/password_change.html'),name='password_change'),
    path('password-change/done/',auth_views.PasswordChangeDoneView.as_view(template_name='core/password_change_done.html'),name='password_change_done'),
    path('programs/', views.all_programs, name='all_programs'),
]
