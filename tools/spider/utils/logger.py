#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
日志工具模块
支持按日期分层存储日志文件，支持实时刷新
"""

import logging
import os
import sys
from datetime import datetime


def get_project_root() -> str:
    """获取项目根目录"""
    # 当前文件路径: repo/xxm_fans_backend/tools/spider/utils/logger.py
    # 项目根目录: 上溯5层
    current_file = os.path.abspath(__file__)
    for _ in range(5):
        current_file = os.path.dirname(current_file)
    return os.path.dirname(current_file)


# 默认日志目录（相对于项目根目录）
DEFAULT_LOG_DIR = os.path.join(get_project_root(), "logs", "spider")

# 爬虫专用日志目录
VIEWS_LOG_DIR = os.path.join(get_project_root(), "logs", "spider", "views")


class FlushableLogger:
    """
    可实时刷新的日志包装器
    每次记录日志后自动刷新到文件
    """
    
    def __init__(self, logger: logging.Logger):
        self._logger = logger
        self._file_handlers = [h for h in logger.handlers if isinstance(h, logging.FileHandler)]
    
    def _flush(self):
        """刷新文件处理器，确保日志写入磁盘"""
        for handler in self._file_handlers:
            handler.flush()
    
    def debug(self, msg, *args, **kwargs):
        self._logger.debug(msg, *args, **kwargs)
        self._flush()
    
    def info(self, msg, *args, **kwargs):
        self._logger.info(msg, *args, **kwargs)
        self._flush()
    
    def warning(self, msg, *args, **kwargs):
        self._logger.warning(msg, *args, **kwargs)
        self._flush()
    
    def error(self, msg, *args, **kwargs):
        self._logger.error(msg, *args, **kwargs)
        self._flush()
    
    def critical(self, msg, *args, **kwargs):
        self._logger.critical(msg, *args, **kwargs)
        self._flush()
    
    def flush(self):
        """手动刷新日志到文件"""
        self._flush()
    
    def __getattr__(self, name):
        """代理其他属性到原始 logger"""
        return getattr(self._logger, name)


def get_daily_log_dir(base_dir: str = None) -> str:
    """
    获取按日期分层的日志目录
    
    Args:
        base_dir: 基础日志目录，默认使用 VIEWS_LOG_DIR
        
    Returns:
        按日期分层的目录路径: {base_dir}/{year}/{month}
    """
    if base_dir is None:
        base_dir = VIEWS_LOG_DIR
    
    now = datetime.now()
    year = now.strftime("%Y")
    month = now.strftime("%m")
    
    log_dir = os.path.join(base_dir, year, month)
    return log_dir


def setup_logger(name: str, log_dir: str = None, use_daily_dir: bool = False, flushable: bool = False):
    """
    设置日志记录器
    
    Args:
        name: 日志记录器名称
        log_dir: 日志目录，默认为项目根目录下的 logs/spider
        use_daily_dir: 是否使用按日期分层的目录结构 (logs/spider/views/{year}/{month})
        flushable: 是否返回可实时刷新的日志包装器
    
    Returns:
        配置好的日志记录器 (FlushableLogger 或 logging.Logger)
    """
    if log_dir is None:
        if use_daily_dir:
            log_dir = get_daily_log_dir()
        else:
            log_dir = DEFAULT_LOG_DIR

    os.makedirs(log_dir, exist_ok=True)

    date_str = datetime.now().strftime("%Y%m%d")
    log_file = os.path.join(log_dir, f"{name}_{date_str}.log")

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # 避免重复添加处理器
    if logger.handlers:
        if flushable:
            return FlushableLogger(logger)
        return logger

    # 文件处理器
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.INFO)

    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    # 格式
    formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)-8s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    if flushable:
        return FlushableLogger(logger)
    return logger


def setup_views_logger(name: str, flushable: bool = True):
    """
    设置爬虫专用日志记录器
    日志保存在 logs/spider/views/{year}/{month}/{name}_YYYYMMDD.log
    
    Args:
        name: 日志记录器名称 (如: crawl_views, import_views, export_views)
        flushable: 是否启用实时刷新（默认启用）
    
    Returns:
        配置好的日志记录器
    """
    return setup_logger(name, use_daily_dir=True, flushable=flushable)


def get_latest_log_file(name: str) -> str:
    """
    获取指定名称的最新日志文件路径
    
    Args:
        name: 日志记录器名称
        
    Returns:
        最新日志文件的完整路径
    """
    log_dir = get_daily_log_dir()
    date_str = datetime.now().strftime("%Y%m%d")
    return os.path.join(log_dir, f"{name}_{date_str}.log")
