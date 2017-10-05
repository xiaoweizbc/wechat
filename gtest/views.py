# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.http.response import HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from wechat_sdk import WechatConf
from wechat_sdk import WechatBasic
from wechat_sdk.exceptions import OfficialAPIError
from wechat_sdk.exceptions import ParseError
from wechat_sdk.messages import (TextMessage, ImageMessage, VoiceMessage, VideoMessage, ShortVideoMessage, LinkMessage,
                                 LocationMessage, EventMessage)

# Create your views here.
your_token = ""
your_appid = ""
your_appsecret = ""
encrypt_mode = "compatible"  # 测试公众号只能用normal和compatible，不能用safe
encoding_aes_key = ""

conf = WechatConf(
    token=your_token,
    appid=your_appid,
    appsecret=your_appsecret,
    encrypt_mode=encrypt_mode,  # 可选项：normal/compatible/safe，分别对应于 明文/兼容/安全 模式
    encoding_aes_key=encoding_aes_key  # 如果传入此值则必须保证同时传入 token, appid
)

# 实例化 WechatBasic
wechat = WechatBasic(conf=conf)

access_token = wechat.get_access_token()['access_token']
access_token_expires_at = wechat.get_access_token()['access_token_expires_at']


@csrf_exempt
def index(request):
    param_dict = dict(zip(request.GET.keys(), request.GET.values()))
    # for (d, x) in param_dict.items():
    #     print(d + " : " + x)
    if request.method == 'GET':  # GET：接入时用到
        nonce = request.GET.get('nonce')
        timestamp = request.GET.get('timestamp')
        echostr = request.GET.get('echostr')
        signature = request.GET.get("signature")
        if not wechat.check_signature(signature=signature, timestamp=timestamp, nonce=nonce):
            print("接入错误！")
            return HttpResponseBadRequest('请到 <微信公众平台-开发-基本配置> 接入！')
        else:
            print("接入成功！")
            return HttpResponse(echostr, content_type="text/plain")

    if request.method == 'POST':  # POST：开发时用到
        body_text = request.body
        try:
            # 如果在实例化 WechatConf 时传入了 encrypt_mode='safe'，
            # 那么在调用本方法进行解析消息时必须传入 msg_signature / timestamp / nonce 三个参数，
            # 否则会无法解密消息。
            if encrypt_mode == "safe":
                nonce = param_dict["nonce"]
                timestamp = param_dict["timestamp"]
                msg_signature = param_dict["msg_signature"]
                wechat.parse_data(data=body_text, msg_signature=msg_signature, timestamp=timestamp, nonce=nonce)
            else:
                wechat.parse_data(data=body_text)
            # 获取解析后的信息:公共信息和私有信息
            # 当调用.parse_data()方法解析成功后，你可以直接获取解析后的具体信息：
            # 1.公共信息获取
            id = wechat.message.id  # 对应于 XML 中的 MsgId
            target = wechat.message.target  # 对应于 XML 中的 ToUserName
            source = wechat.message.source  # 对应于 XML 中的 FromUserName
            time = wechat.message.time  # 对应于 XML 中的 CreateTime
            type = wechat.message.type  # 对应于 XML 中的 MsgType
            raw = wechat.message.raw  # 原始 XML 文本，方便进行其他分析
            # print "id : ",id
            # print "target : ", target
            # print "source : ", source
            # print "time : ", time
            # print "type : ", type
            # print "raw\n", raw
        except ParseError:
            # 当解析 XML 失败时抛出 exceptions.ParseError 异常。
            print("Invalid Body Text")
            return HttpResponseBadRequest('Invalid XML Data')

        # 私有信息获取
        if isinstance(wechat.message, TextMessage):  # 处理文本信息
            content = wechat.message.content  # 对应于 XML 中的 Content
            try:
                nickname = wechat.get_user_info(access_token=access_token, user_id=source, lang='zh_CN')["nickname"]
                print "用户", nickname, "(" + source + ")", "发来<文本>：", content
            except OfficialAPIError as e:
                print e
                print "用户", source, "发来<文本>：", content
            if content == '功能':
                reply = (
                    '目前支持的功能：\n'
                    '1. 使用标准普通话发送语音，会有意想不到的回复哦！"\n'
                    '2. 发送照片，等到图片地址！\n'
                    '3. 发送位置可查经纬度！\n'
                    '还有更多功能正在开发中哦 ^_^\n'
                )
                response = wechat.response_text(content=reply, escape=False)
            else:
                reply = "emmmmmmmm..."
                response = wechat.response_text(content=reply, escape=False)

        elif isinstance(wechat.message, ImageMessage):  # 处理图片信息（不包括gif）
            picurl = wechat.message.picurl
            media_id = wechat.message.media_id
            print "用户", source, "发来<图片>："
            print picurl
            print media_id
            response = wechat.response_image(media_id)  # 发回原图

        elif isinstance(wechat.message, VoiceMessage):  # 处理语音信息
            media_id = wechat.message.media_id  # 对应于 XML 中的 MediaId
            format = wechat.message.format  # 对应于 XML 中的 Format
            recognition = wechat.message.recognition  # 对应于 XML 中的 Recognition
            print "用户", source, "发来<语音>："
            print media_id
            print format
            print recognition
            response = wechat.response_text(content="语音识别：" + recognition)

        elif isinstance(wechat.message, VideoMessage):  # 处理视频信息
            media_id = wechat.message.media_id  # 对应于 XML 中的 MediaId
            thumb_media_id = wechat.message.thumb_media_id  # 对应于 XML 中的 ThumbMediaId
            print "用户", source, "发来<视频>："
            print media_id
            print thumb_media_id
            response = wechat.response_text(content="收到视频，over!")

        elif isinstance(wechat.message, ShortVideoMessage):  # 处理小视频信息
            media_id = wechat.message.media_id  # 对应于 XML 中的 MediaId
            thumb_media_id = wechat.message.thumb_media_id  # 对应于 XML 中的 ThumbMediaId
            print "用户", source, "发来<小视频>："
            print media_id
            print thumb_media_id
            response = wechat.response_text(content="收到小视频，over!")

        elif isinstance(wechat.message, LocationMessage):  # 处理地理位置信息
            location = wechat.message.location  # Tuple(X, Y)，对应于 XML 中的 (Location_X, Location_Y)
            scale = wechat.message.scale  # 对应于 XML 中的 Scale
            label = wechat.message.label  # 对应于 XML 中的 Label
            print "用户", source, "发来<地理位置>："
            print location, isinstance(location, tuple)
            print scale
            print label, isinstance(label, unicode)
            longitude = str(location[0])
            latitude = str(location[1])
            reply = "收到地理位置，over!\n" \
                    + longitude + "," + latitude + "(经纬度)\n" \
                    + label
            response = wechat.response_text(content=reply)

        elif isinstance(wechat.message, LinkMessage):  # 处理链接信息--因无法给公众号发送链接消息，无法测试
            title = wechat.message.title
            description = wechat.message.description
            url = wechat.message.url
            print "用户", source, "发来<链接>："
            print title
            print description
            print url
            response = wechat.response_text(content="收到")

        elif isinstance(wechat.message, EventMessage):  # 处理事件信息
            if wechat.message.type == 'subscribe':  # 关注事件(包括普通关注事件和扫描二维码造成的关注事件)
                key = wechat.message.key  # 对应于 XML 中的 EventKey (普通关注事件时此值为 None)
                ticket = wechat.message.ticket  # 对应于 XML 中的 Ticket (普通关注事件时此值为 None)
                print "target(用户) : ", target
                print "关注了"
                print "source(公众号) : ", source
                print key
                print ticket
                response = wechat.response_text(
                    content=(
                        '感谢老哥or老姐or老铁关注**的公众号！\n'
                        '回复【功能】可查看支持的功能，还可以回复任意内容和机器人开始聊天哦！\n'
                        '..........\n'
                        '........\n'
                        '......\n'
                        '....\n'
                        '..\n'
                        '.\n'
                    ))
            elif wechat.message.type == 'unsubscribe':  # 取消关注事件（无可用私有信息）
                print "target(用户) : ", target
                print "取消关注了"
                print "source(公众号) : ", source
                response = None
            elif wechat.message.type == 'scan':  # 用户已关注时的二维码扫描事件
                key = wechat.message.key  # 对应于 XML 中的 EventKey
                ticket = wechat.message.ticket  # 对应于 XML 中的 Ticket
                print "用户已关注时的二维码扫描事件"
                print key
                print ticket
                response = wechat.response_text(content="收到")
            elif wechat.message.type == 'location':  # 上报地理位置事件
                latitude = wechat.message.latitude  # 对应于 XML 中的 Latitude
                longitude = wechat.message.longitude  # 对应于 XML 中的 Longitude
                precision = wechat.message.precision  # 对应于 XML 中的 Precision
                print latitude
                print longitude
                print precision
                response = wechat.response_text(content="收到")
            elif wechat.message.type == 'click':  # 自定义菜单点击事件
                key = wechat.message.key  # 对应于 XML 中的 EventKey
                print key
                response = wechat.response_text(content="收到")
            elif wechat.message.type == 'view':  # 自定义菜单跳转链接事件
                key = wechat.message.key  # 对应于 XML 中的 EventKey
                print key
                response = wechat.response_text(content="收到")

        return HttpResponse(response, content_type="application/xml")
