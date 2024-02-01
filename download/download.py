import json
import logging.config
import os
import re

import eel
import requests

TISH_PATH = os.path.dirname(__file__)
with open(os.path.join(TISH_PATH, 'logging_config.json'), 'r', encoding="utf-8") as f:
    logging_config = json.loads(f.read())
logging.config.dictConfig(logging_config)
log = logging.getLogger('main')
headers = {
    'user-agent': 'Mozilla/5.0 (Linux; U; Android 9; zh-cn; SM-G977N Build/LMY48Z) AppleWebKit/533.1 (KHTML, like Gecko) Version/5.0 Mobile Safari/533.1',
}


# get download uri
def get_uri(video_id: str) -> tuple:
    log.info('获取下载id')
    url = f'https://www.iesdouyin.com/web/api/v2/aweme/iteminfo/?reflow_source=reflow_page&a_bogus=64745b2b5bdc4e75b720a9a85b19867a&item_ids={video_id}'
    rsp = requests.get(url=url, headers=headers).json()
    video_info = rsp['item_list'][0]
    return video_info['video']['play_addr']['uri'], ' '.join(
        [video_info['author']['nickname'], video_info['desc'], str(video_info['create_time'])])


# download
def download_video(uri: str, file_path: bytes):
    log.info('开始下载')
    url = f'https://www.iesdouyin.com/aweme/v1/play/?ratio=1080p&line=0&video_id={uri}'
    rsp = requests.get(url, headers=headers, stream=True)
    video_size = rsp.headers['content-length']
    block_size = 4048
    with open(file_path, 'wb') as file:
        for count, block in enumerate(rsp.iter_content(block_size), 1):
            # render web page progress bar
            eel.progressBar(video_size, block_size*count)
            file.write(block)
    log.info('保存成功')


def token_to_video_id(link: str) -> str:
    url = re.findall(r'https:.*/', link)[0]
    rsp = requests.get(url, headers=headers, allow_redirects=False)
    return re.findall(r'(https://.*)\?', rsp.text)[0]


# handler link
def handle_link(link: str) -> str:
    """
    :param link:
    :return: video id
    """
    # link 1  听......住车 # 环绕音乐 # 戴上耳机 # 动耳音乐  https://v.xxxx.com/iLWxxxxxxxgn/ 复制此链接，打开x音搜索，直接观看视频！
    # link 2  https://www.douyin.com/video/10xxxxxxxxxxxx
    # simple judgement
    if '复制此链接' in link:
        log.info('将口令转成url')
        link = token_to_video_id(link)
    return re.findall(r'\d+', link)[0]


def entry(link: str, path=''):
    log.info('开始运行')
    # long link to short link
    video_id = handle_link(link)
    # get file uri
    video_uri, file_name = get_uri(video_id)
    # write page
    eel.write_file_name(file_name)
    # file name
    file_path = os.path.join(path or TISH_PATH, file_name + '.mp4')
    # save video
    download_video(video_uri, file_path)
