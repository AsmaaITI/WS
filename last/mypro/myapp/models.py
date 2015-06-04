from django.db import models


# Create your models here.


class UserInfo(models.Model):
	name = models.CharField(max_length=50) 
	email= models.CharField(max_length=50,unique=True)
        password= models.CharField(max_length=50)
        facebookId= models.CharField(max_length=50)
        profilepicture= models.ImageField(upload_to='myapp/static/users',default='myapp/static/users/default.jpg',null=True, blank=True)
	hasfacebook =models.BooleanField(default=False)
        

class Article(models.Model):
	head= models.CharField(max_length=50) 
	body= models.TextField()
        image= models.ImageField(upload_to='myapp/static/')
        date= models.DateTimeField(auto_now_add=True)
        published=models.BooleanField(default=False) 

class Comment(models.Model):
        content= models.TextField()
	date= models.DateTimeField()
        userId = models.ForeignKey(UserInfo)
        articleId = models.ForeignKey(Article)
        commentId = models.IntegerField(null=True)

class ArticleLikes(models.Model):
        userId = models.ForeignKey(UserInfo)
        articleId = models.ForeignKey(Article)

class CommentLikes(models.Model):
        userId = models.ForeignKey(UserInfo)
	commentId = models.ForeignKey(Comment)

class Tags(models.Model):
        word=models.CharField(max_length=50)
        relatedId = models.ForeignKey(Article)#articleid
  	
