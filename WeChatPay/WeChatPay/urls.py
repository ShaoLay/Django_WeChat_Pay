"""WeChatPay URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from django.views.static import serve

from WeChatPay.WeChatPay import settings
from WeChatPay.pay import views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url('buy/', views.buy),  # 打开购买页面
    url('to_pay/', views.wxpay, name='to_pay'),  # 跳转二维码扫描页面
    url('check_wxpay/', views.check_wxpay),  # 支付结果验签
    url('static/<str:path>', serve, {'document_root': settings.STATIC_ROOT}),  # 静态文件访问配置
]
