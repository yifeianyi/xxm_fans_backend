#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
核心爬虫模块
爬取 B站视频数据并保存
"""

import json
import os
import sys
import time
import random
import signal
import socket
from datetime import datetime
from typing import List, Dict, Any, Optional
from contextlib import contextmanager

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xxm_fans_home.settings')

import django
django.setup()

from tools.bilibili import BilibiliAPIClient, BilibiliAPIError
from .utils.logger import setup_views_logger, get_project_root

logger = setup_views_logger("crawl_views")

PROJECT_ROOT = get_project_root()
VIEWS_FILE = os.path.join(PROJECT_ROOT, "data", "spider", "views.json")
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "data", "spider", "views")


class TimeoutError(Exception):
    """自定义超时异常"""
    pass


@contextmanager
def time_limit(seconds: int, desc: str = "操作"):
    """上下文管理器：限制代码块执行时间"""
    def signal_handler(signum, frame):
        raise TimeoutError(f"{desc}超时（{seconds}秒）")

    # 设置信号处理器
    old_handler = signal.signal(signal.SIGALRM, signal_handler)
    signal.alarm(seconds)
    
    try:
        yield
    finally:
        signal.alarm(0)  # 取消闹钟
        signal.signal(signal.SIGALRM, old_handler)


class RobustBilibiliAPIClient(BilibiliAPIClient):
    """强化版B站API客户端，增强超时和异常处理"""
    
    def __init__(self, timeout: int = 8, retry_times: int = 2, retry_delay: int = 1):
        # 使用更短的超时，快速失败
        super().__init__(timeout=timeout, retry_times=retry_times, retry_delay=retry_delay)
        # 设置socket全局超时
        socket.setdefaulttimeout(timeout + 2)
    
    def get_video_info_with_timeout(self, bvid: str, max_wait: int = 15) -> Any:
        """
        带强制超时的视频信息获取
        
        Args:
            bvid: BV号
            max_wait: 最大等待时间（秒）
        
        Returns:
            VideoInfo对象或None
        """
        import requests
        
        url = f"{self.BASE_URL}/x/web-interface/view"
        params = {"bvid": bvid}
        
        for attempt in range(self.retry_times):
            start_time = time.time()
            try:
                logger.debug(f"[{bvid}] 第{attempt+1}次尝试请求...")
                
                # 使用更细粒度的超时：连接3秒，读取5秒
                response = requests.get(
                    url,
                    params=params,
                    headers=self.headers,
                    timeout=(3, 5),  # (连接超时, 读取超时)
                )
                
                elapsed = time.time() - start_time
                logger.debug(f"[{bvid}] 请求完成，耗时{elapsed:.2f}秒")
                
                response.raise_for_status()
                data = response.json()
                
                if data.get("code") != 0:
                    error_msg = data.get("message", "未知错误")
                    if attempt == self.retry_times - 1:
                        raise BilibiliAPIError(error_msg, data.get("code"))
                    logger.warning(f"[{bvid}] API返回错误: {error_msg}，准备重试")
                    time.sleep(self.retry_delay)
                    continue
                
                return data["data"]
                
            except requests.exceptions.ConnectTimeout:
                elapsed = time.time() - start_time
                logger.error(f"[{bvid}] 连接超时（{elapsed:.2f}秒）")
                if attempt == self.retry_times - 1:
                    raise BilibiliAPIError(f"连接超时，无法连接到B站服务器")
                time.sleep(self.retry_delay)
                
            except requests.exceptions.ReadTimeout:
                elapsed = time.time() - start_time
                logger.error(f"[{bvid}] 读取超时（{elapsed:.2f}秒）")
                if attempt == self.retry_times - 1:
                    raise BilibiliAPIError(f"读取超时，服务器响应过慢")
                time.sleep(self.retry_delay)
                
            except requests.exceptions.Timeout:
                elapsed = time.time() - start_time
                logger.error(f"[{bvid}] 请求超时（{elapsed:.2f}秒）")
                if attempt == self.retry_times - 1:
                    raise BilibiliAPIError(f"请求超时（{self.timeout}秒）")
                time.sleep(self.retry_delay)
                
            except requests.exceptions.ConnectionError as e:
                elapsed = time.time() - start_time
                logger.error(f"[{bvid}] 连接错误（{elapsed:.2f}秒）: {e}")
                if attempt == self.retry_times - 1:
                    raise BilibiliAPIError(f"连接错误: {str(e)}")
                time.sleep(self.retry_delay)
                
            except Exception as e:
                elapsed = time.time() - start_time
                logger.error(f"[{bvid}] 请求异常（{elapsed:.2f}秒）: {e}")
                if attempt == self.retry_times - 1:
                    raise BilibiliAPIError(f"请求失败: {str(e)}")
                time.sleep(self.retry_delay)
        
        raise BilibiliAPIError("达到最大重试次数")


class ViewsCrawler:
    """B站投稿数据爬虫"""

    def __init__(self, request_delay_min: float = 1.0, request_delay_max: float = 3.0, max_retries: int = 2):
        self.request_delay_min = request_delay_min
        self.request_delay_max = request_delay_max
        self.max_retries = max_retries
        # 使用强化版客户端
        self.api_client = RobustBilibiliAPIClient(
            timeout=8,  # 减少超时时间，快速失败
            retry_times=max_retries,
            retry_delay=1
        )
        self.session_id = f"crawl_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        self.results = []
        self.errors = []
        self.skipped_bvids = set()  # 记录跳过的BV号

    def load_views(self) -> List[Dict[str, Any]]:
        """加载 views.json，按BV号去重（保留第一个）"""
        if not os.path.exists(VIEWS_FILE):
            raise FileNotFoundError(f"找不到 {VIEWS_FILE}，请先执行导出")

        with open(VIEWS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # 先过滤有效作品
        valid_works = [w for w in data.get('works', []) if w.get('is_valid', True)]
        
        # 按BV号去重，保留第一个
        seen_bvids = set()
        unique_works = []
        
        for work in valid_works:
            work_id = work.get('work_id', '')
            # 统一BV号格式（添加BV前缀）
            bvid = work_id if work_id.startswith('BV') else f"BV{work_id}"
            
            if bvid not in seen_bvids:
                seen_bvids.add(bvid)
                unique_works.append(work)
            else:
                logger.debug(f"跳过重复BV号: {bvid} - {work.get('title', 'Unknown')[:30]}...")
        
        duplicate_count = len(valid_works) - len(unique_works)
        if duplicate_count > 0:
            logger.info(f"从 views.json 加载了 {len(valid_works)} 个有效作品，去重后 {len(unique_works)} 个（跳过 {duplicate_count} 个重复）")
        else:
            logger.info(f"从 views.json 加载了 {len(unique_works)} 个有效作品")
        
        return unique_works

    def crawl_video(self, work: Dict[str, Any], index: int, total: int) -> Optional[Dict[str, Any]]:
        """爬取单个视频数据"""
        work_id = work['work_id']
        platform = work.get('platform', 'bilibili')
        title = work.get('title', 'Unknown')
        
        # 统一BV号格式
        bvid = work_id if work_id.startswith('BV') else f"BV{work_id}"

        # 只处理B站视频
        if platform.lower() not in ['bilibili', '哔哩哔哩']:
            logger.info(f"[{index}/{total}] 跳过非B站作品: {work_id} (平台: {platform})")
            return None
        
        # 检查是否已经跳过（避免重复处理）
        if bvid in self.skipped_bvids:
            logger.debug(f"[{index}/{total}] 跳过已处理的BV号: {bvid}")
            return None

        logger.info(f"[{index}/{total}] 开始爬取: {bvid} - {title[:50]}...")
        
        start_time = time.time()
        
        try:
            # 使用带超时的API调用
            video_data = self.api_client.get_video_info_with_timeout(bvid, max_wait=20)
            
            elapsed = time.time() - start_time
            
            if video_data is None:
                logger.error(f"[{index}/{total}] ✗ 失败: {bvid} - 返回数据为空（耗时{elapsed:.2f}秒）")
                self.errors.append({
                    "work_id": work_id,
                    "title": title,
                    "error": "返回数据为空",
                    "status": "failed"
                })
                return None
            
            # 手动构建结果（避免原始VideoInfo的解析问题）
            result = {
                "platform": platform,
                "work_id": work_id,
                "title": video_data.get('title', title),
                "crawl_time": datetime.now().isoformat(),
                "view_count": video_data.get('stat', {}).get('view', 0),
                "danmaku_count": video_data.get('stat', {}).get('danmaku', 0),
                "comment_count": video_data.get('stat', {}).get('reply', 0),
                "like_count": video_data.get('stat', {}).get('like', 0),
                "coin_count": video_data.get('stat', {}).get('coin', 0),
                "favorite_count": video_data.get('stat', {}).get('favorite', 0),
                "share_count": video_data.get('stat', {}).get('share', 0),
                "status": "success"
            }

            logger.info(f"[{index}/{total}] ✓ 成功: {bvid} 播放量={result['view_count']:,}（耗时{elapsed:.2f}秒）")
            return result

        except TimeoutError as e:
            elapsed = time.time() - start_time
            error_msg = f"强制超时（{elapsed:.2f}秒）"
            logger.error(f"[{index}/{total}] ✗ 失败: {bvid} - {error_msg}")
            self.errors.append({
                "work_id": work_id,
                "title": title,
                "error": str(e),
                "status": "failed"
            })
            return None
            
        except BilibiliAPIError as e:
            elapsed = time.time() - start_time
            error_msg = f"API错误[{e.code}]: {e.message}"
            logger.error(f"[{index}/{total}] ✗ 失败: {bvid} - {error_msg}（耗时{elapsed:.2f}秒）")
            self.errors.append({
                "work_id": work_id,
                "title": title,
                "error": error_msg,
                "status": "failed"
            })
            return None
            
        except Exception as e:
            elapsed = time.time() - start_time
            error_msg = f"异常: {str(e)}"
            logger.error(f"[{index}/{total}] ✗ 失败: {bvid} - {error_msg}（耗时{elapsed:.2f}秒）")
            self.errors.append({
                "work_id": work_id,
                "title": title,
                "error": error_msg,
                "status": "failed"
            })
            return None

    def crawl(self) -> str:
        """执行爬取任务"""
        start_time = datetime.now()
        works = self.load_views()

        total = len(works)
        success = 0
        failed = 0
        skipped = 0

        logger.info("=" * 60)
        logger.info(f"开始爬取任务: {self.session_id}")
        logger.info(f"总计: {total} 个作品")
        logger.info(f"请求间隔: {self.request_delay_min}s - {self.request_delay_max}s (随机)")
        logger.info(f"单次请求超时: 8秒 | 连接超时: 3秒 | 读取超时: 5秒")
        logger.info("=" * 60)

        for i, work in enumerate(works, 1):
            result = self.crawl_video(work, i, total)
            
            if result:
                self.results.append(result)
                success += 1
            elif result is None and work.get('platform', '').lower() in ['bilibili', '哔哩哔哩']:
                # None 且是B站作品表示失败
                failed += 1
            else:
                # None 且非B站作品表示跳过
                skipped += 1

            # 计算进度百分比
            progress = (i / total) * 100
            elapsed_total = (datetime.now() - start_time).total_seconds()
            eta = (elapsed_total / i) * (total - i) if i > 0 else 0
            logger.info(f"进度: {i}/{total} ({progress:.1f}%) | 成功: {success} | 失败: {failed} | 跳过: {skipped} | 预计剩余: {eta/60:.1f}分钟")

            # 不是最后一个，则等待随机间隔
            if i < total:
                delay = random.uniform(self.request_delay_min, self.request_delay_max)
                logger.debug(f"等待 {delay:.3f} 秒后继续...")
                time.sleep(delay)

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        # 构建输出数据
        output_data = {
            "session_id": self.session_id,
            "crawl_time": start_time.isoformat(),
            "crawl_hour": start_time.strftime('%H'),
            "total_count": total,
            "success_count": success,
            "fail_count": failed,
            "skip_count": skipped,
            "duration_seconds": duration,
            "data": self.results,
            "errors": self.errors
        }

        output_path = self._save_output(output_data, start_time)

        logger.info("=" * 60)
        logger.info(f"爬取完成!")
        logger.info(f"总计: {total} | 成功: {success} | 失败: {failed} | 跳过: {skipped}")
        logger.info(f"耗时: {duration:.1f} 秒 ({duration/60:.1f} 分钟)")
        logger.info(f"结果已保存到: {output_path}")
        logger.info("=" * 60)

        return output_path

    def _save_output(self, data: Dict[str, Any], dt: datetime) -> str:
        """保存输出到文件（含小时）"""
        year = dt.strftime('%Y')
        month = dt.strftime('%m')
        day = dt.strftime('%d')
        hour = dt.strftime('%H')
        date_str = dt.strftime('%Y-%m-%d')

        output_dir = os.path.join(OUTPUT_DIR, year, month, day)
        os.makedirs(output_dir, exist_ok=True)

        # 文件名包含小时
        output_file = os.path.join(output_dir, f"{date_str}-{hour}_views_data.json")

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        return output_file


def main():
    crawler = ViewsCrawler(request_delay_min=1.0, request_delay_max=3.0, max_retries=2)
    try:
        output_path = crawler.crawl()
        print(f"\n爬取完成，结果保存到: {output_path}")
        sys.exit(0)
    except KeyboardInterrupt:
        logger.warning("用户中断爬取任务")
        sys.exit(130)
    except Exception as e:
        logger.error(f"爬取任务失败: {e}")
        import traceback
        logger.error(traceback.format_exc())
        sys.exit(1)


if __name__ == '__main__':
    main()
