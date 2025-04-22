# 微博爬虫配置文件

# 默认请求头
DEFAULT_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
}

# API 接口
API_URLS = {
    'user_info': 'https://m.weibo.cn/api/container/getIndex?type=uid&value={}',
    'user_weibo': 'https://m.weibo.cn/api/container/getIndex?type=uid&value={}&containerid={}&page={}',
}

# 默认容器前缀
CONTAINER_ID_PREFIX = '107603'

# 每页微博条数
WEIBO_PER_PAGE = 10

# 请求间隔时间(秒)
REQUEST_DELAY = 1

# 输出文件目录
OUTPUT_DIR = './output'

# 数据保存格式
DATA_FORMATS = ['csv', 'json', 'both']

# 默认爬取页数
DEFAULT_PAGES = 10

# 微博卡片类型
WEIBO_CARD_TYPE = 9

# 图片下载设置
IMAGE_DOWNLOAD = {
    'timeout': 15,       # 图片下载超时时间(秒)
    'max_retries': 3,    # 下载失败时的最大重试次数
    'delay': 0.5,        # 每张图片下载后的等待时间(秒)
    'supported_exts': ['.jpg', '.jpeg', '.png', '.gif', '.webp'] # 支持的图片格式
}

# 调试模式
DEBUG = False 