from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Post, Comment
from .forms import EmailPostForm, CommentForm, SearchForm
from django.views.generic import ListView
from django.core.mail import send_mail
from taggit.models import Tag
from django.db.models import Count
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from django.contrib.postgres.search import TrigramSimilarity
# 自定义函数  自己定义所有内容并处理异常
def post_search(request):
    form = SearchForm()
    query = None
    results = []
    if 'query' in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            search_vector = SearchVector('title',weight='A') + SearchVector('body', weight='B')
            search_query = SearchQuery(query)
            results = Post.objects.annotate(similarity=TrigramSimilarity('title', query),).filter(similarity__gte=0.1).order_by('-similarity')
#            results = Post.objects.annotate(search=search_vector, rank=SearchRank(search_vector, search_query)).filter(rank__gte=0.3).order_by('-rank')
    return render(request, 'blog/post/search.html', {'query': query, "form": form, 'results': results})



def post_list(request, tag_slug=None):
    object_list = Post.published.all()
    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        object_list = object_list.filter(tags__in=[tag])
    paginator = Paginator(object_list, 3) # 每页显示三条数据
    page = request.GET.get('page')
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1) # 如果参数不是一个整数，返回第一页
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    return render(request, 'blog/post/list.html', {'page': page, 'posts': posts, 'tag': tag})

# 定义返回详情视图函数
def post_detail(request, year, month, day, post):
    post = get_object_or_404(Post, slug=post, status='published', publish__year=year, publish__month=month, publish__day=day)
    # 列出文章激活的评论
    comments = post.comments.filter(active=True)  # 获得当前文章所有评论的结果集
    new_comment = None
    if request.method == "POST":
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False) # 根据表单数据创建对象，不写入数据库,以便修改属性后再写入数据库
            new_comment.post = post # 将当前文章设置为外键
            new_comment.save() # 评论写入数据库
    else:
        comment_form = CommentForm()
    # 列出相似发帖
    post_tags_ids = post.tags.values_list('id', flat=True)
    similar_posts = Post.published.filter(tags__in=post_tags_ids).exclude(id=post.id)
    similar_posts = similar_posts.annotate(same_tags=Count('tags')).order_by('-same_tags', '-publish')[:4]

    return render(request, 'blog/post/detail.html', {'post': post, 'comments': comments, 'new_comment': new_comment, 'comment_form': comment_form, 'similar_posts': similar_posts})

# 定义发送邮件视图函数
def post_share(request, post_id):
    #根据id 获取 post 对象
    post = get_object_or_404(Post, id=post_id, status='published')
    sent = False
    if request.method == "POST":
        # 提交表单数据
        form = EmailPostForm(request.POST)
        if form.is_valid():
            # 验证表单数据
            cd = form.cleaned_data
            # 发送邮件
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = '{} ({}) recommends you reading "{}"'.format(cd['name'], cd['email'], post.title)
            message = 'Read "{}" at {}\n\n{}\'s comments:{}'.format(post.title, post_url, cd['name'], cd['comments'])
            send_mail(subject, message, 'banananer@qq.com', [cd['to']])
            sent = True
    else:
        form = EmailPostForm()
    return render(request, 'blog/post/share.html', {'post': post, 'form': form, 'sent': sent})
