# -*- encoding: utf-8 -*-

""" 微信服务端API相关 """

import requests
import base64
import redis
import json

from config.wx_conf import config as wx_config
from config.conf_local import appid, appsecret
from err_codes import SevenThirtyException, error_codes
from Crypto.Cipher import AES
from config.conf_local import local_conf


async def get_session_with_code(auth_code):
    """ 微信临时登录凭证code换取openid, session_key等信息, 并将session_key持久化
        https://developers.weixin.qq.com/miniprogram/dev/api-backend/open-api/login/auth.code2Session.html

    Args:
        auth_code: 临时登录凭证

    Returns:
        openid: 用户在小程序的唯一标识
        session_key: 会话秘钥, 可用于解密wx.getUserInfo获取到的加密数据
    """
    payload = {
        "appid": appid,
        "secret": appsecret,
        "js_code": auth_code,
        "grant_type": "authorization_code"
    }
    result = requests.get(wx_config['code2session_url'], params=payload).json()
    if 'errcode' in result:
        if result['errcode'] == 40029:
            raise SevenThirtyException(**error_codes.WX_INVALID_CODE)
        raise SevenThirtyException(**error_codes.WX_REGISTER_FAIL)
    try:
        # TODO(mbz): import redis from utils.db
        rds = redis.StrictRedis(host=local_conf.redis['HOST'], port=local_conf.redis['PORT'], db=local_conf.redis['DB'], password=local_conf.redis['PASSWORD'])
        rds.set(wx_config['session_key_prefix'] + result['openid'], result['session_key'])
    except:
        raise SevenThirtyException(**error_codes.REDIS_CONNECTION_FAIL)
    return result


async def wx_biz_data_decrypt(encrypted_data, iv, session_key):
    """
        解密wx.getUserInfo获取的加密数据
    """
    session_key_b64 = base64.b64decode(session_key)
    encrypted_data_b64 = base64.b64decode(encrypted_data)
    iv_b64 = base64.b64decode(iv)
    cipher = AES.new(session_key_b64, AES.MODE_CBC, iv_b64)
    decrypted_data_str = cipher.decrypt(encrypted_data_b64)
    decrypted_data = json.loads(decrypted_data_str[:-ord(decrypted_data_str[len(decrypted_data_str)-1:])])
    if decrypted_data['watermark']['appid'] != appid:
        raise SevenThirtyException(**error_codes.WX_INVALID_ENCRYPTED_DATA)
    return decrypted_data
