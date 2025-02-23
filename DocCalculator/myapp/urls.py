from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect

def redirect_to_login(request):
    return redirect("login")

urlpatterns = [
    #path("login/", LoginView.as_view(template_name="myapp/login.html"), name="login"),
    path('', views.home, name='home'),
    path('calculation/', views.calculation, name='calculation'),
    path('calculate_all_contracts/', views.calculate_all_contracts, name='calculate_all_contracts'),
    path('calculate_single_contract/', views.calculate_single_contract, name='calculate_single_contract'),
    path('subscribers_db/', views.subscribers_db, name='subscribers_db'),
    path('edit-subscriber/<int:id>/', views.edit_subscriber, name='edit_subscriber'),
    path('delete-subscriber/<int:id>/', views.delete_subscriber, name='delete_subscriber'),    
    path('search/', views.search_subscribers, name='search_subscribers'),
    path('add/', views.add_subscriber, name='add_subscriber'),
    
    ]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)