# -*- encoding: utf-8 -*-

from fastapi import FastAPI, Request
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from weixin.helper import get_session_with_code
from models.user import test as model_test


app = FastAPI()


class WxRegisterReq(BaseModel):
    auth_code: str


class WxRegisterUnionidReq(BaseModel):
    rawData: str
    userInfo: dict
    signature: str
    encryptedData: str
    iv: str


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


@app.post("/wx_register")
async def wx_register(req: WxRegisterReq):
    """ 接收小程序发来的auth_code换取用户信息, 持久化存储并返回自定义登录态

    Args:
        auth_code: 临时登录凭证, 用来换取openid和session_key

    Returns:
        token: 自定义登录态
    """
    result = await get_session_with_code(req.auth_code)
    # TODO(xinyu.zhang): openid持久化

    return result


@app.post("/wx_register_unionid")
async def wx_register_unionid(req: WxRegisterUnionidReq):
    """ 接收小程序发来的加密信息, 解密后将用户信息持久化存储

    Args:
        rawData: wx.getUserInfo获取的原始用户信息, 不包含unionid
        userInfo: rawData的JSON.verify版本
        signature: 用户信息签名
        encryptedData: 完整用户信息的加密数据
        iv: 加密算法的初始向量
    """
    
    return {"code": 0, "message": "ok"}
