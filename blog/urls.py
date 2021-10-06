from django.urls import path
from . import views

urlpatterns = [
    path('index/',views.starting_page,name="starting-page"),
    path('allposts/',views.posts,name="allposts"),
    path('selected/<slug:slug>/',views.PostDetailView.as_view(),name="selectedpost"),
    path("home",views.index),
    path("savepost",views.SavePostView.as_view(),name="save-post")
]