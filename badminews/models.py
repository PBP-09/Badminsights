from django.db import models
from django.contrib.auth.models import User

class News(models.Model):
    CATEGORY_CHOICES = [
        ('general', 'General'),
        ('tournament', 'Tournament'),
        ('player', 'Player'),
        ('other', 'Other'),
    ]

    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    date_published = models.DateTimeField(auto_now_add=True)
    category = models.CharField(max_length=100, choices=CATEGORY_CHOICES, default='general')
    image = models.ImageField(upload_to='news_images/', blank=True, null=True)
    views = models.PositiveIntegerField(default=0)
    upvotes = models.ManyToManyField(User, related_name='upvoted_news', blank=True)
    read_by = models.ManyToManyField(User, related_name='read_news', blank=True)

    def __str__(self):
        return self.title

    def total_upvotes(self):
        return self.upvotes.count()
