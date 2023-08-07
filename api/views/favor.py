from rest_framework.views import APIView
from rest_framework.response import Response
from api import models
from api.serializer.auth import UserAuthentication
from rest_framework import serializers
from rest_framework import status
from django.db.models import F


class FavorModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.NewsFavorRecord
        fields = ["news"]


class ChildFavorModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CommentFavorRecord
        fields = ["comment"]


class FavorView(APIView):
    authentication_classes = [UserAuthentication, ]

    def post(self, request, *args, **kwargs):
        ser = FavorModelSerializer(data=request.data)
        # 如果校验失败(不能为空)
        if not ser.is_valid():
            return Response({}, status=status.HTTP_400_BAD_REQUEST)
        news_object = ser.validated_data.get('news')
        queryset = models.NewsFavorRecord.objects.filter(user=request.user, news=news_object)
        exists = queryset.exists()
        # 在点一次取消并删除
        if exists:
            queryset.delete()
            models.News.objects.filter(id=news_object.id).update(favor_count=F('favor_count') - 1)
            return Response({}, status=status.HTTP_200_OK)

        models.NewsFavorRecord.objects.create(news=news_object, user=request.user)
        models.News.objects.filter(id=news_object.id).update(favor_count=F('favor_count') + 1)
        return Response({}, status=status.HTTP_201_CREATED)


class ChildFavorView(APIView):
    authentication_classes = [UserAuthentication, ]

    def post(self, request, *args, **kwargs):
        ser = ChildFavorModelSerializer(data=request.data)
        # 如果校验失败(不能为空)
        if not ser.is_valid():
            return Response({}, status=status.HTTP_400_BAD_REQUEST)
        comment_object = ser.validated_data.get('comment')
        queryset = models.CommentFavorRecord.objects.filter(user=request.user, comment=comment_object)
        exists = queryset.exists()
        # 在点一次取消并删除
        if exists:
            queryset.delete()
            models.CommentRecord.objects.filter(id=comment_object.id).update(favor_count=F('favor_count') - 1)
            return Response({}, status=status.HTTP_200_OK)
        # 添加
        models.CommentFavorRecord.objects.create(comment=comment_object, user=request.user)
        models.CommentRecord.objects.filter(id=comment_object.id).update(favor_count=F('favor_count') + 1)
        return Response({}, status=status.HTTP_201_CREATED)
