from django.conf.urls import url,include
from api.views import auth
from api.views import topic
from api.views import news
from api.views import favor
from api.views import detailuser
from api.views import kinds
from api.views import newslist
from api.views import notice
from api.web import manage as web_auction
urlpatterns = [

    url('login/', auth.LoginView.as_view()),
    url(r'^credential/', auth.CredentialView.as_view()),
    url(r'^topic/$', topic.TopicView.as_view()),
    url(r'^news/$', news.NewsView.as_view()),
    url(r'^notice/$', notice.NoticeView.as_view()),
    url(r'notice/delete/(?P<pk>\d+)/$', notice.NoticeDeleteView.as_view()),
    url(r'^news/(?P<pk>\d+)/$', news.NewsDetailView.as_view()),
    url(r'^favor/', favor.FavorView.as_view()),
    url(r'comment_favor/', favor.ChildFavorView.as_view()),
    url(r'^detailuser/$', detailuser.DetailUser.as_view()),
    url(r'^kinds/$', kinds.KindsNewsView.as_view()),
    url(r'^newslist/$', newslist.NewsListView.as_view()),
    # 后台处理
    url(r'auction/delete/(?P<pk>\d+)/$', web_auction.AuctionDeleteView.as_view()),
    url(r'comment/delete/(?P<pk>\d+)/$', web_auction.CommentDeleteView.as_view()),
    # url(r'auction/add/$', web_auction.AuctionAdd),
    # url(r'auction/add/(?P<pk>\d+)/$', web_auction.AuctionItemAdd),

    url(r'auction/edit/(?P<pk>\d+)/$', web_auction.NewsEditView.as_view()),
    #url(r'auction/edit/$', web_auction.NewsEditViews.as_view()),
    #url(r'auction/editimage/$', web_auction.NewsEditImage.as_view()),
    # url(r'auction/item/detail/$', web_auction.AuctionItemDetail),





    url(r'^comment/$', news.CommentView.as_view()),
]
