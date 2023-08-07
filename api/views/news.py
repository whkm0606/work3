
import itertools
import collections
from urllib import request

from django.forms import model_to_dict
from rest_framework import serializers
from rest_framework.filters import BaseFilterBackend
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from api.serializer.pages import MaxBaseFilterBackend, MinBaseFilterBackend, NewsListLimitOffsetPagination
from api.serializer.auth import GeneralAuthentication,UserAuthentication
from django.db.models import Max
from api import models
import collections
from django.db.models import F



# ################################ 动态列表 ################################

class CreateNewsTopicModelSerializer(serializers.Serializer):#序列化
    key = serializers.CharField()
    cos_path = serializers.CharField()


class CreateNewsModelSerializer(serializers.ModelSerializer):
    imageList = CreateNewsTopicModelSerializer(many=True)
    token = serializers.CharField()
    topic_id = serializers.CharField()
    Response(imageList)
    print(imageList)
    class Meta:
        model = models.News
        # fields = "__all__"
        exclude = [ 'user','viewer_count', 'comment_count','favor_count']

    def create(self, validated_data):
        image_list = validated_data.pop('imageList')##切割newDetail字典数据
        print(image_list)
        print(1)
        # 获取用户信息
        token = validated_data.pop('token')##切割token数据
        user_object = models.UserInfo.objects.filter(token=token).first()
        print(token)
        print(user_object)
        validated_data['user'] = user_object
        news_object = models.News.objects.create(**validated_data)##创建news表中数据
        data_list = models.NewsDetail.objects.bulk_create(
            [models.NewsDetail(**info, news=news_object) for info in image_list]
        )
        news_object.imageList = data_list
        news_object.token = token

        if news_object.topic:
            news_object.topic.count += 1
            news_object.save()

        return news_object


class ListNewsModelSerializer(serializers.ModelSerializer):
    topic = serializers.SerializerMethodField()
    user = serializers.SerializerMethodField()


    class Meta:
        model = models.News
        exclude = ['address', ]

    def get_topic(self, obj):

        if not obj.topic:
            return
        return model_to_dict(obj.topic, ['id', 'title'])

    def get_user(self, obj):
        return model_to_dict(obj.user, ['id', 'nickname', 'avatar','token'])

class NewsView(CreateAPIView, ListAPIView):

    """
    获取动态列表
    """
    serializer_class = ListNewsModelSerializer
    queryset = models.News.objects.prefetch_related('user', 'topic').order_by("-id")
    pagination_class = NewsListLimitOffsetPagination
    filter_backends = [MinBaseFilterBackend, MaxBaseFilterBackend]
#加到最小值，最大值

    def perform_create(self, serializer):
        # 调用save 其先调用creat()
        new_object = serializer.save()
        return new_object

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CreateNewsModelSerializer
        if self.request.method == 'GET':
            return ListNewsModelSerializer


