import requests
import json
import re
import time
import os
import pandas as pd
from lxml import etree
from tqdm import tqdm
from config import (
    DEFAULT_HEADERS, 
    API_URLS, 
    CONTAINER_ID_PREFIX, 
    REQUEST_DELAY, 
    WEIBO_CARD_TYPE,
    IMAGE_DOWNLOAD,
    DEBUG
)


class WeiboSpider:
    def __init__(self, cookie=None):
        """
        初始化微博爬虫
        :param cookie: 用户cookie字符串
        """
        self.headers = DEFAULT_HEADERS.copy()
        
        if cookie:
            self.headers['Cookie'] = cookie
        
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    def get_user_info(self, user_id):
        """
        获取用户基本信息
        :param user_id: 用户ID
        :return: 用户信息字典
        """
        url = API_URLS['user_info'].format(user_id)
        try:
            response = self.session.get(url)
            if response.status_code == 200:
                data = response.json()
                if data['ok'] == 1:
                    user_info = data['data']['userInfo']
                    info = {
                        'id': user_info['id'],
                        'screen_name': user_info['screen_name'],
                        'followers_count': user_info['followers_count'],
                        'follow_count': user_info['follow_count'],
                        'statuses_count': user_info['statuses_count'],
                        'description': user_info['description'],
                        'profile_url': user_info['profile_url']
                    }
                    return info
            return None
        except Exception as e:
            print(f"获取用户信息出错: {e}")
            return None
    
    def get_user_weibos(self, user_id, pages=10):
        """
        获取用户的微博列表
        :param user_id: 用户ID
        :param pages: 要爬取的页数
        :return: 微博列表
        """
        weibos = []
        container_id = f"{CONTAINER_ID_PREFIX}{user_id}"
        
        for page in tqdm(range(1, pages + 1), desc="爬取微博页数"):
            url = API_URLS['user_weibo'].format(user_id, container_id, page)
            try:
                response = self.session.get(url)
                time.sleep(REQUEST_DELAY)  # 避免请求过快
                
                if response.status_code == 200:
                    data = response.json()
                    if data['ok'] == 1 and 'cards' in data['data']:
                        cards = data['data']['cards']
                        for card in cards:
                            if card['card_type'] == WEIBO_CARD_TYPE:  # 微博卡片类型
                                mblog = card['mblog']
                                # 提取微博内容，去除HTML标签
                                text = re.sub(r'<[^>]+>', '', mblog['text'])
                                
                                weibo = {
                                    'id': mblog['id'],
                                    'text': text,
                                    'created_at': mblog['created_at'],
                                    'reposts_count': mblog['reposts_count'],
                                    'comments_count': mblog['comments_count'],
                                    'attitudes_count': mblog['attitudes_count'],
                                    'source': mblog['source']
                                }
                                
                                # 如果有图片，提取图片链接
                                if 'pics' in mblog:
                                    weibo['pics'] = []
                                    for pic in mblog['pics']:
                                        # 获取大图链接，而不是缩略图
                                        # 微博图片URL模式处理: 尝试获取大图
                                        pic_url = pic['url']
                                        # 替换可能的不同尺寸标识为large
                                        large_pic_url = self._get_large_image_url(pic_url)
                                        weibo['pics'].append(large_pic_url)
                                else:
                                    weibo['pics'] = []
                                
                                weibos.append(weibo)
                    else:
                        if DEBUG:
                            print(f"第{page}页没有数据或格式不正确")
                        break
                else:
                    print(f"请求失败，状态码: {response.status_code}")
                    break
            except Exception as e:
                print(f"爬取第{page}页微博出错: {e}")
                continue
                
        return weibos
    
    def _get_large_image_url(self, url):
        """
        将微博图片URL转换为大图URL
        """
        # 常见的微博图片尺寸标识
        size_patterns = [
            '/orj360/', '/orj480/', '/orj960/', '/orj1080/',  # 自适应尺寸
            '/thumb150/', '/thumb180/', '/thumb300/', '/thumb600/', '/thumb720/',  # 缩略图
            '/mw690/', '/mw1024/', '/mw2048/'  # 中等尺寸
        ]
        
        # 替换为large大图
        result_url = url
        for pattern in size_patterns:
            if pattern in url:
                result_url = url.replace(pattern, '/large/')
                break
        
        return result_url
    
    def save_to_csv(self, weibos, filename):
        """
        将微博数据保存为CSV文件
        :param weibos: 微博列表
        :param filename: 文件名
        """
        if not weibos:
            print("没有微博数据可保存")
            return
        
        df = pd.DataFrame(weibos)
        # 处理pics列表，转换为字符串
        if 'pics' in df.columns:
            df['pics'] = df['pics'].apply(lambda x: '|'.join(x) if x else '')
        
        df.to_csv(filename, index=False, encoding='utf-8-sig')
        print(f"微博数据已保存至 {filename}")
    
    def save_to_json(self, weibos, filename):
        """
        将微博数据保存为JSON文件
        :param weibos: 微博列表
        :param filename: 文件名
        """
        if not weibos:
            print("没有微博数据可保存")
            return
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(weibos, f, ensure_ascii=False, indent=4)
        
        print(f"微博数据已保存至 {filename}")
    
    def download_images(self, weibos, save_dir):
        """
        下载微博中的图片
        :param weibos: 微博列表
        :param save_dir: 保存目录
        """
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        
        img_count = 0
        error_count = 0
        
        for weibo in tqdm(weibos, desc="下载图片"):
            if 'pics' in weibo and weibo['pics']:
                weibo_id = weibo['id']
                weibo_dir = os.path.join(save_dir, weibo_id)
                if not os.path.exists(weibo_dir):
                    os.makedirs(weibo_dir)
                
                for i, pic_url in enumerate(weibo['pics']):
                    try:
                        # 添加重试机制
                        max_retries = IMAGE_DOWNLOAD['max_retries']
                        for retry in range(max_retries):
                            try:
                                response = self.session.get(
                                    pic_url,
                                    stream=True,
                                    timeout=IMAGE_DOWNLOAD['timeout']
                                )
                                
                                if response.status_code == 200:
                                    # 获取正确的文件扩展名
                                    file_ext = self._get_file_extension(pic_url, response.headers.get('Content-Type'))
                                    file_name = f"{i+1}{file_ext}"
                                    file_path = os.path.join(weibo_dir, file_name)
                                    
                                    with open(file_path, 'wb') as f:
                                        for chunk in response.iter_content(chunk_size=1024):
                                            if chunk:
                                                f.write(chunk)
                                    
                                    # 检查文件是否为空或过小（可能是错误的图片）
                                    file_size = os.path.getsize(file_path)
                                    if file_size < 1024:  # 小于1KB可能是无效图片
                                        if DEBUG:
                                            print(f"警告: 文件过小 ({file_size} 字节): {file_path}")
                                    
                                    img_count += 1
                                    # 成功下载，跳出重试循环
                                    break
                                else:
                                    print(f"下载图片失败，状态码: {response.status_code}，URL: {pic_url}")
                                    if retry < max_retries - 1:
                                        time.sleep(1)  # 失败后等待1秒再重试
                            except requests.exceptions.RequestException as e:
                                if retry < max_retries - 1:
                                    print(f"下载图片出错，重试 {retry+1}/{max_retries}: {e}")
                                    time.sleep(1)
                                else:
                                    raise
                    except Exception as e:
                        print(f"下载图片最终失败: {e}, URL: {pic_url}")
                        error_count += 1
                        continue
                    
                    # 下载间隔，避免请求过快
                    time.sleep(IMAGE_DOWNLOAD['delay'])
        
        print(f"共下载 {img_count} 张图片，失败 {error_count} 张")
    
    def _get_file_extension(self, url, content_type=None):
        """
        根据URL或内容类型获取文件扩展名
        """
        # 首先尝试从URL获取扩展名
        if url:
            path = url.split('?')[0]  # 移除URL参数
            if '.' in path:
                ext = os.path.splitext(path)[1].lower()
                if ext in IMAGE_DOWNLOAD['supported_exts']:
                    return ext
        
        # 如果URL中没有有效扩展名，则尝试从Content-Type获取
        if content_type:
            if 'jpeg' in content_type or 'jpg' in content_type:
                return '.jpg'
            elif 'png' in content_type:
                return '.png'
            elif 'gif' in content_type:
                return '.gif'
            elif 'webp' in content_type:
                return '.webp'
        
        # 默认返回.jpg
        return '.jpg' 