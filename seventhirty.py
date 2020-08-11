# -*- encoding: utf-8 -*-

from fastapi import FastAPI

app = FastAPI()

@app.get("/test")
def test():
    return {"msg": "that's ok"}


@app.post("/wx_register")
def wx_register():
    """ 接收小程序发来的auth_code换取用户信息, 持久化存储并返回自定义登录态

    Args:
        auth_code

    Returns:
        token
    """
    pass
