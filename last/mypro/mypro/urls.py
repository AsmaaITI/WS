from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [
        url(r'^forgetpass/$', 'myapp.views.forgetpass'),
	url('', include('social.apps.django_app.urls', namespace='social')),
	url(r'^facebooklogin/','myapp.views.facebooklogin'),
        url(r'^facebookregister/','myapp.views.facebookregister'),
	url(r'^sendmail/$', 'myapp.views.sendmail'),
	url(r'^renew/$', 'myapp.views.renew'),
	url(r'^savepass/$', 'myapp.views.savepass'),
        url(r'^article/(?P<art_id>\d+)/$','myapp.views.article'),
	url(r'^like/(?P<art_id>\d+)/(?P<cmt_id>\d+)/$','myapp.views.like'),
	url(r'^unlike/(?P<art_id>\d+)/(?P<cmt_id>\d+)/$','myapp.views.unlike'),
	url(r'^home/$','myapp.views.home'),
	url(r'^articles/$','myapp.views.all_articles'),
	url(r'^admin/', include(admin.site.urls)),
	url(r'^article/$','myapp.views.article'),
	url(r'^$', 'myapp.views.index'),
	url(r'^index/$', 'myapp.views.index'),
	url(r'^login/$', 'myapp.views.login'),
	url(r'^logout/$', 'myapp.views.logout'),
	url(r'^saveUserfacebook/$', 'myapp.views.saveUserfacebook'),
	url(r'^register/$', 'myapp.views.register'),
	url(r'^saveUser/$', 'myapp.views.saveUser'),
	url(r'^profile/$', 'myapp.views.profile'),
	url(r'^updateprofile/$', 'myapp.views.updateprofile'),
	url(r'', 'myapp.views.notvalid'),
	
]
