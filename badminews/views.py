from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q
from .models import News
from .forms import NewsForm

def news_list(request):
    filter_type = request.GET.get("filter", "all")  # default 'all'

    if filter_type == "all":
        news = News.objects.all().order_by('-date_published')
    else:
        news = News.objects.filter(author=request.user).order_by('-date_published')

    category = request.GET.get('category')
    search = request.GET.get('search')

    if category:
        news = news.filter(category=category)
    if search:
        news = news.filter(Q(title__icontains=search) | Q(content__icontains=search))

    paginator = Paginator(news, 10)  # Show 10 news per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'categories': News.CATEGORY_CHOICES,
        'selected_category': category,
        'search_query': search,
        'filter_type': filter_type,
    }
    return render(request, 'badminews/news_list.html', context)

def news_detail(request, pk):
    news_item = get_object_or_404(News, pk=pk)
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

def news_json(request):
    news = News.objects.all().order_by('-date_published')
    data = list(news.values('id', 'title', 'content', 'author__username', 'date_published', 'category'))
    return JsonResponse(data, safe=False)
