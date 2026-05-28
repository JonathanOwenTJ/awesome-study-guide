#!/usr/bin/env python3
"""
网站连通性检测脚本
批量检查 README.md 中的链接是否可访问
"""

import re
import sys
import time
import urllib.request
import urllib.error
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

import sys
import io

# 设置 stdout 编码为 utf-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 配置文件
README_FILE = "README.md"
TIMEOUT = 10  # 请求超时时间（秒）
MAX_WORKERS = 10  # 并发线程数


def extract_urls(readme_path):
    """从 README.md 中提取所有 URL"""
    urls = []
    with open(readme_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 匹配 Markdown 链接 [text](url)
    pattern = r'\[([^\]]+)\]\((https?://[^\)]+)\)'
    matches = re.findall(pattern, content)

    for text, url in matches:
        # 清理 URL，去除可能的尾随字符
        url = url.strip().rstrip(')')
        urls.append((text, url))

    return urls


def check_url(text, url):
    """检查单个 URL 是否可访问"""
    try:
        req = urllib.request.Request(
            url,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
        )

        with urllib.request.urlopen(req, timeout=TIMEOUT) as response:
            status = response.getcode()
            return {
                'text': text,
                'url': url,
                'status': status,
                'ok': 200 <= status < 400,
                'error': None
            }

    except urllib.error.HTTPError as e:
        return {
            'text': text,
            'url': url,
            'status': e.code,
            'ok': False,
            'error': f'HTTP {e.code}'
        }
    except urllib.error.URLError as e:
        return {
            'text': text,
            'url': url,
            'status': None,
            'ok': False,
            'error': str(e.reason)
        }
    except Exception as e:
        return {
            'text': text,
            'url': url,
            'status': None,
            'ok': False,
            'error': str(e)
        }


def main():
    print(f"[检测] 网站连通性检测")
    print(f"[时间] 开始: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"[配置] 文件: {README_FILE}, 线程: {MAX_WORKERS}, 超时: {TIMEOUT}秒\n")

    # 提取 URL
    urls = extract_urls(README_FILE)
    if not urls:
        print("[错误] 未找到任何链接")
        sys.exit(1)

    print(f"[信息] 发现 {len(urls)} 个链接\n")

    # 并发检测
    results = []
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_url = {
            executor.submit(check_url, text, url): (text, url)
            for text, url in urls
        }

        for future in as_completed(future_to_url):
            result = future.result()
            results.append(result)

            status_icon = "[OK]" if result['ok'] else "[FAIL]"
            status_text = f"[{result['status']}]" if result['status'] else "[失败]"
            print(f"{status_icon} {status_text} {result['text'][:30]:<30} | {result['url'][:50]}")

    # 统计结果
    total = len(results)
    ok_count = sum(1 for r in results if r['ok'])
    failed_count = total - ok_count

    print(f"\n{'='*60}")
    print(f"[统计] 检测结果")
    print(f"{'='*60}")
    print(f"[正常] {ok_count}/{total}")
    print(f"[失败] {failed_count}/{total}")

    if failed_count > 0:
        print(f"\n[警告] 以下链接访问异常:")
        print(f"{'-'*60}")
        for r in results:
            if not r['ok']:
                error_msg = r['error'] if r['error'] else 'Unknown error'
                print(f"[FAIL] [{error_msg}] {r['text']}")
                print(f"       → {r['url']}\n")

    print(f"\n[时间] 结束: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # 返回退出码，供 CI/CD 使用
    sys.exit(0 if failed_count == 0 else 1)


if __name__ == '__main__':
    main()
