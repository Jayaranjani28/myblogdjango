from django.http.response import HttpResponseRedirect
from django.shortcuts import render,get_object_or_404
from django.urls import reverse
from blog.forms import CommentForm
from .models import Post
from django.views import View

# Create your views here.
def index(request):
    return render(request,"blog/base.html")

def starting_page(request):
    latest_posts = Post.objects.all().order_by("-date")[:3] # negative index for slicing doesnot supported by django
    return render(request,"blog/index.html",{
        "posts":latest_posts
    })
    
# class StartingPageView(ListView):
#     template_name = "blog/index.html"
#     model = Post
#     Ordering = ["-date"]
#     context_object_name = "posts"

#     def get_queryset(self):
#         queryset = super().get_queryset()
#         data = queryset[:3]
#         return data

def posts(request):
    all_posts = Post.objects.all().order_by("-date")
    return render(request,"blog/all-posts.html",{
        "all_posts":all_posts
    })

#  class AllPostView(ListView):
#     template_name = "blog/all-posts.html"
#     model = Post
#     Ordering = ["-date"]
#     context_object_name = "all_posts"



# def post_detail(request,slug):
#     selected_post = get_object_or_404(Post,slug=slug)
#     return render(request,"blog/post-detail.html",{
#         "post":selected_post,
#         "post_tags":selected_post.tags.all()
#             })

# class PostDetailView(DetailView):
#     template_name = "blog/post-detail.html"
#     model = Post
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context["post_tags"] = self.object.tags.all()
#         context["comment_form"] = CommentForm()
#         return context

class PostDetailView(View):
    def is_saved_post(self,request,post_id):
        saved_posts = request.session.get("saved_posts")
        if saved_posts is not None:
            is_saved = post_id in saved_posts
        else:
            is_saved = False
        return is_saved

    def get(self,request,slug):
        post = Post.objects.get(slug=slug)
        
        context = {
            "post" : post,
            "post_tags" : post.tags.all(),
            "comment_form" : CommentForm(),
            "comments": post.comments.all().order_by("-id"),
            "saved_for_later":self.is_saved_post(request,post.id)
        }
        return render(request,"blog/post-detail.html",context)

    def post(self,request,slug):
        comment_form = CommentForm(request.POST)
        post = Post.objects.get(slug=slug)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.post = post
            comment.save()
            return HttpResponseRedirect(reverse("selectedpost",args=[slug]))
        
        context = {
            "post" : post,
            "post_tags" : post.tags.all(),
            "comment_form" : comment_form,
            "comments":post.comments.all(),
            "saved_for_later":self.is_saved_post(request,post.id),
        }
        return render(request,"blog/post-detail.html",context)


class SavePostView(View):
    def get(self,request):
        saved_posts = request.session.get("saved_posts")
        context = {}
        if saved_posts is None or len(saved_posts) == 0:
            context["posts"] = []
            context["has_posts"] = False
        else:
            posts = Post.objects.filter(id__in=saved_posts)
            context["posts"] = posts
            context["has_posts"] = True
        return render(request,"blog/saved_posts.html",context)

    def post(self,request):
        saved_posts = request.session.get("saved_posts")
        if saved_posts is None:
            saved_posts = []
        post_id = int(request.POST["post_id"])
        if post_id not in saved_posts:
            saved_posts.append(post_id)
            request.session["saved_posts"] = saved_posts
        else:
            saved_posts.remove(post_id)
        request.session["saved_posts"] = saved_posts
        return HttpResponseRedirect("/index")