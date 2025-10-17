from django.db import models
from django.contrib.auth.models import User

class Recipe(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    ingredients = models.TextField()
    instructions = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Link the recipe to the user who created it.
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.title


# ❌ REMOVED: The entire Favorite model is removed.
# class Favorite(models.Model):
#     recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
#     added_at = models.DateTimeField(auto_now_add=True)
#     user = models.ForeignKey(User, on_delete=models.CASCADE)

#     class Meta:
#         unique_together = ('user', 'recipe')

#     def __str__(self):
#         return f"Favorite: {self.recipe.title} by {self.user.username}"