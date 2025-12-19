from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseNotAllowed
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count, F
from django.core.paginator import Paginator
from .models import Post, Comment
from .forms import PostForm, CommentForm
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt
from django.utils.html import strip_tags
import requests
import json

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

    # --- Hitung view hanya sekali per user/session ---
    if request.user.is_authenticated:
        session_key = f'viewed_post_{post.pk}_user_{request.user.pk}'
        if not request.session.get(session_key, False):
            Post.objects.filter(pk=post.pk).update(views=F('views') + 1)
            request.session[session_key] = True
    else:
        # untuk anonymous, simpan list id post yg sudah dilihat
        viewed = request.session.get('viewed_posts', [])
        if post.pk not in viewed:
            Post.objects.filter(pk=post.pk).update(views=F('views') + 1)
            viewed.append(post.pk)
            request.session['viewed_posts'] = viewed

    post.refresh_from_db()

    comments = post.comments.select_related('author').order_by('-created_at')
    comment_form = CommentForm()

    context = {
        'post': post,
        'comments': comments,
        'comment_form': comment_form,
    }
    return render(request, 'post_detail.html', context)


@login_required(login_url='/login/')
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
        else:
            messages.error(request, 'Gagal menambahkan komentar. Pastikan semua field diisi.')
    return redirect('smash_talk:post_detail', pk=post.pk)

@login_required(login_url='/login/')
def like_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    
    if request.user in post.likes.all():
        post.likes.remove(request.user)
    else:
        post.likes.add(request.user)
    
    return redirect('smash_talk:post_detail', pk=post.pk)

@login_required(login_url='/login/')
def like_comment(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    
    if request.user in comment.likes.all():
        comment.likes.remove(request.user)
    else:
        comment.likes.add(request.user)
    
    return redirect('smash_talk:post_detail', pk=comment.post.pk)

@login_required(login_url='/login/')
def delete_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    
    # Hanya author yang bisa menghapus post
    if post.author == request.user:
        # Hapus file gambar dari storage (jika ada)
        if post.image:
            post.image.delete(save=False)

        # Hapus objek dari database
        post.delete()
        messages.success(request, 'Postingan dan gambarnya berhasil dihapus!')
    else:
        messages.error(request, 'Anda tidak memiliki izin untuk menghapus postingan ini.')
    
    return redirect('smash_talk:forum_list')


@login_required(login_url='/login/')
def delete_comment(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    
    # Hanya author yang bisa menghapus komentar
    if comment.author == request.user:
        comment.delete()
        messages.success(request, 'Komentar berhasil dihapus!')
    else:
        messages.error(request, 'Anda tidak memiliki izin untuk menghapus komentar ini.')
    
    
    return redirect('smash_talk:post_detail', pk=comment.post.pk)

@login_required(login_url='/login/')
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()

            # kalau permintaan datang dari AJAX
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                html = render_to_string('single_post.html', {'post': post}, request=request)
                return JsonResponse({
                    'success': True,
                    'html': html,
                    'message': 'Postingan berhasil dibuat!'
                })

            messages.success(request, 'Postingan berhasil dibuat!')
            return redirect('smash_talk:forum_list')
        else:
            # kalau invalid form
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'errors': form.errors,
                    'message': 'Gagal membuat postingan.'
                })

            return render(request, 'create_post.html', {'form': form})
    else:
        form = PostForm()
        return render(request, 'create_post.html', {'form': form})

    
def get_posts_ajax(request):

    posts = Post.objects.all().values('id', 'title', 'content', 'author__username')
    return JsonResponse(list(posts), safe=False)


@csrf_exempt 
def create_post_ajax(request):
    """Buat post baru lewat AJAX (POST)."""
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user if request.user.is_authenticated else None
            post.save()
            return JsonResponse({'status': 'success', 'title': post.title})
        else:
            return JsonResponse({'status': 'error', 'errors': form.errors})
    return JsonResponse({'status': 'invalid'})

def _absolute_image_url(request, image_field):
    if not image_field:
        return None
    try:
        return request.build_absolute_uri(image_field.url)
    except Exception:
        return None

