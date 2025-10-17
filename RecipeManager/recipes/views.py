from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout, authenticate 
from django.contrib.auth.models import User 
import requests
import json 
from datetime import datetime # 🔑 CRITICAL FIX: ADDED THIS IMPORT

from .models import Recipe 
from .forms import RecipeForm 

# 🔑 JWT CONFIGURATION
API_BASE_URL = "http://127.0.0.1:8001/api/v1/recipes/"
JWT_TOKEN_URL = "http://127.0.0.1:8001/api/token/" 


# 🔑 JWT HELPER FUNCTION
def get_auth_headers_jwt(request):
    """Retrieves the JWT token from the session and formats the Authorization header."""
    token = request.session.get('access_token')
    if token:
        return {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json',
        }
    return {'Content-Type': 'application/json'} 


# ----------------- AUTHENTICATION HANDLERS (JWT) -----------------

def login_user(request):
    """Handles login by acquiring JWT tokens from the backend API."""
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST) 
        
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            
            api_payload = {'username': username, 'password': password}
            
            try:
                response = requests.post(
                    JWT_TOKEN_URL,
                    data=api_payload
                )
            except requests.exceptions.ConnectionError:
                form.add_error(None, "API server (Port 8001) is unreachable.")
                return render(request, "registration/login.html", {'form': form})
            
            if response.status_code == 200:
                tokens = response.json()
                
                request.session['access_token'] = tokens['access']
                
                user = authenticate(username=username, password=password)
                if user is not None:
                    login(request, user)
                
                return redirect("recipe_list")
            
            else:
                error_detail = response.json().get('detail', 'Invalid credentials.')
                form.add_error(None, f"Login failed: {error_detail}")
        
        return render(request, "registration/login.html", {'form': form})
    
    form = AuthenticationForm()
    return render(request, "registration/login.html", {'form': form})


def logout_user(request):
    """Handles logout by deleting the JWT token and clearing the Django session."""
    if 'access_token' in request.session:
        del request.session['access_token']
    logout(request) 
    return redirect("recipe_list")


def register(request):
    """Handles registration using Django's form, saving user to the shared DB."""
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user) 
            return redirect("recipe_list")
    else:
        form = UserCreationForm()
    return render(request, "registration/register.html", {"form": form})


# ----------------- CRUD VIEWS (API CLIENT) -----------------

@login_required 
def recipe_list(request):
    recipes = [] 
    headers = get_auth_headers_jwt(request)
    
    try:
        response = requests.get(API_BASE_URL, headers=headers)
    except requests.exceptions.ConnectionError:
        error_message = "API server (Port 8001) is unreachable."
        return render(request, "recipes/recipe_list.html", {"recipes": recipes, "error": error_message}) 

    if response.status_code == 200:
        recipes = response.json()
        
        # 🔑 FIX: Iterate and convert date for list view display
        for recipe in recipes:
            created_at_str = recipe.get('created_at')
            if created_at_str:
                try:
                    # Convert ISO string to datetime object for template filter
                    recipe['created_at'] = datetime.fromisoformat(created_at_str.replace('Z', '+00:00'))
                except ValueError:
                    # If conversion fails, leave it as a string
                    pass
    else:
        error_message = f"Error fetching recipes from API (Status {response.status_code}). Please re-login."
        return render(request, "recipes/recipe_list.html", {"recipes": recipes, "error": error_message}) 

    return render(
        request,
        "recipes/recipe_list.html",
        {"recipes": recipes},
    )


@login_required 
def recipe_detail(request, pk):
    headers = get_auth_headers_jwt(request)
    
    try:
        response = requests.get(f"{API_BASE_URL}{pk}/", headers=headers)
    except requests.exceptions.ConnectionError:
        return redirect("recipe_list")

    if response.status_code == 200:
        recipe_data = response.json()
        
        # 🔑 FIX: Convert date for detail view display
        created_at_str = recipe_data.get('created_at')
        if created_at_str:
            try:
                recipe_data['created_at'] = datetime.fromisoformat(created_at_str.replace('Z', '+00:00'))
            except ValueError:
                pass
        
        is_owner = recipe_data.pop('is_owner', False) 
        ingredients = recipe_data.get('ingredients', '').splitlines()

        return render(
            request,
            "recipes/recipe_detail.html",
            {
                "recipe": recipe_data,
                "ingredients": ingredients,
                "is_owner": is_owner,
            },
        )
    return redirect("recipe_list") 


@login_required
def recipe_create(request):
    if request.method == "POST":
        form = RecipeForm(request.POST)
        if form.is_valid():
            
            headers = get_auth_headers_jwt(request)
            payload = json.dumps(form.cleaned_data)
            
            try:
                response = requests.post(API_BASE_URL, data=payload, headers=headers)
            except requests.exceptions.ConnectionError:
                form.add_error(None, "API server (Port 8001) is unreachable.")
                return render(request, "recipes/recipe_form.html", {"form": form})
            
            if response.status_code in [201, 200]: 
                return redirect("recipe_list")
            
            else:
                try:
                    api_errors = response.json()
                    form.add_error(None, f"API failed with status {response.status_code}: {api_errors}")
                except json.JSONDecodeError:
                     form.add_error(None, f"API failed with status {response.status_code}. Server returned non-JSON error.")

    else:
        form = RecipeForm()
    
    return render(request, "recipes/recipe_form.html", {"form": form})


@login_required
def recipe_update(request, pk):
    headers = get_auth_headers_jwt(request)

    try:
        get_response = requests.get(f"{API_BASE_URL}{pk}/", headers=headers)
    except requests.exceptions.ConnectionError:
        return redirect("recipe_list")
    
    if get_response.status_code != 200:
        return redirect("recipe_list")

    recipe_data = get_response.json()
    
    if not recipe_data.get('is_owner', False):
        return redirect("recipe_list") 

    if request.method == "POST":
        form = RecipeForm(request.POST) 
        if form.is_valid():
            payload = json.dumps(form.cleaned_data)
            
            try:
                response = requests.put(f"{API_BASE_URL}{pk}/", data=payload, headers=headers)
            except requests.exceptions.ConnectionError:
                form = RecipeForm(request.POST)
                form.add_error(None, "API server (Port 8001) is unreachable.")
                return render(request, "recipes/recipe_form.html", {"form": form, "pk": pk})

            if response.status_code == 200:
                return redirect("recipe_list")
            
            else:
                form.add_error(None, f"API update failed with status {response.status_code}.")

    else:
        form = RecipeForm(initial=recipe_data)

    return render(request, "recipes/recipe_form.html", {"form": form, "pk": pk})


@login_required
def recipe_delete(request, pk):
    headers = get_auth_headers_jwt(request)
    
    try:
        response = requests.delete(f"{API_BASE_URL}{pk}/", headers=headers)
    except requests.exceptions.ConnectionError:
        return redirect("recipe_list") 
    
    if response.status_code == 204 or response.status_code == 200:
        pass 
    
    return redirect("recipe_list")