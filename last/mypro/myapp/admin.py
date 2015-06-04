from django.contrib import admin
from myapp.models import Article,UserInfo,Tags
# Register your models here.


class TagAdmin(admin.TabularInline):
     model=Tags

class ArticleAdmin(admin.ModelAdmin):
    readonly_fields = ('date',)
    list_display = ( 'head', 'body', 'image', 'published')
    list_filter = ['date','published']
    search_fields = ['date',]
    inlines=[TagAdmin]

class UserInfoAdmin(admin.ModelAdmin):
    readonly_fields = ('facebookId','hasfacebook','profilepicture')
    list_display = ( 'name', 'email', 'password')
    list_filter = ['hasfacebook',]

class TagtestAdmin(admin.ModelAdmin):
     model=Tags



admin.site.register(Article,ArticleAdmin)
admin.site.register(UserInfo, UserInfoAdmin)
admin.site.register(Tags,TagtestAdmin)