# ################################ 动态详细 ################################
class NewsDetailModelSerializer(serializers.ModelSerializer):
    images = serializers.SerializerMethodField()
    create_date = serializers.DateTimeField(format="%Y-%m-%d %H:%M")

    user = serializers.SerializerMethodField()
    topic = serializers.SerializerMethodField()

    viewer = serializers.SerializerMethodField()
    comment = serializers.SerializerMethodField()

    favor = serializers.SerializerMethodField()

    class Meta:
        model = models.News
        exclude = ['cover', ]

    def get_images(self, obj):
        detail_queryset = models.NewsDetail.objects.filter(news=obj)
        # return [row.cos_path for row in detail_queryset]
        # return [{'id':row.id,'path':row.cos_path} for row in detail_queryset]
        return [model_to_dict(row, ['id', 'cos_path','key']) for row in detail_queryset]

    def get_user(self, obj):
        return model_to_dict(obj.user, fields=['id', 'nickname', 'avatar','token','telephone'])

    def get_topic(self, obj):
        if not obj.topic:
            return
        return model_to_dict(obj.topic, fields=['id', 'title'])

    def get_viewer(self, obj):
        # 根据新闻的对象 obj(news)
        # viewer_queryset = models.ViewerRecord.objects.filter(news_id=obj.id).order_by('-id')[0:10]
        queryset = models.ViewerRecord.objects.filter(news_id=obj.id)
        viewer_object_list = queryset.order_by('-id')[0:10]
        context = {
            'count': queryset.count(),
            'result': [model_to_dict(row.user, ['nickname', 'avatar']) for row in viewer_object_list]
        }
        return context

    def get_comment(self, obj):
        """
        获取所有的1级评论，再给每个1级评论获取一个耳机评论。
        :param obj:
        :return:
        """

        # 1.获取所有的 一级 评论
        first_queryset = models.CommentRecord.objects.filter(news=obj, depth=1).order_by('id')[0:10].values(
            'id',
            'content',
            'depth',
            'user__nickname',
            'user__avatar',
            'create_date',
            'favor_count'
        )
        first_id_list = [item['id'] for item in first_queryset]
        # 2.获取所有的二级评论
        # second_queryset = models.CommentRecord.objects.filter(news=obj,depth=2)
        # 2. 获取所有1级评论下的二级评论
        # second_queryset = models.CommentRecord.objects.filter(news=obj, depth=2,reply_id__in=first_id_list)
        # 2. 获取所有1级评论下的二级评论(每个二级评论只取最新的一条)
        from django.db.models import Max
        result = models.CommentRecord.objects.filter(news=obj, depth=2, reply_id__in=first_id_list).values(
            'reply_id').annotate(max_id=Max('id'))
        second_id_list = [item['max_id'] for item in result]  # 5, 8

        second_queryset = models.CommentRecord.objects.filter(id__in=second_id_list).values(
            'id',
            'content',
            'depth',
            'user__nickname',
            'user__avatar',
            'create_date',
            'reply_id',
            'reply__user__nickname',
            'favor_count'
        )
        import collections
        data_list = {}
        user_object = self.context['request'].user

        # 认证不通过执行
        #评论点赞进行传递
        if not user_object:
            for item in first_queryset:
                item['favor'] = False
                #item['favor_count'] = models.CommentRecord.objects.filter(id=item['id'])
                item['create_date'] = item['create_date'].strftime("%Y-%m-%d %H:%M")
                data_list[item['id']] = item
            for row in second_queryset:
                row['create_date'] = row['create_date'].strftime("%Y-%m-%d %H:%M")
                # item['favor_count'] = models.CommentRecord.objects.filter(id=item['id'])
                row['favor'] = False
                data_list[row['reply_id']]['child'] = [row]

            return data_list.values()

        else:
            for item in first_queryset:
                item['favor'] = models.CommentFavorRecord.objects.filter(comment_id=item['id'],
                                                                         user=user_object).exists()
                # item['favor_count'] = models.CommentRecord.objects.filter(id=item['id'])
                item['create_date'] = item['create_date'].strftime("%Y-%m-%d %H:%M")
                data_list[item['id']] = item
            for row in second_queryset:
                row['create_date'] = row['create_date'].strftime("%Y-%m-%d %H:%M")
                # item['favor_count'] = models.CommentRecord.objects.filter(id=item['id'])
                row['favor'] = models.CommentFavorRecord.objects.filter(comment_id=row['id'], user=user_object).exists()
                data_list[row['reply_id']]['child'] = [row]

            return data_list.values()


        # first_dict = collections.OrderedDict()
        # for item in first_queryset:
        #     item['create_date'] = item['create_date'].strftime('%Y-%m-%d')
        #     first_dict[item['id']] = item
        #
        # for node in second_queryset:
        #     first_dict[node['reply_id']]['child'] = [node, ]
        #
        # return first_dict.values()

    def get_favor(self, obj):
        # 1. 用户未登录
        user_object = self.context['request'].user
        if not user_object:
            return False

        # 2. 用户已登录
        exists = models.NewsFavorRecord.objects.filter(user=user_object, news=obj).exists()
        return exists

