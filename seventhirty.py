# -*- encoding: utf-8 -*-

import jwt

from fastapi import FastAPI, Request
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from wx.helper import get_session_with_code, wx_biz_data_decrypt
from models.user import test as model_test, wx_register_openid, wx_register_userinfo, get_primary_plant_id
from models.stpi import save_img_url
from config.conf_local import secret_salt
from err_codes import SevenThirtyException, error_codes
from config.conf_local import secret_salt


app = FastAPI()


class WxRegisterReq(BaseModel):
    auth_code: str


class WxRegisterResp(BaseModel):
    token: str
    code: int
    message: str


class WxRegisterUnionidReq(BaseModel):
    token: str
    userInfo: dict
    signature: str
    encryptedData: str
    iv: str


class StpiImgReq(BaseModel):
    token: str
    img_url: str
    plant_id: int


class IndexReq(BaseModel):
    token: str


# 全局错误捕获中间件
@app.middleware("http")
async def catch_error(request: Request, call_next):
    try:
        response = await call_next(request)
        return response
    except Exception as e:
        resp = jsonable_encoder(e)
        return JSONResponse(content=resp)


@app.get("/test")
async def test():
    # raise Exception
    await model_test()
    return {"code": 0}


@app.post("/stpmini/wx_register")
async def wx_register(req: WxRegisterReq):
    """ 接收小程序发来的auth_code换取用户信息, 持久化存储并返回自定义登录态

    Args:
        auth_code: 临时登录凭证, 用来换取openid和session_key

    Returns:
        token: 自定义登录态
        code: 错误码
    """
    result = await get_session_with_code(req.auth_code)
    await wx_register_openid(result['openid'])
    sign_data = {
        "openid": result['openid'],
        "session_key": result['session_key']
    }
    token = jwt.encode(sign_data, secret_salt, algorithm='HS256')
    return WxRegisterResp(**{"token": token, "code": 0, "message": "success"})


@app.post("/stpmini/wx_register_unionid")
async def wx_register_unionid(req: WxRegisterUnionidReq):
    """ 接收小程序发来的加密信息, 解密后将用户信息持久化存储

    Args:
        userInfo: rawData的JSON.verify版本
        signature: 用户信息签名
        encryptedData: 完整用户信息的加密数据
        iv: 加密算法的初始向量

    Returns:
        ...
    """
    sign_data = {}
    try:
        sign_data = jwt.decode(req.token, secret_salt, algorithms=['HS256'])
    except:
        raise SevenThirtyException(**error_codes.INVALID_TOKEN)
    if 'openid' not in sign_data or 'session_key' not in sign_data:
        raise SevenThirtyException(**error_codes.INVALID_TOKEN)
    # 目前不满足获取unionid条件, 直接存储user_info
    # result = await wx_biz_data_decrypt(req.encryptedData, req.iv, sign_data['session_key'])
    await wx_register_userinfo(sign_data['openid'], req.userInfo)
    return {"code": 0, "message": "ok"}


@app.get("stpmini/index")
async def get_index(req: IndexReq):
    sign_data = {}
    try:
        sign_data = jwt.decode(req.token, secret_salt, algorithms=['HS256'])
    except:
        raise SevenThirtyException(**error_codes.INVALID_TOKEN)
    if 'openid' not in sign_data or 'session_key' not in sign_data:
        raise SevenThirtyException(**error_codes.INVALID_TOKEN)
    # 获取用户设置的首页展示植株
    primary_plant_id = await get_primary_plant_id(sign_data['openid'])
    # 根据首页展示植株id获取小程序首页需要的所有信息
    pass


@app.post("/stpi/img")
async def recv_img(req: StpiImgReq):
    sign_data = {}
    # 校验来自STPI的请求合法性
    try:
        sign_data = jwt.decode(req.token, secret_salt, algorithms=['HS256'])
    except:
        raise SevenThirtyException(**error_codes.INVALID_TOKEN)
    else:
        if 'datetime' not in sign_data or 'camera_id' not in sign_data:
            raise SevenThirtyException(**error_codes.INVALID_TOKEN)
    await save_img_url(req.img_url, sign_data['datetime'], req.plant_id, sign_data['camera_id'])
