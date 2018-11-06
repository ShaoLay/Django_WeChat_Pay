import hashlib
from random import Random
import time

import qrcode as qrcode
from bs4 import BeautifulSoup
from django.contrib.sites import requests
from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.


# 报名首页
from django.views.decorators.csrf import csrf_exempt

from WeChatPay.WeChatPay import settings


def buy(request):
    return render(request,'buy.html')

# 定义字典转XML的函数
def trans_dict_to_xml(data_dict):
    data_xml = []
    for k in sorted(data_dict.keys()):  # 遍历字典排序后的key
        v = data_dict.get(k)  # 取出字典中key对应的value
        if k == 'detail' and not v.startswith('<![CDATA['):  # 添加XML标记
            v = '<![CDATA[{}]]>'.format(v)
        data_xml.append('<{key}>{value}</{key}>'.format(key=k, value=v))
    return '<xml>{}</xml>'.format(''.join(data_xml))  # 返回XML

# 定义XML转字典的函数
def trans_xml_to_dict(data_xml):
    soup = BeautifulSoup(data_xml, features='xml')
    xml = soup.find('xml')  # 解析XML
    if not xml:
        return {}
    data_dict = dict([(item.name, item.text) for item in xml.find_all()])
    return data_dict


# 发起微信支付
def wxpay(request):
    nonce_str = random_str()  # 拼接出随机的字符串即可，我这里是用  时间+随机数字+5个随机字母

    total_fee = 1  # 付款金额，单位是分，必须是整数
    body = 'baoming'  # 商品描述
    out_trade_no = order_num(user_id=request.POST.get('phone', '12345'))  # 订单编号

    params = {
        'appid': settings._APP_ID,  # APPID
        'mch_id': settings._MCH_ID,  # 商户号
        'nonce_str': nonce_str,  # 回调地址
        'out_trade_no': out_trade_no,  # 订单编号
        'total_fee': total_fee,  # 订单总金额
        'spbill_create_ip': settings._CREATE_IP,  # 发送请求服务器的IP地址
        'notify_url': settings._NOTIFY_URL,  # 支付回调地址
        'body': body,  # 商品描述
        'trade_type': 'NATIVE'  # 扫码支付
    }

    sign = get_sign(params, settings._API_KEY)  # 获取签名
    params['sign'] = sign  # 添加签名到参数字典
    # print(params)
    xml = trans_dict_to_xml(params)  # 转换字典为XML
    response = requests.request('post', settings._UFDODER_URL, data=xml)  # 以POST方式向微信公众平台服务器发起请求
    data_dict = trans_xml_to_dict(response.content)  # 将请求返回的数据转为字典
    qrcode_name = out_trade_no + '.png'  # 支付二维码图片保存路径

    if data_dict.get('return_code') == 'SUCCESS':  # 如果请求成功
        img = qrcode.make(data_dict.get('code_url'))  # 创建支付二维码片
        img.save('static' + '/' + qrcode_name)  #

        return render(request, 'qrcode.html', {'qrcode_img': qrcode_name})  # 为支付页面模板传入二维码图像

    return HttpResponse('交易请求失败！')


# 支付成功后回调
@csrf_exempt  # 去除csrf验证
def check_wxpay(request):
    data_dict = trans_xml_to_dict(request.body)  # 回调数据转字典
    sign = data_dict.pop('sign')  # 取出签名
    key = settings._API_KEY  # 商户交易密钥
    back_sign = get_sign(data_dict, key)  # 计算签名
    if sign == back_sign:  # 验证签名是否与回调签名相同
        '''
        检查对应业务数据的状态，判断该通知是否已经处理过，如果没有处理过再进行处理，如果处理过直接返回结果成功。
        '''
        print('支付成功！')
        return HttpResponse('SUCCESS')
    else:
        '''
            此处编写支付失败后的业务逻辑
        '''

        return HttpResponse('failed')


# 获取签名
def get_sign(data_dict, key):  # 签名函数，参数为签名的数据和密钥
    params_list = sorted(data_dict.items(), key=lambda e: e[0], reverse=False)  # 参数字典倒排序为列表
    params_str = "&".join(u"{}={}".format(k, v) for k, v in params_list) + '&key=' + key
    # 组织参数字符串并在末尾添加商户交易密钥
    md5 = hashlib.md5()  # 使用MD5加密模式
    md5.update(params_str.encode())  # 将参数字符串传入
    sign = md5.hexdigest().upper()  # 完成加密并转为大写
    return sign


# 生成订单号
def order_num(package_id=12345, user_id=56789):
    # 商品id后2位+下单时间的年月日12+用户2后四位+随机数4位
    local_time = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))[2:]
    result = str(package_id)[-2:] + local_time + str(user_id)[-2:] + str(random.randint(1000, 9999))
    return result


# 生成随机字符串
def random_str(randomlength=8):
    str = ''
    chars = 'AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789'
    length = len(chars) - 1
    random = random.Random()
    for i in range(randomlength):
        str += chars[random.randint(0, length)]
    return str

