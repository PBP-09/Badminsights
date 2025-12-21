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
    search_query = request.GET.get('search', '').strip()

    # Auto-populate dummy data if no news exists
    if not News.objects.exists():
        from django.core.management import call_command
        call_command('populate_news')

    if filter_type == "all":
        news = News.objects.all()
    else:
        news = News.objects.filter(author=request.user)

    category = request.GET.get('category')

    if category and category != "":
        news = news.filter(category=category)

    # Apply search filter
    if search_query:
        news = news.filter(Q(title__icontains=search_query) | Q(content__icontains=search_query))

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
        'search_query': search_query,
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

    # Check if this is an API request (from Flutter)
    if request.GET.get('format') == 'json':
        # Return JSON for Flutter app
        data = {
            'id': news_item.id,
            'title': news_item.title,
            'content': news_item.content,
            'author_username': news_item.author.username,
            'date_published': news_item.date_published.isoformat(),
            'category': news_item.category,
            'views': news_item.views,
            'total_upvotes': news_item.total_upvotes(),
            'image': news_item.image.url if news_item.image else None,
        }

        # Add user-specific data if authenticated
        if request.user.is_authenticated:
            data['is_upvoted'] = request.user in news_item.upvotes.all()
            data['is_read'] = request.user in news_item.read_by.all()
        else:
            data['is_upvoted'] = False
            data['is_read'] = False

        return JsonResponse(data)
    else:
        # Return HTML for web browser
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
                'news_id': news.id,
                'news_data': {
                    'id': news.id,
                    'title': news.title,
                    'content': news.content,
                    'author_username': news.author.username,
                    'date_published': news.date_published.isoformat(),
                    'category': news.category,
                    'image': news.image.url if news.image else None,
                    'views': news.views,
                    'total_upvotes': news.total_upvotes(),
                    'is_upvoted': False,  # New news, not upvoted yet
                    'is_read': False,  # New news, not read yet
                }
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
            if request.content_type == 'multipart/form-data':
                # Web form submission
                return redirect('badminews:news_list')
            else:
                # Flutter API call
                return JsonResponse({
                    'success': True,
                    'message': 'News updated successfully!',
                    'news_data': {
                        'id': news.id,
                        'title': news.title,
                        'content': news.content,
                        'author_username': news.author.username,
                        'date_published': news.date_published.isoformat(),
                        'category': news.category,
                        'image': news.image.url if news.image else None,
                        'views': news.views,
                        'total_upvotes': news.total_upvotes(),
                        'is_upvoted': request.user in news.upvotes.all(),
                        'is_read': request.user in news.read_by.all(),
                    }
                })
        else:
            if request.content_type == 'multipart/form-data':
                # Web form with errors
                return render(request, 'badminews/add_news.html', {'form': form, 'news': news, 'is_edit': True})
            else:
                # Flutter API call with errors
                return JsonResponse({'success': False, 'errors': form.errors})
    else:
        form = NewsForm(instance=news)
    return render(request, 'badminews/add_news.html', {'form': form, 'news': news, 'is_edit': True})

@login_required
def delete_news(request, pk):
    news = get_object_or_404(News, pk=pk, author=request.user)
    if request.method == 'POST':
        news.delete()
        if request.content_type == 'multipart/form-data':
            # Web form submission
            return redirect('badminews:news_list')
        else:
            # Flutter API call
            return JsonResponse({
                'success': True,
                'message': 'News deleted successfully!'
            })
    return redirect('badminews:news_list')

def news_json(request):
    filter_type = request.GET.get("filter", "all")
    sort_by = request.GET.get("sort", "date")
    category = request.GET.get('category')
    search_query = request.GET.get('search', '').strip()

    if filter_type == "all":
        news = News.objects.all()
    else:
        news = News.objects.filter(author=request.user)

    # Apply filters first
    if category and category.strip() != "":
        news = news.filter(category=category.strip())

    if search_query:
        news = news.filter(Q(title__icontains=search_query) | Q(content__icontains=search_query))

    # Apply sorting after filtering
    if sort_by == "upvotes":
        news = news.annotate(upvote_count=Count('upvotes')).order_by('-upvote_count', '-date_published')
    else:
        news = news.order_by('-date_published')

    # Build data with additional fields
    data = []
    for item in news:
        item_data = {
            'id': item.id,
            'title': item.title,
            'content': item.content,
            'author_username': item.author.username,
            'date_published': item.date_published.isoformat(),
            'category': item.category,
            'views': item.views,
            'total_upvotes': item.total_upvotes(),
            'image': item.image.url if item.image else None,
        }

        # Add user-specific data if authenticated
        if request.user.is_authenticated:
            item_data['is_upvoted'] = request.user in item.upvotes.all()
            item_data['is_read'] = request.user in item.read_by.all()
        else:
            item_data['is_upvoted'] = False
            item_data['is_read'] = False

        data.append(item_data)

    return JsonResponse(data, safe=False)

def trending_news_json(request):
    # Get trending news (top 3 by upvotes, then by views)
    trending_news = News.objects.annotate(
        upvote_count=Count('upvotes')
    ).order_by('-upvote_count', '-views', '-date_published')[:3]

    data = []
    for item in trending_news:
        item_data = {
            'id': item.id,
            'title': item.title,
            'content': item.content,
            'author_username': item.author.username,
            'date_published': item.date_published.isoformat(),
            'category': item.category,
            'views': item.views,
            'total_upvotes': item.total_upvotes(),
            'image': item.image.url if item.image else None,
        }

        # Add user-specific data if authenticated
        if request.user.is_authenticated:
            item_data['is_upvoted'] = request.user in item.upvotes.all()
            item_data['is_read'] = request.user in item.read_by.all()
        else:
            item_data['is_upvoted'] = False
            item_data['is_read'] = False

        data.append(item_data)

    return JsonResponse(data, safe=False)
