from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Post, Comment

class SmashTalkModuleTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
        
        self.post = Post.objects.create(
            title='Test Post',
            content='Test content',
            author=self.user,
            category='question'
        )
        
        self.comment = Comment.objects.create(
            post=self.post,
            author=self.user,
            content='Test comment'
        )

    def test_module_models(self):
        """Test models functionality"""
        self.assertEqual(str(self.post), 'Test Post')
        self.assertEqual(str(self.comment), 'Komentar oleh testuser pada Test Post')
        self.assertEqual(self.post.total_comments(), 1)

    def test_module_views(self):
        """Test module views"""
        # Test forum list
        response = self.client.get(reverse('smash_talk:forum_list'))
        self.assertEqual(response.status_code, 200)
        
        # Test post detail
        response = self.client.get(reverse('smash_talk:post_detail', args=[self.post.pk]))
        self.assertEqual(response.status_code, 200)

    def test_module_urls(self):
        """Test module URL patterns"""
        urls = [
            reverse('smash_talk:forum_list'),
            reverse('smash_talk:post_detail', args=[1]),
            reverse('smash_talk:create_post'),
        ]
        
        for url in urls:
            response = self.client.get(url)
            self.assertIn(response.status_code, [200, 302])  # 302 for redirect to login

    def test_authentication_required(self):
        """Test that certain actions require authentication"""
        # Try to create post without login
        response = self.client.get(reverse('smash_talk:create_post'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
        
        # Login and try again
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('smash_talk:create_post'))
        self.assertEqual(response.status_code, 200)