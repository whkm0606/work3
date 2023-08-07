import re
import random
import uuid

from rest_framework.views import APIView
from rest_framework.response import Response
from django_redis import get_redis_connection

from api import models
#from utils.tencent.msg import send_message
from api.serializer.account import MessageSerializer, LoginSerializer


class MessageView(APIView):
    def get(self, request, *args, **kwargs):
        """
        发送手机短信验证码
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        # 1.获取手机号
        # 2.手机格式校验
        ser = MessageSerializer(data=request.query_params)
        if not ser.is_valid():
            return Response({'status': False, 'message': '手机格式错误'})
        phone = ser.validated_data.get('phone')

        # 3.生成随机验证码
        random_code = random.randint(1000, 9999)
        # 5.把验证码+手机号保留（30s过期）
        """
        result = send_message(phone,random_code)
        if not result:
            return Response({"status": False, 'message': '短信发送失败'})
        """
        print(random_code)

        """
        #   5.1 搭建redis服务器（云redis）
        #   5.2 django中方便使用redis的模块 django-redis
               配置:
                    CACHES = {
                        "default": {
                            "BACKEND": "django_redis.cache.RedisCache",
                            "LOCATION": "redis://127.0.0.1:6379",
                            "OPTIONS": {
                                "CLIENT_CLASS": "django_redis.client.DefaultClient",
                                "CONNECTION_POOL_KWARGS": {"max_connections": 100}
                                # "PASSWORD": "密码",
                            }
                        }
                    }
                使用：
        """


        conn = get_redis_connection()
        conn.set(phone, random_code, ex=60)

        return Response({"status": True, 'message': '发送成功'})


class LoginView(APIView):

    def post(self, request, *args, **kwargs):
        """
        1. 校验手机号是否合法
        2. 校验验证码，redis
            - 无验证码
            - 有验证码，输入错误
            - 有验证码，成功

        4. 将一些信息返回给小程序
        """
        #正式操作
        # ser = LoginSerializer(data=request.data)
        # if not ser.is_valid():
        #     return Response({"status": False, 'message': '验证码错误'})
        # phone = ser.validated_data.get('phone')
        # nickname = ser.validated_data.get('nickname')
        # avatar = ser.validated_data.get('avatar')

        # 3. 去数据库中获取用户信息（获取/创建）
        phone = request.data.get('phone')
        nickname = request.data.get('nickname')
        avatar = request.data.get('avatar')
        user_object, flag = models.UserInfo.objects.get_or_create(
            telephone = phone,
            defaults = {
                "nickname": nickname,
                'avatar' : avatar}
         )
        user_object.token = str(uuid.uuid4())
        user_object.save()

        return Response({"status": True, "data": {"token": user_object.token,'phone': phone}})





class CredentialView(APIView):

    def get(self,request,*args,**kwargs):
        from sts.sts import Sts
        from django.conf import settings
        config = {
            # 临时密钥有效时长，单位是秒
            'duration_seconds': 1800,
            # 固定密钥 id
            'secret_id': settings.TENCENT_SECRET_ID,
            # 固定密钥 key
            'secret_key': settings.TENCENT_SECRET_KEY,
            # 设置网络代理
            # 'proxy': {
            #     'http': 'xx',
            #     'https': 'xx'
            # },
            # 换成你的 bucket
            'bucket': 'shiwuzhaoling-1317046259',
            # 换成 bucket 所在地区
            'region': 'ap-nanjing',
            # 这里改成允许的路径前缀，可以根据自己网站的用户登录态判断允许上传的具体路径
            # 例子： a.jpg 或者 a/* 或者 * (使用通配符*存在重大安全风险, 请谨慎评估使用)
            'allow_prefix': '*',
            # 密钥的权限列表。简单上传和分片需要以下的权限，其他权限列表请看
            'allow_actions': [
                'name/cos:PostObject',
                'name/cos:PutObject',
                'name/cos:DeleteObject',
            ],

        }
        sts = Sts(config)
        response = sts.get_credential()
        return Response(response)
# class CredentialView(APIView):
#     import json
#     import os
#
#     from sts.sts import Sts
#
#     if __name__ == '__main__':
#
#         def get_credential_demo():
#             config = {
#                 # 请求URL，域名部分必须和domain保持一致
#                 # 使用外网域名时：https://sts.tencentcloudapi.com/
#                 # 使用内网域名时：https://sts.internal.tencentcloudapi.com/
#                 'url': 'https://sts.tencentcloudapi.com/',
#                 # 域名，非必须，默认为 sts.tencentcloudapi.com
#                 # 内网域名：sts.internal.tencentcloudapi.com
#                 'domain': 'sts.tencentcloudapi.com',
#                 # 临时密钥有效时长，单位是秒
#                 'duration_seconds': 1800,
#                 'secret_id': settings.TENCENT_SECRET_ID,
#                 # 固定密钥
#                 'secret_key': settings.TENCENT_SECRET_KEY,
#                 # 设置网络代理
#                 # 'proxy': {
#                 #     'http': 'xx',
#                 #     'https': 'xx'
#                 # },
#                 # 换成你的 bucket
#                 'bucket': 'shiwuzhaoling-1317046259',
#                 # 换成 bucket 所在地区
#                 'region': 'ap-nanjing',
#                 # 这里改成允许的路径前缀，可以根据自己网站的用户登录态判断允许上传的具体路径
#                 # 例子： a.jpg 或者 a/* 或者 * (使用通配符*存在重大安全风险, 请谨慎评估使用)
#                 'allow_prefix': ['exampleobject', 'exampleobject2'],
#                 # 密钥的权限列表。简单上传和分片需要以下的权限，其他权限列表请看 https://cloud.tencent.com/document/product/436/31923
#                 'allow_actions': [
#                     # 简单上传
#                     'name/cos:PutObject',
#                     'name/cos:PostObject',
#                 ],
#                 # 临时密钥生效条件，关于condition的详细设置规则和COS支持的condition类型可以参考 https://cloud.tencent.com/document/product/436/71306
#                 "condition": {
#                     "ip_equal": {
#                         "qcs:ip": [
#                             "10.217.182.3/24",
#                             "111.21.33.72/24",
#                         ]
#                     }
#                 }
#             }
#
#             try:
#                 sts = Sts(config)
#                 response = sts.get_credential()
#                 print('get data : ' + json.dumps(dict(response), indent=4))
#             except Exception as e:
#                 print(e)
#
#         def get_role_credential_demo():
#             config = {
#                 # 请求URL，域名部分必须和domain保持一致
#                 # 使用外网域名时：https://sts.tencentcloudapi.com/
#                 # 使用内网域名时：https://sts.internal.tencentcloudapi.com/
#                 'url': 'https://sts.internal.tencentcloudapi.com/',
#                 # 域名，非必须，默认为外网域名 sts.tencentcloudapi.com
#                 # 内网域名：sts.internal.tencentcloudapi.com
#                 'domain': 'sts.internal.tencentcloudapi.com',
#                 # 临时密钥有效时长，单位是秒
#                 'duration_seconds': 1800,
#                 'secret_id': setting.TENCENT_SECRET_ID,
#                 # 固定密钥
#                 'secret_key': setting.TENCENT_SECRET_KEY,
#                 # 设置网络代理
#                 # 'proxy': {
#                 #     'http': 'xx',
#                 #     'https': 'xx'
#                 # },
#                 # 换成你的 bucket
#                 'bucket': 'shiwuzhaoling-1317046259',
#                 # 换成 bucket 所在地区
#                 'region': 'ap-nanjing',
#                 # 这里改成允许的路径前缀，可以根据自己网站的用户登录态判断允许上传的具体路径
#                 # 例子： a.jpg 或者 a/* 或者 * (使用通配符*存在重大安全风险, 请谨慎评估使用)
#                 'allow_prefix': ['exampleobject', 'exampleobject2'],
#                 # 密钥的权限列表。简单上传和分片需要以下的权限，其他权限列表请看 https://cloud.tencent.com/document/product/436/31923
#                 'allow_actions': [
#                     # 简单上传
#                     'name/cos:PutObject',
#                     'name/cos:PostObject',
#                 ],
#                 # 临时密钥生效条件，关于condition的详细设置规则和COS支持的condition类型可以参考 https://cloud.tencent.com/document/product/436/71306
#                 "condition": {
#                     "ip_equal": {
#                         "qcs:ip": [
#                             "10.217.182.3/24",
#                             "111.21.33.72/24",
#                         ]
#                     }
#                 }
#             }
#
#             try:
#                 sts = Sts(config)
#                 role_arn = 'qcs::cam::uin/12345678:roleName/testRoleName'  # 角色的资源描述，可在cam访问管理，点击角色名获取
#                 response = sts.get_role_credential(role_arn=role_arn)
#                 print('get data : ' + json.dumps(dict(response), indent=4))
#             except Exception as e:
#                 print(e)


























