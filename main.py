from weibo_spider import WeiboSpider
import argparse
import os
from config import DEFAULT_PAGES, OUTPUT_DIR, DATA_FORMATS


def parse_args():
    parser = argparse.ArgumentParser(description='微博爬虫工具')
    parser.add_argument('-u', '--user_id', type=str, required=True, help='要爬取的用户ID')
    parser.add_argument('-p', '--pages', type=int, default=DEFAULT_PAGES, help=f'要爬取的微博页数，默认为{DEFAULT_PAGES}页')
    parser.add_argument('-c', '--cookie', type=str, default='', help='微博cookie字符串，可以提高爬取成功率')
    parser.add_argument('-o', '--output', type=str, default=OUTPUT_DIR, help=f'输出目录，默认为{OUTPUT_DIR}')
    parser.add_argument('--download_images', action='store_true', help='是否下载微博图片')
    parser.add_argument('--format', type=str, choices=DATA_FORMATS, default='both', help='数据保存格式，支持csv、json或both，默认为both')
    
    return parser.parse_args()


def main():
    args = parse_args()
    
    # 确保输出目录存在
    if not os.path.exists(args.output):
        os.makedirs(args.output)
    
    # 初始化爬虫
    spider = WeiboSpider(cookie=args.cookie)
    
    # 获取用户信息
    user_info = spider.get_user_info(args.user_id)
    if user_info:
        print(f"\n用户信息:")
        print(f"用户名: {user_info['screen_name']}")
        print(f"粉丝数: {user_info['followers_count']}")
        print(f"关注数: {user_info['follow_count']}")
        print(f"微博数: {user_info['statuses_count']}")
        print(f"简介: {user_info['description']}\n")
    else:
        print("无法获取用户信息，请检查用户ID是否正确或尝试提供cookie")
        return
    
    # 获取用户微博
    print(f"开始爬取用户 {user_info['screen_name']} 的微博，共 {args.pages} 页")
    weibos = spider.get_user_weibos(args.user_id, pages=args.pages)
    print(f"共爬取到 {len(weibos)} 条微博\n")
    
    if weibos:
        # 保存微博数据
        if args.format in ['csv', 'both']:
            csv_filename = os.path.join(args.output, f"{args.user_id}_weibos.csv")
            spider.save_to_csv(weibos, csv_filename)
        
        if args.format in ['json', 'both']:
            json_filename = os.path.join(args.output, f"{args.user_id}_weibos.json")
            spider.save_to_json(weibos, json_filename)
        
        # 下载图片
        if args.download_images:
            images_dir = os.path.join(args.output, f"{args.user_id}_images")
            print(f"\n开始下载微博图片...")
            spider.download_images(weibos, images_dir)
    

if __name__ == "__main__":
    main() 