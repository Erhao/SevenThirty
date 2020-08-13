# -*- encoding: utf-8 -*-

""" 微信服务端API相关 """


import requests
from config.wx_conf import config as wx_config
from config.conf_local import appid, appsecret


async def get_session_with_code(auth_code):
    """ 微信临时登录凭证code换取openid, session_key等信息
        https://developers.weixin.qq.com/miniprogram/dev/api-backend/open-api/login/auth.code2Session.html

    Args:
        auth_code: 临时登录凭证

    Returns:
        ...
    """
    # appid=APPID&secret=SECRET&js_code=JSCODE&grant_type=authorization_code
    payload = {
        "appid": appid,
        "secret": appsecret,
        "js_code": auth_code,
        "grant_type": "authorization_code"
    }
    result = requests.get(wx_config["code2session_url"], params=payload)
    print('----------------', result.json())
    return "ok"
