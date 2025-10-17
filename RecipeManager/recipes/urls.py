# RecipeManager/recipes/urls.py (Frontend App)

from django.urls import path
from . import views

urlpatterns = [
    path('', views.recipe_list, name='recipe_list'),
    path('recipe/<int:pk>/', views.recipe_detail, name='recipe_detail'),
    path('recipe/add/', views.recipe_create, name='recipe_create'),
    path('recipe/<int:pk>/edit/', views.recipe_update, name='recipe_update'),
    path('recipe/<int:pk>/delete/', views.recipe_delete, name='recipe_delete'),
    
    # 🔑 NEW JWT HANDLERS
    path('login/', views.login_user, name='login'),      
    path('logout/', views.logout_user, name='logout'),    
    
    path("register/", views.register, name="register"),
]