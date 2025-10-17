# recipe_backend_api/recipes_api/serializers.py

from rest_framework import serializers
from .models import Recipe

class RecipeSerializer(serializers.ModelSerializer):
    # Field for the frontend to easily determine edit permissions
    is_owner = serializers.SerializerMethodField() 

    class Meta:
        model = Recipe
        fields = ['id', 'title', 'description', 'ingredients', 'instructions', 'created_at', 'user', 'is_owner']
        read_only_fields = ['user', 'created_at']

    def get_is_owner(self, obj):
        request = self.context.get('request')
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            return obj.user == request.user
        return False