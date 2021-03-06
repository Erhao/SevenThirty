# -*- encoding: utf-8 -*-

import jwt
import time

from fastapi import FastAPI, Request
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from wx.helper import get_session_with_code, wx_biz_data_decrypt
from models.user import (
    test as model_test,
    wx_register_openid,
    wx_register_userinfo,
    get_primary_plant_id,
    get_user,
    get_user_plants,
    get_rank_list,
    get_point_and_rank,
    calculate_point
)
from models.stpi import save_img_url
from models.plant import get_plant, get_plant_imgs_with_same_time_pointer
from models.environment import get_latest_humi_and_temp
from config.conf_local import secret_salt
from err_codes import SevenThirtyException, error_codes
from config.conf_local import secret_salt, local_conf
from constants import constants
from scheduler.point import update_point_and_rank
from mqtt.mqtt_jobs import pub_watering_cmd, sub_soil_moisture, sub_temp_humi
from utils.db.redis_conn import redis_cli
from multiprocessing import Process


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


class WateringReq(BaseModel):
    token: str
    plant_id: int


# 全局错误捕获中间件
@app.middleware("http")
async def catch_error(request: Request, call_next):
    try:
        response = await call_next(request)
        return response
    except Exception as e:
        resp = jsonable_encoder(e)
        return JSONResponse(content=resp)


# 定时任务
@app.on_event('startup')
async def init_scheduler():
    """
        初始化定时任务
    """
    scheduler = AsyncIOScheduler()
    scheduler.add_job(update_point_and_rank, 'cron', hour=7, minute=30)

    scheduler.start()


# 多进程监听土壤湿度上报
@app.on_event('startup')
def init_sub_soil_moisture():
    """
        监听土壤湿度上报
    """
    sub_soil_moisture_process = Process(target=sub_soil_moisture)
    sub_soil_moisture_process.start()


# 多进程监听空气温湿度上报
@app.on_event('startup')
def init_sub_temp_humi():
    """
        监听土壤湿度上报
    """
    sub_temp_humi_process = Process(target=sub_temp_humi)
    sub_temp_humi_process.start()


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


@app.get("/stpmini/index")
async def get_index(token: str):
    sign_data = {}
    try:
        sign_data = jwt.decode(token, secret_salt, algorithms=['HS256'])
    except:
        raise SevenThirtyException(**error_codes.INVALID_TOKEN)
    if 'openid' not in sign_data or 'session_key' not in sign_data:
        raise SevenThirtyException(**error_codes.INVALID_TOKEN)
    # 获取用户设置的首页展示植株, 如果用户未授权则默认展示plant_id=1的植株信息
    user = await get_user(sign_data['openid'])
    # serial<0 即为未授权用户
    is_authoried = True if user[3] >= 0 else False
    primary_plant_id = await get_primary_plant_id(sign_data['openid']) if is_authoried else 1
    # 根据首页展示植株id获取小程序首页需要的所有信息
    # 1. 获取plant自身信息
    plant = await get_plant(primary_plant_id)
    # 2. 获取最近的同一时间点的照片信息
    plant_imgs = await get_plant_imgs_with_same_time_pointer(primary_plant_id)
    # 3. 获取最近的温湿度
    latest_humi, latest_temp = await get_latest_humi_and_temp(primary_plant_id)
    # 组装
    planting_days = (datetime.now() - plant[3]).days
    latest_5_imgs = []
    for plant_img in plant_imgs:
        latest_5_imgs.append({
            "datetime": plant_img[4],
            "img_url": plant_img[2]
        })
    result = {
        "plant_id": plant[0],
        "plant_name": plant[1],
        "plant_img_url": plant[2],
        "planting_days": planting_days,
        "latest_5_imgs": latest_5_imgs,
        "latest_humi": latest_humi,
        "latest_temp": latest_temp
    }
    return {"code": 0, "message": "success", "data": result}


@app.get("/stpmini/mine")
async def get_mine(token: str):
    sign_data = {}
    try:
        sign_data = jwt.decode(token, secret_salt, algorithms=['HS256'])
    except:
        raise SevenThirtyException(**error_codes.INVALID_TOKEN)
    if 'openid' not in sign_data or 'session_key' not in sign_data:
        raise SevenThirtyException(**error_codes.INVALID_TOKEN)
    user = await get_user(sign_data['openid'])
    _, plants = await get_user_plants(sign_data['openid'])
    serial = user[3]
    type_count = len(set([ plant[4] for plant in plants ]))
    plant_count = len(plants)
    primary_plant_id = await get_primary_plant_id(sign_data['openid'])
    index_plant_name = list(filter(lambda plant: plant[0] == primary_plant_id, plants))[0][1]
    result = {
        "serial": serial,
        "type_count": type_count,
        "plant_count": plant_count,
        "index_plant_name": index_plant_name
    }
    return {"code": 0, "message": "success", "data": result}


