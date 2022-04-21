from django.urls import path
from . import views


urlpatterns = [
    # ex: /polls/
    path('', views.index, name='indexDefault'),
    # ex: /polls/
    path('index/', views.index, name='index'),
    # ex: /polls/5/
    path('login/', views.login, name='login'),
    # ex: /polls/5/results/
    path('register/', views.register, name='register'),
    # ex: /polls/5/vote/
    path('logout/', views.logout, name='logout'),

    # path('search/', views.search, name='search'),
]