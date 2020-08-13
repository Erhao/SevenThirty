# -*- encoding: utf-8 -*-

from fastapi import FastAPI
from pydantic import BaseModel
from weixin.helper import get_session_with_code

app = FastAPI()


class WxLoginReq(BaseModel):
    auth_code: str


@app.get("/test")
def test():
    return {"msg": "that's ok"}


@app.post("/wx_register")
async def wx_register(req: WxLoginReq):
    """ 接收小程序发来的auth_code换取用户信息, 持久化存储并返回自定义登录态

    Args:
        auth_code

    Returns:
        token
    """
    result = await get_session_with_code(req.auth_code)
    print('-----------------res', result)
    return {"code": 0}
