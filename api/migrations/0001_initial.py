# Generated by Django 3.2.18 on 2023-04-26 03:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ManageInfo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('account', models.CharField(max_length=11, verbose_name='账户')),
                ('nickname', models.CharField(max_length=64, verbose_name='昵称')),
                ('password', models.CharField(max_length=64, verbose_name='密码')),
                ('avatar', models.CharField(max_length=64, verbose_name='头像')),
            ],
        ),
        migrations.CreateModel(
            name='News',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cover', models.CharField(max_length=128, verbose_name='封面')),
                ('content', models.CharField(max_length=255, verbose_name='内容')),
                ('address', models.CharField(blank=True, max_length=128, null=True, verbose_name='位置')),
                ('kinds', models.CharField(blank=True, max_length=255, null=True, verbose_name='类型')),
                ('favor_count', models.PositiveIntegerField(default=0, verbose_name='赞数')),
                ('viewer_count', models.PositiveIntegerField(default=0, verbose_name='浏览数')),
                ('comment_count', models.PositiveIntegerField(default=0, verbose_name='评论数')),
                ('create_date', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
            ],
        ),
        migrations.CreateModel(
            name='Notice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.CharField(max_length=255, verbose_name='内容')),
                ('create_date', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
            ],
        ),
        migrations.CreateModel(
            name='Topic',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=32, verbose_name='分类')),
                ('count', models.PositiveIntegerField(default=0, verbose_name='该类数量')),
            ],
        ),
        migrations.CreateModel(
            name='UserInfo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('telephone', models.CharField(max_length=11, verbose_name='手机号')),
                ('nickname', models.CharField(max_length=64, verbose_name='昵称')),
                ('avatar', models.CharField(max_length=64, verbose_name='头像')),
                ('token', models.CharField(blank=True, max_length=64, null=True, verbose_name='用户Token')),
            ],
        ),
        migrations.CreateModel(
            name='ViewerRecord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('news', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.news', verbose_name='动态')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.userinfo', verbose_name='用户')),
            ],
        ),
        migrations.CreateModel(
            name='NewsFavorRecord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('news', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.news', verbose_name='动态')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.userinfo', verbose_name='点赞用户')),
            ],
        ),
        migrations.CreateModel(
            name='NewsDetail',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.CharField(help_text='用于以后在腾讯对象存储中删除', max_length=128, verbose_name='腾讯对象存储中的文件名')),
                ('cos_path', models.CharField(max_length=128, verbose_name='腾讯对象存储中图片路径')),
                ('news', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.news', verbose_name='动态')),
            ],
        ),
        migrations.AddField(
            model_name='news',
            name='topic',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='api.topic', verbose_name='话题'),
        ),
        migrations.AddField(
            model_name='news',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='news', to='api.userinfo', verbose_name='发布者'),
        ),
        migrations.CreateModel(
            name='CommentRecord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.CharField(max_length=255, verbose_name='评论内容')),
                ('create_date', models.DateTimeField(auto_now_add=True, verbose_name='评论时间')),
                ('depth', models.PositiveIntegerField(default=1, verbose_name='评论层级')),
                ('favor_count', models.PositiveIntegerField(default=0, verbose_name='赞数')),
                ('news', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.news', verbose_name='动态')),
                ('reply', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='replys', to='api.commentrecord', verbose_name='回复')),
                ('root', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='roots', to='api.commentrecord', verbose_name='根评论')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.userinfo', verbose_name='评论者')),
            ],
        ),
        migrations.CreateModel(
            name='CommentFavorRecord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('comment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.commentrecord', verbose_name='动态')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.userinfo', verbose_name='点赞用户')),
            ],
        ),
    ]
