from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Post
from .forms import EmailPostForm
from django.views.generic import ListView
# Create your views here.
# django自带的基于类的通用ListView视图只需指定需要的参数即可
class PostListView(ListView):
    queryset = Post.published.all()
    context_object_name = 'posts'
    paginate_by = 3
    template_name = 'blog/post/list.html'

# 自定义函数  自己定义所有内容并处理异常
#def post_list(request):
#    object_list = Post.published.all()
#    paginator = Paginator(object_list, 3) # 每页显示三条数据
#    page = request.GET.get('page')
#    try:
#        posts = paginator.page(page)
#    except PageNotAnInteger:
#        posts = paginator.page(1) # 如果参数不是一个整数，返回第一页
#    except EmptyPage:
#        posts = paginator.page(paginator.num_pages)
#    return render(request, 'blog/post/list.html', {'page': page, 'posts': posts})

# 定义返回详情视图函数
def post_detail(request, year, month, day, post):
    post = get_object_or_404(Post, slug=post, status='published', publish__year=year, publish__month=month, publish__day=day)
    return render(request, 'blog/post/detail.html', {'post': post})

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
