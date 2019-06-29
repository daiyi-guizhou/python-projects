from django.conf.urls import url

from . import views
app_name='blog'  #避免url的 href name 时候出错。
urlpatterns = [            
    #url(r'^index/$',views.index), #子路径。http://127.0.0.1:8000/index/index/     ## 要r'^index/$' 而不是。 r'^index$'
    url(r'^$',views.index), #子路径。http://127.0.0.1:8000/blog
    #url(r'^article/(?P<article_id>[0-9]+)$',views.article_page), #子路径。http://127.0.0.1:8000/blog/article/1
    url(r'^article/(?P<article_id>[0-9]+)$',views.article_page,name='article_page'), #href的设置，没有include，就直接用name
    url(r'^article_edit/(?P<article_id>[0-9]+)$',views.article_edit,name='article_edit'), #一个url.py的url语句，对应views.的一个方法，
    #views.article_edit就是方法名。 
    url(r'^article_edit/action/$',views.edit_action,name='edit_action')
]
