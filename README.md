# 微博爬虫工具

一个用于爬取微博用户发布的微博内容并保存到本地的爬虫工具，支持cookie传入，可提高爬取成功率。

## 功能特点

- 爬取用户基本信息（用户名、粉丝数、关注数等）
- 爬取用户发布的微博内容
- 支持自定义爬取页数
- 支持保存为CSV和JSON格式
- 支持下载微博中的图片（优化了图片下载功能，支持获取原图）
- 支持传入自定义cookie提高爬取成功率

## 安装依赖

```bash
pip install -r requirements.txt
```

## 使用方法

### 基本使用

最简单的使用方式是指定用户ID进行爬取：

```bash
python main.py -u 用户ID
```

例如：

```bash
python main.py -u 1004524612 
```

### 高级用法

#### 使用cookie提高爬取成功率

```bash
python main.py -u 用户ID -c "你的cookie字符串"
```

#### 自定义爬取页数

```bash
python main.py -u 用户ID -p 20
```

#### 指定输出目录

```bash
python main.py -u 用户ID -o ./my_weibo_data
```

#### 自定义保存格式

```bash
# 只保存CSV格式
python main.py -u 用户ID --format csv

# 只保存JSON格式
python main.py -u 用户ID --format json
```

#### 下载微博图片

```bash
python main.py -u 用户ID --download_images
```

完整示例（包含所有选项）：

```bash
python main.py -u 1004524612 -p 5 -o ./weibo_data --download_images --format json -c "你的cookie字符串"
```

### 所有参数说明

```
-u, --user_id         要爬取的用户ID (必需)
-p, --pages           要爬取的微博页数，默认为10页
-c, --cookie          微博cookie字符串，可以提高爬取成功率
-o, --output          输出目录，默认为当前目录下的output
--download_images     是否下载微博图片
--format              数据保存格式，支持csv、json或both，默认为both
```

## 如何获取cookie

1. 登录微博网页版 (https://weibo.com)
2. 打开浏览器开发者工具 (F12)
3. 在开发者工具中选择"Network"标签
4. 刷新网页
5. 在请求列表中找到任意一个请求，点击查看详情
6. 在请求头中找到"Cookie"字段，复制其值

## 图片下载说明

- 爬虫会自动将微博中的缩略图转换为原图下载
- 下载的图片会按照微博ID组织在指定的输出目录下
- 默认会自动重试下载失败的图片（最多3次）
- 图片会以数字序号命名（如 1.jpg, 2.png 等）

## 注意事项

- 请合理设置爬取间隔和频率，避免被封IP
- 爬取结果仅供个人学习研究使用，请勿用于商业用途
- 尊重微博用户隐私，不要过度爬取或分享他人信息
- 如果遇到图片下载问题，可以尝试提供cookie进行爬取 