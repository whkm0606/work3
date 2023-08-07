from rest_framework.response import Response
import json
from rest_framework.views import APIView
from api import models
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import datetime
from .web_form.NewsModelForm import AuctionCreateForm, AuctionItemCreateForm
import uuid
# from api import task
from django.db.models import F

#删除失物招领
class AuctionDeleteView(APIView):
    def post(self, request, *args, **kwargs):
        new_id = json.loads(request.body.decode('utf8')).get('new_id')
        if not new_id:
            return Response({'status': False, 'message': "请传入有效id"})
        models.news.objects.filter(id=new_id).delete()
        return Response({'status': True, 'message': '删除成功'})

#删除失物招领图片
def NewItemImgDelete(request, pk):
    if request.method == "GET":
        iid = request.GET.get('iid')
        if not iid and pk:
            return JsonResponse({'status': False, 'message': '不欧克'})
        models.newsdetail.objects.filter(item_id=pk, id=iid).delete()
        return JsonResponse({'status': True, 'message': 'ok'})
# 删除失物招领
def NewItemDeleteView(request, pk):
    new_id = json.loads(request.body.decode('utf8')).get('news_id')
    if not new_id:
        return Response({'status': False, 'message': "请传入有效信息id"})
    if not pk:
        return Response({'status': False, 'message': "请传入有效信息id"})
    print(pk)
    models.news.objects.filter(id=new_id, new_id=pk).delete()
    # models.Auction.objects.filter(id=pk).update(goods_count=F('goods_count') - 1)
    return JsonResponse({'status': True, 'message': '删除成功'})


@csrf_exempt
def AuctionItemAdd(request, pk):
    if not pk:
        return JsonResponse({'status': False, 'message': 'id为空'})
    if request.method == "POST":

        new_obj = models.new.objects.filter(id=pk).first()
        if not new_obj:
            return JsonResponse({'status': False, 'message': '不ok'})

        content = json.loads(request.body.decode('utf8')).get('content')

       # content['auction'] = auction_obj
        # 创建拍品
        if not content.get('id'):
            form = AuctionItemCreateForm(data=content)
        else:
            auction_item_obj = models.AuctionItem.objects.filter(id=content['id'], auction=auction_obj).first()
            form = AuctionItemCreateForm(data=content, instance=auction_item_obj)
        if form.is_valid():
            form.instance.uid = str(uuid.uuid4())
            if not content.get('id'):
                form.instance.auction.goods_count += 1
                form.instance.auction.save()
            item = form.save()
            content.pop('auction')
            content['id'] = item.id
            content['status_name'] = item.get_status_display()
            # auction_item = form.save(commit=False)
            # auction_item.uid = str(uuid.uuid4())
            # auction_item.save()
            return JsonResponse({'status': True, 'message': content})
        return JsonResponse({'status': False, 'message': form.errors.get_json_data()})


@csrf_exempt
def AuctionItemDetail(request):
    if request.method == "POST":
        context = json.loads(request.body.decode('utf8'))
        did = context.get('id')
        print(context)
        auction_detail_obj = models.AuctionItemDetail.objects
        if not did:
            context.pop('id')
            auction_obj = auction_detail_obj.create(**context)
            return JsonResponse({'status': True, 'message': auction_obj.id})
        auction_detail_obj.filter(id=did, item_id=context['item_id']).update(value=context['value'], key=context['key'])
        return JsonResponse({'status': True, 'message': 'ok'})