@app.get("/stpmini/mine/total_point")
async def get_mine_total_point(token: str):
    sign_data = {}
    try:
        sign_data = jwt.decode(token, secret_salt, algorithms=['HS256'])
    except:
        raise SevenThirtyException(**error_codes.INVALID_TOKEN)
    if 'openid' not in sign_data or 'session_key' not in sign_data:
        raise SevenThirtyException(**error_codes.INVALID_TOKEN)
    point_and_rank = await get_point_and_rank(sign_data['openid'])
    result = {
        "point": point_and_rank[0],
        "rank": point_and_rank[1]
    }
    return {"code": 0, "message": "success", "data": result}


@app.get("/stpmini/mine_category")
async def get_mine_category(token: str):
    sign_data = {}
    try:
        sign_data = jwt.decode(token, secret_salt, algorithms=['HS256'])
    except:
        raise SevenThirtyException(**error_codes.INVALID_TOKEN)
    if 'openid' not in sign_data or 'session_key' not in sign_data:
        raise SevenThirtyException(**error_codes.INVALID_TOKEN)
    _, plants = await get_user_plants(sign_data['openid'])
    result = {}
    for plant in plants:
        if plant[4] not in result:
            result[constants.PLANT_TYPE[plant[4]]] = [{
                "plant_name": plant[1],
                "applicant_name": plant[8],
                "planting_at": plant[3].strftime("%Y-%m-%d")
            }]
        else:
            result[constants.PLANT_TYPE[plant[4]]].append([{
                "plant_name": plant[1],
                "applicant_name": plant[8],
                "planting_at": plant[3].strftime("%Y-%m-%d")
            }])
    return {"code": 0, "message": "success", "data": result}


@app.get("/stpmini/mine_plant")
async def get_mine_plant(token: str):
    sign_data = {}
    try:
        sign_data = jwt.decode(token, secret_salt, algorithms=['HS256'])
    except:
        raise SevenThirtyException(**error_codes.INVALID_TOKEN)
    if 'openid' not in sign_data or 'session_key' not in sign_data:
        raise SevenThirtyException(**error_codes.INVALID_TOKEN)
    user_plants, plants = await get_user_plants(sign_data['openid'])
    plant_id_plant_info = {
        user_plant[0]: {
            "plant_id": user_plant[0],
            "watering_times": user_plant[2],
            "is_primary_plant": user_plant[1]
        } for user_plant in user_plants
    }
    plant_name_plant_info = {
        plant[1]: plant_id_plant_info[plant[0]] for plant in plants
    }
    return {"code": 0, "message": "success", "data": plant_name_plant_info}


@app.get("/stpmini/rank")
async def get_rank(token: str, plant_id: int):
    sign_data = {}
    try:
        sign_data = jwt.decode(token, secret_salt, algorithms=['HS256'])
    except:
        raise SevenThirtyException(**error_codes.INVALID_TOKEN)
    if 'openid' not in sign_data or 'session_key' not in sign_data:
        raise SevenThirtyException(**error_codes.INVALID_TOKEN)
    plant = await get_plant(plant_id)
    user_plants, users = await get_rank_list(plant_id)
    openid_nickname = {
        user[0]: user[4] for user in users
    }
    rank_list = []
    rank = -1
    max_watering_times = float('inf')
    for user_plant in user_plants:
        if max_watering_times > user_plant[3]:
            max_watering_times = user_plant[3]
            rank += 1
        rank_info = {
            "user_id": user_plant[0],
            "user_name": openid_nickname[user_plant[0]],
            "watering_times": user_plant[3],
            "rank": rank,
            "is_self": 1 if user_plant[0] == sign_data['openid'] else 0
        }
        rank_list.append(rank_info)
    return {"code": 0, "message": "success", "data": {
        "plant_name": plant[1],
        "rank_list": rank_list,
    }}


@app.get("/stpmini/plant")
async def get_plant_with_id(token: str, plant_id: int):
    sign_data = {}
    try:
        sign_data = jwt.decode(token, secret_salt, algorithms=['HS256'])
    except:
        raise SevenThirtyException(**error_codes.INVALID_TOKEN)
    if 'openid' not in sign_data or 'session_key' not in sign_data:
        raise SevenThirtyException(**error_codes.INVALID_TOKEN)
    plant = await get_plant(plant_id)
    result = {
        "plant_id": plant[0],
        "plant_name": plant[1],
        "planting_at": plant[3].strftime("%Y-%m-%d"),
        "type": constants.PLANT_TYPE[plant[0]],
        "intro": plant[6],
        "applicant_name": plant[8],
    }
    return {"code": 0, "message": "success", "data": result}


