# -*- encoding: utf-8 -*-

""" 七牛云相关工具方法 """

from uuid import uuid4

from qiniu import Auth, BucketManager
from config.conf_local import local_conf


async def upload_to_qiniu(url):
    """ 抓取网络资源到空间

    Args:
        url: 网络图片url
    """
    #构建鉴权对象
    q = Auth(local_conf.qiniu['AccessKey'], local_conf.qiniu['SecretKey'])
    #要上传的空间
    bucket_name = local_conf.qiniu['bucket_name']
    bucket_manager = BucketManager(q)
    key = str(uuid4()) + '.jpg'
    _ret, info = bucket_manager.fetch(url, bucket_name, key)
    if info.status_code == 200:
        return local_conf.qiniu['cdn_prefix'] + key
    return url
