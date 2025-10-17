# recipe_backend_api/recipes_api/views.py

from rest_framework import viewsets, permissions
from .models import Recipe
from .serializers import RecipeSerializer
from .permissions import IsOwnerOrReadOnly

class RecipeViewSet(viewsets.ModelViewSet):
    serializer_class = RecipeSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def perform_create(self, serializer):
        # User is guaranteed to be authenticated via JWT (request.user is available)
        serializer.save(user=self.request.user)
    
    def get_queryset(self):
        # Filter for the current authenticated user
        if self.request.user.is_authenticated:
            return Recipe.objects.filter(user=self.request.user).order_by('-created_at')
        return Recipe.objects.none()