from django.urls import path, include
from . import views
from rest_framework import routers
from core.middleware.ssl_cert_auth import debug_ssl_headers  # dodano za debugiranje SSL certifikatov

# from django.views.decorators.csrf import ensure_csrf_cookie    # dodano 20.10.2025
# from django.http import JsonResponse                           # dodano 20.10.2025
# from core.views import get_csrf_token                          # dodano 20.10.2025

router = routers.DefaultRouter()
# router.register(r'core', views.BuildingsModelViewSet)

urlpatterns = [
    path("hello_world/", views.HelloWord.as_view(), name="hello_world"),
    path('', include(router.urls)),
    path('not_loggedin/', views.notLoggedIn, name="not_loggedin"),
    path('login/', views.LoginView.as_view(), name="login"),
    path('logout/', views.LogoutView.as_view(), name="logout"),  # popravil tudi 'name'
    path('isloggedin/', views.IsLoggedIn.as_view(), name="isloggedin"),
    path('check-login/', views.CheckLoginView.as_view(), name="check-login"),  
    path('debug-ssl/', debug_ssl_headers),  # dodano za debugiranje SSL certifikatov
    # path('csrf/', get_csrf_token, name='get-csrf-token'),                                                 
]


