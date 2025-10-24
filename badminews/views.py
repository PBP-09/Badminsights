from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .models import News
from .forms import NewsForm

def news_list(request):
    filter_type = request.GET.get("filter", "all")  # default 'all'
    sort_by = request.GET.get("sort", "date")  # default sort by date

    if filter_type == "all":
        news = News.objects.all()
    else:
        news = News.objects.filter(author=request.user)

    category = request.GET.get('category')

    if category and category != "":
        news = news.filter(category=category)

    # Apply sorting after filtering
    if sort_by == "upvotes":
        news = news.annotate(upvote_count=Count('upvotes')).order_by('-upvote_count', '-date_published')
    else:
        news = news.order_by('-date_published')

    paginator = Paginator(news, 10)  # Show 10 news per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Get trending news (top 3 by upvotes, then by views)
    trending_news = News.objects.annotate(
        upvote_count=Count('upvotes')
    ).order_by('-upvote_count', '-views', '-date_published')[:3]

    context = {
        'page_obj': page_obj,
        'categories': News.CATEGORY_CHOICES,
        'selected_category': category,
        'filter_type': filter_type,
        'sort_by': sort_by,
        'trending_news': trending_news,
    }
    return render(request, 'badminews/news_list.html', context)

def news_detail(request, pk):
    news_item = get_object_or_404(News, pk=pk)
    # Increment view count
    news_item.views += 1
    # Mark as read by current user if authenticated
    if request.user.is_authenticated:
        news_item.read_by.add(request.user)
    news_item.save()
    return render(request, 'badminews/news_detail.html', {'news_item': news_item})

@login_required
def add_news(request):
    if request.method == 'POST':
        form = NewsForm(request.POST, request.FILES)
        if form.is_valid():
            news = form.save(commit=False)
            news.author = request.user
            news.save()
            return redirect('news_list')
    else:
        form = NewsForm()
    return render(request, 'badminews/add_news.html', {'form': form})

@require_POST
@csrf_exempt
def upvote_news(request, pk):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)

    news_item = get_object_or_404(News, pk=pk)
    if request.user in news_item.upvotes.all():
        news_item.upvotes.remove(request.user)
        upvoted = False
    else:
        news_item.upvotes.add(request.user)
        upvoted = True

    return JsonResponse({
        'upvoted': upvoted,
        'upvote_count': news_item.total_upvotes()
    })

@login_required
def create_news_ajax(request):
    if request.method == 'POST':
        form = NewsForm(request.POST, request.FILES)
        if form.is_valid():
            news = form.save(commit=False)
            news.author = request.user
            news.save()
            return JsonResponse({
                'success': True,
                'message': 'News created successfully!',
                'news_id': news.id
            })
        else:
            return JsonResponse({
                'success': False,
                'errors': form.errors
            })
    return JsonResponse({'success': False, 'message': 'Invalid request method'})

@login_required
def edit_news(request, pk):
    news = get_object_or_404(News, pk=pk, author=request.user)
    if request.method == 'POST':
        form = NewsForm(request.POST, request.FILES, instance=news)
        if form.is_valid():
            form.save()
            return redirect('badminews:news_list')
    else:
        form = NewsForm(instance=news)
    return render(request, 'badminews/add_news.html', {'form': form, 'news': news, 'is_edit': True})

@login_required
def delete_news(request, pk):
    news = get_object_or_404(News, pk=pk, author=request.user)
    if request.method == 'POST':
        news.delete()
        return redirect('badminews:news_list')
    return redirect('badminews:news_list')

def news_json(request):
    filter_type = request.GET.get("filter", "all")
    sort_by = request.GET.get("sort", "date")
    category = request.GET.get('category')

    if filter_type == "all":
        news = News.objects.all()
    else:
        news = News.objects.filter(author=request.user)

    # Apply filters first
    if category and category.strip() != "":
        news = news.filter(category=category.strip())

    # Apply sorting after filtering
    if sort_by == "upvotes":
        news = news.annotate(upvote_count=Count('upvotes')).order_by('-upvote_count', '-date_published')
    else:
        news = news.order_by('-date_published')

    data = list(news.values('id', 'title', 'content', 'author__username', 'date_published', 'category', 'views'))
    return JsonResponse(data, safe=False)
