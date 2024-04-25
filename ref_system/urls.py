from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from app.views import phone_form_view, profile, code_form_view, UserViewSet, PhoneLoginView, CodeLoginView, ProfileView

router = DefaultRouter()
router.register(r"users", UserViewSet)
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(router.urls)),
    path("user/phone_login/", PhoneLoginView.as_view(), name="phone_login"),
    path("user/code_login/", CodeLoginView.as_view(), name="code_login"),
    path("user/profile/", ProfileView.as_view(), name="profile_view"),
    path('api-auth/', include('rest_framework.urls')),
    path('request-phone-number/', phone_form_view, name='phone_auth'),
    path('code_form_view/', code_form_view, name='code_form_view'),
    path('profile/', profile, name='profile'),
    # Другие URL-маршруты вашего приложения
]
