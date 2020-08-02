# -*- encoding: utf-8 -*-

from fastapi import FastAPI

app = FastAPI()

@app.get("/test")
def test():
    return {"msg": "this's ok"}
