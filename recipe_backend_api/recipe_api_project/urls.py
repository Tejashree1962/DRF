# recipe_backend_api/recipe_api_project/urls.py

from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from recipes_api.views import RecipeViewSet

# 🔑 JWT Views for login/refresh
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

router = DefaultRouter()
router.register(r'recipes', RecipeViewSet, basename='recipe')

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # 🔑 JWT AUTHENTICATION ENDPOINTS
    # /api/token/ returns {access: "...", refresh: "..."}
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    # /api/token/refresh/ returns a new access token
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Your main API endpoint: /api/v1/recipes/...
    path('api/v1/', include(router.urls)),

    # Optional: For DRF's built-in login/logout forms (for browsable API)
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]