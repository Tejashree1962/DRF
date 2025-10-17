# recipe_manager/urls.py (Frontend Project)

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # 1. Main App Paths (e.g., '/', '/recipe/add/')
    path('', include('recipes.urls')),
    
    # 2. Login/Logout Handlers
    # 🔑 FIX: Explicitly route the 'login' and 'logout' paths to the JWT handlers defined in recipes.urls
    
    # This includes the general recipes.urls, which handles paths like 'register/' and 'recipe/add/'
    # path('', include('recipes.urls')),  <-- This line already handles all non-prefixed paths.
    
    # We explicitly map the 'accounts/login/' and 'accounts/logout/' prefixes 
    # to the views named 'login' and 'logout' defined inside recipes.urls
    path('accounts/', include('recipes.urls')), # This routes /accounts/login/ and /accounts/logout/ 
                                               # to the login/logout handlers defined in recipes/urls.py
]