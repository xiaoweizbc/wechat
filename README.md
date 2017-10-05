#Django框架接入微信公众号demo
### 集成步骤
	1.创建项目wechat
	2.创建应用gtest
	3.主要编写wechat\gtest\views.py视图文件
	4.运行项目后，将路由地址配置到公众号后台，例如：http://127.0.0.1:8000/weixin_test/
	（127.0.0.1:8000属于本地回环地址，实际应改为运行项目主机的公网地址）

#wechat-sdk接口调用示例代码
###一、新增临时素材
```
import urllib
import StringIO
from wechat_sdk.exceptions import OfficialAPIError
url = 'http://wx3.sinaimg.cn/mw690/a716fd45ly1fioum9l9ucj208c08cweg.jpg'
r = urllib.urlopen(url)
imgBuf  = StringIO.StringIO(r.read())
print("type of imgBuf =",type(imgBuf))
try:
a = wechat.upload_media (media_type="image", media_file=imgBuf, extension="jpg")
	print(a)
except OfficialAPIError,e:
	print(e)
```
### 二、客服消息
#####1.发送文本消息
```
user_id = ""
content = "\n...\n..\n."
wechat.send_text_message(user_id, content)
```
#####2.发送图片消息
```
user_id = ""
media_id = a["media_id"]
wechat.send_image_message(user_id, media_id)
```
### 三、获取用户基本信息
```
{
    "subscribe": 1, 
    "openid": "o6_bmjrPTlm6_2sgVt7hMZOPfL2M", 
    "nickname": "Band", 
    "sex": 1, 
    "language": "zh_CN", 
    "city": "广州", 
    "province": "广东", 
    "country": "中国", 
    "headimgurl": "http://wx.qlogo.cn/mmopen/g3MonUZtNHkdmzicIlibx6iaFqAc56vxLSUfpb6n5WKSYVY0ChQKkiaJSgQ1dZuTOgvLLrhJbERQQ4eMsv84eavHiaiceqxibJxCfHe/0", 
    "subscribe_time": 1382694957,
    "unionid": "o6_bmasdasdsad6_2sgVt7hMZOPfL",
    "remark": "",
    "groupid": 0
}
```
```
user_id = ""
nickname = wechat.get_user_info(access_token=access_token, user_id=user_id, lang='zh_CN')["nickname"]
print nickname
```
附：详细接口说明请访问官网文档：https://wechat-sdk.doraemonext.com/
