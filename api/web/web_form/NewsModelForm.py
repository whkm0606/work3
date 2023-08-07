from api import models
from django import forms
from django.core import validators
from datetime import datetime


class AuctionCreateForm(forms.ModelForm):
    class Meta:
        model = models.News
        exclude = ['total_price', 'goods_count', 'bid_count', 'look_count', 'video']
        error_messages = {
            'cover': {
                'required': '封面页不能为空'
            },
            'title': {
                'required': '标题不能为空'
            },
            'preview_start_time': {
                'required': '预展开始时间不能为空'
            },
            'preview_end_time': {
                'required': '预展结束时间不能为空'
            },
            'auction_start_time': {
                'required': '拍卖开始时间不能为空'
            },
            'auction_end_time': {
                'required': '拍卖结束时间不能为空'
            }
        }

    def clean_cover(self):
        cover = self.cleaned_data.get('cover')
        if not cover:
            raise validators.ValidationError('封面页不能为空')
        return cover


class AuctionItemCreateForm(forms.ModelForm):

    class Meta:
        model = models.NewsDetail
        exclude = ['video', 'bid_count', 'look_count', 'uid']
