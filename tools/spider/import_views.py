#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据导入模块
将爬取结果导入到 SQLite 数据库
支持自动查找最新数据文件
"""

import json
import os
import sqlite3
import sys
import glob
from datetime import datetime
from typing import Dict, Any, Optional, List, Tuple
from pathlib import Path

# 处理导入路径
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.join(current_dir, '..', '..')
sys.path.insert(0, os.path.abspath(backend_dir))

# 尝试相对导入，如果失败则使用绝对导入
try:
    from .utils.logger import setup_views_logger, get_project_root
except ImportError:
    from tools.spider.utils.logger import setup_views_logger, get_project_root

logger = setup_views_logger("import_views")

PROJECT_ROOT = get_project_root()
SQLITE_DB = os.path.join(PROJECT_ROOT, "data", "view_data.sqlite3")
VIEWS_DIR = os.path.join(PROJECT_ROOT, "data", "spider", "views")


class ViewsImporter:
    """数据导入器"""

    def __init__(self):
        self.conn = None
        self.cursor = None

    def connect(self):
        """连接数据库"""
        os.makedirs(os.path.dirname(SQLITE_DB), exist_ok=True)
        self.conn = sqlite3.connect(SQLITE_DB)
        self.cursor = self.conn.cursor()
        self._init_tables()

    def close(self):
        """关闭连接"""
        if self.conn:
            self.conn.close()

    def _init_tables(self):
        """初始化数据表"""
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS data_analytics_workmetricsspider (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                platform TEXT NOT NULL,
                work_id TEXT NOT NULL,
                title TEXT,
                crawl_date TEXT NOT NULL,
                crawl_hour TEXT NOT NULL,
                crawl_time TEXT NOT NULL,
                view_count INTEGER DEFAULT 0,
                danmaku_count INTEGER DEFAULT 0,
                comment_count INTEGER DEFAULT 0,
                like_count INTEGER DEFAULT 0,
                coin_count INTEGER DEFAULT 0,
                favorite_count INTEGER DEFAULT 0,
                share_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(platform, work_id, crawl_date, crawl_hour)
            )
        """)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS data_analytics_crawlsessionspider (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT UNIQUE NOT NULL,
                crawl_date TEXT NOT NULL,
                crawl_hour TEXT NOT NULL,
                start_time TEXT,
                end_time TEXT,
                total_count INTEGER DEFAULT 0,
                success_count INTEGER DEFAULT 0,
                fail_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 创建索引
        self.cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_work_metrics_platform_work_id
            ON data_analytics_workmetricsspider(platform, work_id)
        """)
        self.cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_work_metrics_crawl_date
            ON data_analytics_workmetricsspider(crawl_date)
        """)
        self.cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_work_metrics_crawl_hour
            ON data_analytics_workmetricsspider(crawl_date, crawl_hour)
        """)
        self.cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_crawl_sessions_date
            ON data_analytics_crawlsessionspider(crawl_date)
        """)
        self.cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_crawl_sessions_hour
            ON data_analytics_crawlsessionspider(crawl_date, crawl_hour)
        """)

        self.conn.commit()
        logger.info("数据库表初始化完成")

    def find_latest_data_file(self) -> Optional[Tuple[str, str, str]]:
        """
        自动查找最新的数据文件
        
        Returns:
            (文件路径, 日期字符串, 小时字符串) 或 None
        """
        if not os.path.exists(VIEWS_DIR):
            logger.error(f"数据目录不存在: {VIEWS_DIR}")
            return None

        # 扫描所有数据文件
        # 路径格式: data/spider/views/YYYY/MM/DD/YYYY-MM-DD-HH_views_data.json
        pattern = os.path.join(VIEWS_DIR, "*/*/*/*_views_data.json")
        data_files = glob.glob(pattern)
        
        if not data_files:
            logger.error(f"未找到任何数据文件，路径: {pattern}")
            return None
        
        # 按修改时间排序，获取最新文件
        latest_file = max(data_files, key=os.path.getmtime)
        
        # 从文件名解析日期和小时
        # 文件名格式: YYYY-MM-DD-HH_views_data.json
        filename = os.path.basename(latest_file)
        parts = filename.replace("_views_data.json", "").split("-")
        
        if len(parts) >= 4:
            year, month, day, hour = parts[0], parts[1], parts[2], parts[3]
            date_str = f"{year}-{month}-{day}"
            hour_str = hour
            logger.info(f"找到最新数据文件: {latest_file} (日期: {date_str}, 小时: {hour_str})")
            return latest_file, date_str, hour_str
        else:
            logger.error(f"无法解析文件名: {filename}")
            return None

    def list_available_files(self, limit: int = 10) -> List[Tuple[str, str, str, float]]:
        """
        列出可用的数据文件（按时间倒序）
        
        Args:
            limit: 返回的最大文件数量
            
        Returns:
            [(文件路径, 日期, 小时, 修改时间), ...]
        """
        if not os.path.exists(VIEWS_DIR):
            return []
        
        pattern = os.path.join(VIEWS_DIR, "*/*/*/*_views_data.json")
        data_files = glob.glob(pattern)
        
        files_with_mtime = []
        for file_path in data_files:
            filename = os.path.basename(file_path)
            parts = filename.replace("_views_data.json", "").split("-")
            if len(parts) >= 4:
                year, month, day, hour = parts[0], parts[1], parts[2], parts[3]
                date_str = f"{year}-{month}-{day}"
                hour_str = hour
                mtime = os.path.getmtime(file_path)
                files_with_mtime.append((file_path, date_str, hour_str, mtime))
        
        # 按修改时间倒序排序
        files_with_mtime.sort(key=lambda x: x[3], reverse=True)
        return files_with_mtime[:limit]

    def load_crawl_data(self, date_str: Optional[str] = None,
                        hour_str: Optional[str] = None,
                        auto_find: bool = True) -> Optional[Dict[str, Any]]:
        """
        加载爬取数据
        
        Args:
            date_str: 指定日期 (YYYY-MM-DD)
            hour_str: 指定小时 (HH)
            auto_find: 是否自动查找最新文件（当 date_str/hour_str 未指定时）
        """
        # 如果未指定日期/小时，自动查找最新文件
        if (date_str is None or hour_str is None) and auto_find:
            result = self.find_latest_data_file()
            if result:
                file_path, date_str, hour_str = result
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                logger.info(f"自动加载最新数据文件: {file_path}")
                return data
            return None
        
        # 使用指定的日期和小时
        if date_str is None:
            date_str = datetime.now().strftime('%Y-%m-%d')
        if hour_str is None:
            hour_str = datetime.now().strftime('%H')

        year, month, day = date_str.split('-')
        data_file = os.path.join(
            VIEWS_DIR, year, month, day,
            f"{date_str}-{hour_str}_views_data.json"
        )

        if not os.path.exists(data_file):
            logger.error(f"找不到数据文件: {data_file}")
            return None

        with open(data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        logger.info(f"加载数据文件: {data_file}")
        return data

    def check_data_exists(self, crawl_date: str, crawl_hour: str, session_id: str = None) -> bool:
        """
        检查指定日期小时的数据是否已存在
        
        Args:
            crawl_date: 爬取日期 (YYYY-MM-DD)
            crawl_hour: 爬取小时 (HH)
            session_id: 会话ID（可选）
            
        Returns:
            True 如果数据已存在，False 否则
        """
        # 检查该日期小时是否已有数据
        self.cursor.execute("""
            SELECT COUNT(*) FROM data_analytics_workmetricsspider
            WHERE crawl_date = ? AND crawl_hour = ?
        """, (crawl_date, crawl_hour))
        
        count = self.cursor.fetchone()[0]
        
        if count > 0:
            return True
        
        # 也检查会话表
        self.cursor.execute("""
            SELECT COUNT(*) FROM data_analytics_crawlsessionspider
            WHERE crawl_date = ? AND crawl_hour = ?
        """, (crawl_date, crawl_hour))
        
        session_count = self.cursor.fetchone()[0]
        
        return session_count > 0

    def get_existing_stats(self, crawl_date: str, crawl_hour: str) -> Dict[str, Any]:
        """
        获取已存在数据的统计信息
        
        Returns:
            包含统计信息的字典
        """
        self.cursor.execute("""
            SELECT COUNT(*), SUM(view_count) FROM data_analytics_workmetricsspider
            WHERE crawl_date = ? AND crawl_hour = ?
        """, (crawl_date, crawl_hour))
        
        result = self.cursor.fetchone()
        
        self.cursor.execute("""
            SELECT session_id, total_count, success_count, created_at
            FROM data_analytics_crawlsessionspider
            WHERE crawl_date = ? AND crawl_hour = ?
            LIMIT 1
        """, (crawl_date, crawl_hour))
        
        session_result = self.cursor.fetchone()
        
        return {
            'work_count': result[0] or 0,
            'total_views': result[1] or 0,
            'session_id': session_result[0] if session_result else None,
            'total_count': session_result[1] if session_result else 0,
            'success_count': session_result[2] if session_result else 0,
            'created_at': session_result[3] if session_result else None,
        }

    def import_data(self, data: Dict[str, Any], force: bool = False) -> bool:
        """
        导入数据到数据库
        
        Args:
            data: 爬取数据字典
            force: 是否强制重新导入（即使数据已存在）
        """
        try:
            crawl_time = data.get('crawl_time', datetime.now().isoformat())
            crawl_date = crawl_time[:10]
            crawl_hour = data.get('crawl_hour', crawl_time[11:13] if len(crawl_time) > 13 else "00")
            crawl_time_str = crawl_time[11:19] if len(crawl_time) > 10 else "00:00:00"

            session_id = data.get('session_id', 'unknown')
            total_count = data.get('total_count', 0)
            success_count = data.get('success_count', 0)
            fail_count = data.get('fail_count', 0)

            # 检查数据是否已存在
            if not force and self.check_data_exists(crawl_date, crawl_hour, session_id):
                stats = self.get_existing_stats(crawl_date, crawl_hour)
                logger.warning(f"数据已存在: {crawl_date} {crawl_hour}:00")
                logger.warning(f"  - 已有作品记录: {stats['work_count']} 条")
                logger.warning(f"  - 总会话记录: {stats['total_count']} 条")
                logger.warning(f"  - 会话ID: {stats['session_id']}")
                if stats['created_at']:
                    logger.warning(f"  - 入库时间: {stats['created_at']}")
                logger.warning(f"如需强制重新导入，请使用 --force 参数")
                return True  # 返回 True 表示这不是错误，只是跳过了

            self.conn.execute("BEGIN TRANSACTION")

            # 插入会话记录
            self.cursor.execute("""
                INSERT OR REPLACE INTO data_analytics_crawlsessionspider
                (session_id, crawl_date, crawl_hour, start_time, end_time,
                 total_count, success_count, fail_count, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (
                session_id, crawl_date, crawl_hour, crawl_time_str,
                datetime.now().strftime('%H:%M:%S'),
                total_count, success_count, fail_count
            ))

            # 插入作品数据
            metrics_data = data.get('data', [])
            imported = 0

            for item in metrics_data:
                if item.get('status') != 'success':
                    continue

                self.cursor.execute("""
                    INSERT OR REPLACE INTO data_analytics_workmetricsspider
                    (platform, work_id, title, crawl_date, crawl_hour, crawl_time,
                     view_count, danmaku_count, comment_count, like_count,
                     coin_count, favorite_count, share_count, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                """, (
                    item.get('platform', 'bilibili'),
                    item.get('work_id'),
                    item.get('title'),
                    crawl_date,
                    crawl_hour,
                    crawl_time_str,
                    item.get('view_count', 0),
                    item.get('danmaku_count', 0),
                    item.get('comment_count', 0),
                    item.get('like_count', 0),
                    item.get('coin_count', 0),
                    item.get('favorite_count', 0),
                    item.get('share_count', 0)
                ))
                imported += 1

            self.conn.commit()
            logger.info(f"导入完成: 成功导入 {imported} 条作品记录，会话 {session_id}")
            return True

        except Exception as e:
            self.conn.rollback()
            logger.error(f"导入失败: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return False

    def import_by_date(self, date_str: Optional[str] = None,
                       hour_str: Optional[str] = None,
                       auto_find: bool = True,
                       force: bool = False) -> bool:
        """
        按日期导入数据
        
        Args:
            date_str: 指定日期 (YYYY-MM-DD)
            hour_str: 指定小时 (HH)
            auto_find: 是否自动查找最新文件
            force: 是否强制重新导入
        """
        data = self.load_crawl_data(date_str, hour_str, auto_find=auto_find)
        if not data:
            return False
        return self.import_data(data, force=force)

    def import_latest(self, force: bool = False) -> bool:
        """导入最新的数据文件（便捷方法）"""
        return self.import_by_date(auto_find=True, force=force)


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description='导入B站投稿数据到SQLite',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 自动查找并导入最新数据文件（默认行为）
  python import_views.py
  
  # 导入指定日期的数据
  python import_views.py --date 2026-02-06 --hour 14
  
  # 查看可用的数据文件
  python import_views.py --list
  
  # 强制重新导入（即使数据已存在）
  python import_views.py --force
        """
    )
    parser.add_argument('--date', type=str, help='指定日期 (YYYY-MM-DD)')
    parser.add_argument('--hour', type=str, help='指定小时 (HH)')
    parser.add_argument('--list', action='store_true', help='列出可用的数据文件')
    parser.add_argument('--force', action='store_true', help='强制重新导入（即使数据已存在）')
    args = parser.parse_args()

    importer = ViewsImporter()
    
    try:
        importer.connect()
        
        # 列出可用文件
        if args.list:
            files = importer.list_available_files(limit=20)
            if files:
                print("\n可用的数据文件（最近20个）：")
                print("-" * 80)
                print(f"{'序号':<6}{'日期':<12}{'小时':<8}{'文件名':<40}{'修改时间':<20}")
                print("-" * 80)
                for i, (file_path, date, hour, mtime) in enumerate(files, 1):
                    mtime_str = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')
                    filename = os.path.basename(file_path)
                    print(f"{i:<6}{date:<12}{hour:<8}{filename:<40}{mtime_str:<20}")
                print("-" * 80)
                print(f"\n共 {len(files)} 个文件")
                success = True
            else:
                print("未找到任何数据文件")
                success = False
            # 不在这里退出，让 finally 块关闭数据库连接
        
        # 导入数据（如果不是 --list 模式）
        if not args.list:
            if args.date or args.hour:
                # 指定了日期/小时，按指定导入
                success = importer.import_by_date(args.date, args.hour, auto_find=False, force=args.force)
            else:
                # 未指定，自动查找最新文件
                logger.info("未指定日期/小时，自动查找最新数据文件...")
                success = importer.import_latest(force=args.force)
        
        sys.exit(0 if success else 1)
        
    except Exception as e:
        logger.error(f"导入任务失败: {e}")
        import traceback
        logger.error(traceback.format_exc())
        sys.exit(1)
    finally:
        importer.close()


if __name__ == '__main__':
    main()