def api_post_list(request):
    if request.method != 'GET':
        return HttpResponseNotAllowed(['GET'])
    q = request.GET.get('q','')
    category = request.GET.get('category','')
    sort_by = request.GET.get('sort','newest')
    page = int(request.GET.get('page', 1))
    per_page = int(request.GET.get('per_page', 10))

    qs = Post.objects.select_related('author').all()
    if q:
        from django.db.models import Q
        qs = qs.filter(Q(title__icontains=q) | Q(content__icontains=q) | Q(author__username__icontains=q))
    if category:
        qs = qs.filter(category=category)

    if sort_by == 'popular':
        from django.db.models import Count
        qs = qs.annotate(like_count=Count('likes')).order_by('-like_count','-created_at')
    elif sort_by == 'most_commented':
        from django.db.models import Count
        qs = qs.annotate(comment_count=Count('comments')).order_by('-comment_count','-created_at')
    else:
        qs = qs.order_by('-created_at')

    paginator = Paginator(qs, per_page)
    page_obj = paginator.get_page(page)

    data = []
    for p in page_obj:
        data.append({
            'id': p.id,
            'title': p.title,
            'content': p.content,
            'author': p.author.username,
            'like_count': p.like_count(),
            'category': p.category,
            'image': _absolute_image_url(request, p.image),
            'views': p.views,
            'created_at': p.created_at.isoformat(),
            'updated_at': p.updated_at.isoformat(),
        })

    return JsonResponse({
        'results': data,
        'page': page_obj.number,
        'num_pages': paginator.num_pages,
        'total': paginator.count,
    })


def api_post_detail(request, pk):
    if request.method != 'GET':
        return HttpResponseNotAllowed(['GET'])
    p = get_object_or_404(Post.objects.select_related('author'), pk=pk)
    data = {
        'id': p.id,
        'title': p.title,
        'content': p.content,
        'author': p.author.username,
        'like_count': p.like_count(),
        'category': p.category,
        'image': _absolute_image_url(request, p.image),
        'views': p.views,
        'created_at': p.created_at.isoformat(),
        'updated_at': p.updated_at.isoformat(),
        # optionally include comments count
        'comment_count': p.comments.count(),
    }
    return JsonResponse(data)


@csrf_exempt
@login_required(login_url='/login/')
def api_create_post(request):
    # menggunakan form yang sudah ada (PostForm) untuk validasi + file upload
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])
    form = PostForm(request.POST, request.FILES)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        # jika many-to-many perlu set, tapi di sini tidak
        return JsonResponse({
            'status': 'success',
            'id': post.id,
            'title': post.title,
            'image': _absolute_image_url(request, post.image),
            'created_at': post.created_at.isoformat()
        }, status=201)
    else:
        return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)


@csrf_exempt
@login_required(login_url='/login/')
def api_toggle_like_post(request, pk):
    # toggle like via POST (AJAX/mobile)
    if request.method not in ('POST',):
        return HttpResponseNotAllowed(['POST'])
    post = get_object_or_404(Post, pk=pk)
    user = request.user
    if user in post.likes.all():
        post.likes.remove(user)
        liked = False
    else:
        post.likes.add(user)
        liked = True
    return JsonResponse({'status': 'success', 'liked': liked, 'like_count': post.like_count()})


@login_required(login_url='/login/')
@csrf_exempt
def api_add_comment(request, pk):
    # POST to add comment to post pk
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])
    post = get_object_or_404(Post, pk=pk)
    form = CommentForm(request.POST)
    if form.is_valid():
        c = form.save(commit=False)
        c.post = post
        c.author = request.user
        c.save()
        return JsonResponse({
            'status': 'success',
            'id': c.id,
            'content': c.content,
            'author': c.author.username,
            'created_at': c.created_at.isoformat()
        }, status=201)
    return JsonResponse({'status':'error','errors': form.errors}, status=400)


def api_get_comments(request, pk):
    if request.method != 'GET':
        return HttpResponseNotAllowed(['GET'])
    post = get_object_or_404(Post, pk=pk)
    qs = post.comments.select_related('author').order_by('-created_at')
    data = [{
        'id': c.id,
        'content': c.content,
        'author': c.author.username,
        'created_at': c.created_at.isoformat()
    } for c in qs]
    return JsonResponse({'comments': data})