@app.post("/stpmini/watering")
async def watering(req: WateringReq):
    sign_data = {}
    try:
        sign_data = jwt.decode(req.token, secret_salt, algorithms=['HS256'])
    except:
        raise SevenThirtyException(**error_codes.INVALID_TOKEN)
    if 'openid' not in sign_data or 'session_key' not in sign_data:
        raise SevenThirtyException(**error_codes.INVALID_TOKEN)

    now = datetime.now()
    # 距离上次浇水时间小于30min则驳回请求
    latest_watering_info_res = redis_cli.get(constants.REDIS_LATEST_WATERING_INFO_PREFIX + str(req.plant_id)).decode('utf-8')
    latest_watering_datetime = datetime.strptime(latest_watering_info_res.split(',')[0], '%Y-%m-%d %H:%M:%S')
    if (now - latest_watering_datetime).seconds < 1800:
        return {"code": 0, "message": "success", "data": {
            "status": constants.WATERING_REQ_STATUS['rejected'],
            "msg": "刚刚浇过水了, 等会儿再来试试吧~"
        }}

    # 最近一次上报的土壤湿度为'1'则驳回请求
    latest_soil_moisture_res = redis_cli.get(constants.REDIS_LATEST_SOIL_MOISTURE_PREFIX + str(req.plant_id)).decode('utf-8')
    if latest_soil_moisture_res == constants.SOIL_MOISTURE['WET']:
        return {"code": 0, "message": "success", "data": {
            "status": constants.WATERING_REQ_STATUS['rejected'],
            "msg": "土壤水分充足, 等会儿再来试试吧~"
        }}

    # 获得积分 = 1.0 * 土壤湿度系数 * 时间规则系数
    """
        土壤湿度系数:
            1       -       距离上一次浇水0.5h~4h
            1.1     -       距离上一次浇水4h~6h
            1.2     -       距离上一次浇水6h~12h
            1.4     -       距离上一次浇水12h~24h
            1.8     -       距离上一次浇水>24h
        时间规则系数:
            1       -       12:00~15:00
            1.2     -       其他时间段
    """
    soil_moisture_coefficient = 1
    hours = (now - latest_watering_datetime).seconds / 3600
    if hours <= 4:
        soil_moisture_coefficient = 1
    elif hours <= 6:
        soil_moisture_coefficient = 1.1
    elif hours <= 12:
        soil_moisture_coefficient = 1.2
    elif hours <= 24:
        soil_moisture_coefficient = 1.4
    else:
        soil_moisture_coefficient = 1.8

    time_rule_coefficient = 1
    if now.hour <= 12 or now.hour >= 15:
        time_rule_coefficient = 1.2

    point = int(100 * soil_moisture_coefficient * time_rule_coefficient)
    await calculate_point(sign_data['openid'], req.plant_id, point)

    # 更新redis最近一次浇水信息
    user = await get_user(sign_data['openid'])
    new_latest_watering_info = now.strftime("%Y-%m-%d %H:%M:%S") + ',' + user[4]
    redis_cli.set(constants.REDIS_LATEST_WATERING_INFO_PREFIX + str(req.plant_id), new_latest_watering_info)

    # 发布浇水命令
    pub_watering_cmd_process = Process(target=pub_watering_cmd, args=(req, sign_data))
    pub_watering_cmd_process.start()

    return {"code": 0, "message": "success", "data": {
        "status": constants.WATERING_REQ_STATUS['success'],
        "msg": "预计用时15秒, 正在浇水中..."
    }}


@app.get("/stpmini/latest_watering_info")
async def get_latest_watering_info(token: str, plant_id: int):
    sign_data = {}
    try:
        sign_data = jwt.decode(token, secret_salt, algorithms=['HS256'])
    except:
        raise SevenThirtyException(**error_codes.INVALID_TOKEN)
    if 'openid' not in sign_data or 'session_key' not in sign_data:
        raise SevenThirtyException(**error_codes.INVALID_TOKEN)
    latest_watering_info_res = redis_cli.get(constants.REDIS_LATEST_WATERING_INFO_PREFIX + str(plant_id)).decode('utf-8')
    latest_watering_time = latest_watering_info_res.split(',')[0]
    latest_watering_user = latest_watering_info_res.split(',')[1]
    return {"code": 0, "message": "success", "data": {
        "latest_watering_time": latest_watering_time,
        "latest_watering_user": latest_watering_user,
    }}


@app.post("/stpi/img")
async def recv_img(req: StpiImgReq):
    sign_data = {}
    # 校验来自STPI的请求合法性
    try:
        sign_data = jwt.decode(req.token, secret_salt, algorithms=['HS256'])
    except:
        raise SevenThirtyException(**error_codes.INVALID_TOKEN)
    if 'datetime' not in sign_data or 'camera_id' not in sign_data:
        raise SevenThirtyException(**error_codes.INVALID_TOKEN)
    time_pointer = int(req.img_url.split('.')[-2].split('_')[-2])
    await save_img_url(req.img_url, sign_data['datetime'], req.plant_id, sign_data['camera_id'], time_pointer)
    return
