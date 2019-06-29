from __future__ import unicode_literals
from django.db import models
# Create your models here.

class Article(models.Model):
    title = models.CharField(max_length=32,default='Title')  ## max_length=32  必须参数。
    content = models.TextField(null=True)

    def __str__(self):              #返回 名称。
        return self.title           #依据其中的元素返回。