from django.db import models
from django.contrib.auth.models import User
from main.models import Player
from django.conf import settings

class Bookmark(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bookmarks')
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='bookmarked_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'player')
        ordering = ['-created_at'] 

    def __str__(self):
        return f"{self.user.username} → {self.player.name}"
