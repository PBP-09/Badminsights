from django.db import models
from django.conf import settings

class Post(models.Model):
    CATEGORY_CHOICES = [
        ('question', 'Pertanyaan'),
        ('experience', 'Pengalaman'),
        ('recommendation', 'Rekomendasi'),
        ('strategy', 'Strategi'),
        ('player', 'Pemain'),
        ('match', 'Pertandingan'),
        ('general', 'Umum'),
    ]


    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    likes = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='liked_posts', blank=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='general')

    # NEW: image and views
    image = models.ImageField(upload_to='posts/', null=True, blank=True)
    views = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'smash_talk_posts'
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def like_count(self):
        return self.likes.count()
    like_count.short_description = 'Likes'


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'smash_talk_comments'
        ordering = ['created_at']
    
    def __str__(self):
        # tampilkan username agar lebih jelas
        return f"Comment by {self.author.username} on {self.post.title}"

class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('user', 'User'),
        ('admin', 'Admin'),
    ]
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user')

    def __str__(self):
        return f"{self.user.username} - {self.role}"
    
