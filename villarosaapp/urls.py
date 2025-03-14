
from django.contrib import admin
from django.urls import path
from villarosaapp import views

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', views.index, name='index'),

    path('starter/', views.starter, name= 'starter'),

    path('about/', views.about, name='about'),

    path('chefs/', views.chefs, name='chefs'),

    path('contact/', views.contact, name='contact'),
    path('gallery/', views.gallery, name='gallery'),
    path('events/', views.starter, name='events'),
    path('menu/', views.menu, name='menu'),
    path('specials/', views.specials, name='specials'),

    path('book/', views.book, name='book'),
    path('edit/<int:id>', views.edit, name='edit'),

    path('reservations/', views.reservations, name='reservations'),

    path('delete/<int:id>', views.delete, name='delete'),

#Mpesa Api--------------

path('pay/', views.pay, name='pay'),
path('stk/', views.stk, name='stk'),
path('token/', views.token, name='token'),
path('transactions/', views.transactions_list, name='transactions'),
]