class NewsDetailView(RetrieveAPIView):
    queryset = models.News.objects
    serializer_class = NewsDetailModelSerializer
    authentication_classes = [GeneralAuthentication]

    def get(self,request,*args,**kwargs):
        response = super().get(request,*args,**kwargs)
        #如果用户已经登录，在访问记录添加一条记录
        #去Authorization的请求头去获取token

        if not request.user:
            return response
        #判断当前用户是否访问该新闻
        new_object = self.get_object()#该新闻是否存在 不存在就会报错（self.get_object()）
        ## pk = kwargs.get('pk') 与上面相同
        #print(new_object,request.user)
        exists = models.ViewerRecord.objects.filter(user = request.user,news= new_object).exists()
        if exists:
            return response
        models.ViewerRecord.objects.create(user = request.user,news= new_object)
        models.News.objects.filter(id = new_object.id).update(viewer_count = F('viewer_count')+1)
        #print(8)
        return  response


# ################################ 发布评论 ################################
"""
"id": 10,
"content": "哈哈哈哈",
"create_date": "2020-01-13 04:39",
"depth": 1,
"nickname": "wupeiqi",
"avatar": "https://mini-1251317460.cos.ap-chengdu.myqcloud.com/08a9daei1578736867828.png",
"reply": null,
"reply_nickname": null,
"""
class CommentModelSerializer(serializers.ModelSerializer):
    create_date = serializers.DateTimeField(format='%Y-%m-%d')
    user__nickname = serializers.CharField(source='user.nickname')
    user__avatar = serializers.CharField(source='user.avatar')
    reply_id = serializers.CharField(source='reply.id')
    reply__user__nickname = serializers.CharField(source='reply.user.nickname')
    class Meta:
        model = models.CommentRecord
        exclude = ['news','user','reply','root']
    def get_favor(self, obj):
        user_object = self.context['request'].user
        if not user_object:
            return False
        # 判断是否有赞
        exists = models.CommentFavorRecord.objects.filter(comment=obj, user=user_object).exists()
        return exists


class CreateCommentModelSerializer(serializers.ModelSerializer):
    create_date = serializers.DateTimeField(format='%Y-%m-%d',read_only=True)
    user__nickname = serializers.CharField(source='user.nickname',read_only=True)
    user__avatar = serializers.CharField(source='user.avatar',read_only=True)
    reply_id = serializers.CharField(source='reply.id',read_only=True)
    reply__user__nickname = serializers.CharField(source='reply.user.nickname',read_only=True)

    class Meta:
        model = models.CommentRecord
        # fields = "__all__"
        exclude = ['user','favor_count']

class CommentView(APIView):

    def get_authenticators(self):
        if self.request.method == "POST":
            return [UserAuthentication(), ]
        return [GeneralAuthentication(), ]

    def get(self,request,*args,**kwargs):
        root_id = request.query_params.get('root')
        # 1. 获取这个根评论的所有子孙评论
        node_queryset = models.CommentRecord.objects.filter(root_id=root_id).order_by('id')
        # 2. 序列化
        ser = CommentModelSerializer(instance=node_queryset,many=True)

        return Response(ser.data,status=status.HTTP_200_OK)

    def post(self,request,*args,**kwargs):
        # 1. 进行数据校验: news/depth/reply/content/root
        ser = CreateCommentModelSerializer(data=request.data)
        if ser.is_valid():
            # 对新增到的数据值进行序列化(数据格式需要调整)
            token = request.data.get('token')
            news_id = request.data.get('news')
            user_object = models.UserInfo.objects.filter(token=token).first()
            ser.save(user=user_object)# 保存到数据库
            models.News.objects.filter(id=news_id).update(comment_count=F('comment_count')+1)

            return Response(ser.data,status=status.HTTP_201_CREATED)
        return Response(ser.errors,status=status.HTTP_400_BAD_REQUEST)




