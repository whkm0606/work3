from rest_framework.authentication import BaseAuthentication
from api import models
from rest_framework import exceptions


# 普通认证(可以要用户登录也可以不用)没有通过就跳过这继续向后运行
class GeneralAuthentication(BaseAuthentication):
    def authenticate(self, request):
        token = request.META.get('HTTP_AUTHORIZATION', None)
        # 如果没有获取到token(即未登录状态)
        if not token:
            return None
        # 获取我们ur路径上的pk(news_id)
        # pk = kwargs.get('pk')
        user_object = models.UserInfo.objects.filter(token=token).first()
        # 判断token是否正确
        if not user_object:
            return None
        return (user_object, token)


# 用户认证(必须要用户登录后才能访问的页面)没有通过就不能往后运行
class UserAuthentication(BaseAuthentication):
    def authenticate(self, request):
        token = request.META.get('HTTP_AUTHORIZATION', None)
        # 如果没有获取到token(即未登录状态)
        if not token:
            raise exceptions.AuthenticationFailed()
        # 获取我们ur路径上的pk(news_id)
        # pk = kwargs.get('pk')
        user_object = models.UserInfo.objects.filter(token=token).first()
        # 判断token是否正确
        if not user_object:
            raise exceptions.AuthenticationFailed()
        return (user_object, token)
