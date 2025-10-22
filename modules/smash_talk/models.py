from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

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
    
    title = models.CharField(max_length=200, verbose_name="Judul")
    content = models.TextField(verbose_name="Konten")
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='forum_posts')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='general')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    likes = models.ManyToManyField(User, related_name='liked_posts', blank=True)
    views = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Postingan'
        verbose_name_plural = 'Postingan'
    
    def __str__(self):
        return self.title
    
    def total_likes(self):
        return self.likes.count()
    
    def total_comments(self):
        return self.comments.count()

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='forum_comments')
    content = models.TextField(verbose_name="Komentar")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    likes = models.ManyToManyField(User, related_name='liked_comments', blank=True)
    
    class Meta:
        ordering = ['created_at']
        verbose_name = 'Komentar'
        verbose_name_plural = 'Komentar'
    
    def __str__(self):
        return f"Komentar oleh {self.author} pada {self.post.title}"
    
    def total_likes(self):
        return self.likes.count()