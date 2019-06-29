from django.shortcuts import render    #render 响应调用。
from django.http import HttpResponse
from . import models

# Create your views here.

def index(request):     #request  is default.
    #pass
    #return HttpResponse("hello,world,daiyi")   ###响应这句话。
    #return render(request,"index.html")    ##把模板的html 给返回响应。
    #return render(request,"index.html",{'hellog':'hello,blog'})    ##传参。  {{hellog}} html里调用 字典的 键。
    #return render(request,"blog/index.html",{'hellog':'hello,blog'})    ##解决app冲突，路径 "blog/index.html"
    #article=models.Article.objects.get(pk=2)
    #return render(request,"blog/index.html",{'article':article})
    articles = models.Article.objects.all() ##获取所有对象。(集合形式。)
    return render(request,"blog/index.html",{'articles':articles}) 

def article_page(request,article_id):
    article=models.Article.objects.get(pk=article_id)
    return render(request,"blog/article_page.html",{'article':article})

# def article_edit(request):
#     #article=models.Article.objects.get(pk=article_id)
#     return render(request,"blog/article_edit.html")

def article_edit(request,article_id):
    if str(article_id) == "0":
        return render(request,"blog/article_edit.html")
    article=models.Article.objects.get(pk=article_id)
    return render(request,"blog/article_edit.html",{'article':article})  # 一个def方法，就对应返回一个 html文件。

def edit_action(request):
    title = request.POST.get('title','title')
    content = request.POST.get('content','content')
    article_id = request.POST.get('article_id','0')
    
    if article_id == "0":
        models.Article.objects.create(title=title,content=content)
        articles = models.Article.objects.all()
        return render(request,"blog/index.html",{'articles':articles})

    article=models.Article.objects.get(pk=article_id)   
    article.title=title
    article.content=content
    article.id=article_id
    article.save()      ###object的内容修改与保存。
    article=models.Article.objects.get(pk=article_id)
    return render(request,"blog/article_page.html",{'article':article})
