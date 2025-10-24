from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count
from django.core.paginator import Paginator
from .models import Post, Comment
from .forms import PostForm, CommentForm
from django.http import JsonResponse
from django.template.loader import render_to_string

def forum_list(request):
    query = request.GET.get('q','')
    category = request.GET.get('category','')
    posts = Post.objects.all()

    if query:
        posts = posts.filter(
            Q(title__icontains=query) |
            Q(content__icontains=query) |
            Q(author__username__icontains=query)
        )
    if category:
        posts = posts.filter(category=category)

    sort_by = request.GET.get('sort', 'newest')
    if sort_by == 'popular':
        posts = posts.annotate(like_count=Count('likes')).order_by('-like_count','-created_at')
    elif sort_by == 'most_commented':
        posts = posts.annotate(comment_count=Count('comments')).order_by('-comment_count','-created_at')
    else:
        posts = posts.order_by('-created_at')

    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    form = PostForm()   # <-- ADD THIS

    context = {
        'page_obj': page_obj,
        'query': query,
        'category': category,
        'sort_by': sort_by,
        'categories': Post.CATEGORY_CHOICES,
        'form': form,   
    }
    return render(request, 'forum_list.html', context)

def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    
    # Increment view count
    post.views += 1
    post.save()
    
    comments = post.comments.all()
    comment_form = CommentForm()
    
    context = {
        'post': post,
        'comments': comments,
        'comment_form': comment_form,
    }
    return render(request, 'post_details.html', context)


@login_required
def add_comment(request, pk):
    post = get_object_or_404(Post, pk=pk)
    
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            messages.success(request, 'Komentar berhasil ditambahkan!')
    
    return redirect('post_details', pk=post.pk)

@login_required
def like_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    
    if request.user in post.likes.all():
        post.likes.remove(request.user)
    else:
        post.likes.add(request.user)
    
    return redirect('post_details', pk=post.pk)

@login_required
def like_comment(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    
    if request.user in comment.likes.all():
        comment.likes.remove(request.user)
    else:
        comment.likes.add(request.user)
    
    return redirect('post_details', pk=comment.post.pk)

@login_required
def delete_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    
    # Hanya author yang bisa menghapus post
    if post.author == request.user:
        post.delete()
        messages.success(request, 'Postingan berhasil dihapus!')
    else:
        messages.error(request, 'Anda tidak memiliki izin untuk menghapus postingan ini.')
    
    return redirect('forum_list')

@login_required
def delete_comment(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    
    # Hanya author yang bisa menghapus komentar
    if comment.author == request.user:
        comment.delete()
        messages.success(request, 'Komentar berhasil dihapus!')
    else:
        messages.error(request, 'Anda tidak memiliki izin untuk menghapus komentar ini.')
    
    return redirect('post_details', pk=comment.post.pk)

def create_post(request):
    if request.method == 'POST':
        # IMPORTANT: include request.FILES to handle image upload
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            # If AJAX request, return JSON with HTML snippet
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                # render single-post partial (create this template)
                html = render_to_string('smash_talk/partials/_single_post.html', {'post': post}, request=request)
                return JsonResponse({'success': True, 'html': html})
            # else regular POST: show success and redirect to the post detail or forum
            messages.success(request, 'Postingan berhasil dibuat!')
            return redirect('smash_talk:post_detail', pk=post.pk)
        else:
            # form invalid
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'errors': form.errors})
            # for normal POST, re-render the form page with errors
            return render(request, 'create_post.html', {'form': form})
    else:
        # GET -> render create_post.html with empty form
        form = PostForm()
        return render(request, 'create_post.html', {'form': form})