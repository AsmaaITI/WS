# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Article',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('head', models.CharField(max_length=50)),
                ('body', models.TextField()),
                ('image', models.ImageField(upload_to=b'myapp/static/')),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('published', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='ArticleLikes',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('articleId', models.ForeignKey(to='myapp.Article')),
            ],
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('content', models.TextField()),
                ('date', models.DateTimeField()),
                ('commentId', models.IntegerField(null=True)),
                ('articleId', models.ForeignKey(to='myapp.Article')),
            ],
        ),
        migrations.CreateModel(
            name='CommentLikes',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('commentId', models.ForeignKey(to='myapp.Comment')),
            ],
        ),
        migrations.CreateModel(
            name='Tags',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('word', models.CharField(max_length=50)),
                ('relatedId', models.ForeignKey(to='myapp.Article')),
            ],
        ),
        migrations.CreateModel(
            name='UserInfo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
                ('email', models.CharField(unique=True, max_length=50)),
                ('password', models.CharField(max_length=50)),
                ('facebookId', models.CharField(max_length=50)),
                ('profilepicture', models.ImageField(default=b'myapp/static/users/default.jpg', null=True, upload_to=b'myapp/static/users', blank=True)),
                ('hasfacebook', models.BooleanField(default=False)),
            ],
        ),
        migrations.AddField(
            model_name='commentlikes',
            name='userId',
            field=models.ForeignKey(to='myapp.UserInfo'),
        ),
        migrations.AddField(
            model_name='comment',
            name='userId',
            field=models.ForeignKey(to='myapp.UserInfo'),
        ),
        migrations.AddField(
            model_name='articlelikes',
            name='userId',
            field=models.ForeignKey(to='myapp.UserInfo'),
        ),
    ]
