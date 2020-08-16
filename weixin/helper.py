# -*- encoding: utf-8 -*-

""" 微信服务端API相关 """


import requests
from config.wx_conf import config as wx_config
from config.conf_local import appid, appsecret
from err_codes import SevenThirtyException, error_codes


async def get_session_with_code(auth_code):
    """ 微信临时登录凭证code换取openid, session_key等信息
        https://developers.weixin.qq.com/miniprogram/dev/api-backend/open-api/login/auth.code2Session.html

    Args:
        auth_code: 临时登录凭证

    Returns:
        openid: 用户在小程序的唯一标识
        session_key: 会话秘钥
    """
    payload = {
        "appid": appid,
        "secret": appsecret,
        "js_code": auth_code,
        "grant_type": "authorization_code"
    }
    result = requests.get(wx_config["code2session_url"], params=payload).json()
    print('c2s res', result)
    if 'errcode' in result:
        if result['errcode'] == 40029:
            raise SevenThirtyException(**error_codes.WX_BAD_CODE)
        raise SevenThirtyException(**error_codes.WX_REGISTER_FAIL)
    return result
