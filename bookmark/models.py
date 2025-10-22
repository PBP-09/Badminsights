from django.db import models
from main.models import Player
# Create your models here.
class Bookmark(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='bookmarks')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Bookmark - {self.player.name}"
