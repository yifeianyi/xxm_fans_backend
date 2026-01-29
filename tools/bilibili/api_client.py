"""
B站API客户端
提供统一的B站API调用接口，包括错误处理、重试逻辑等
"""
import requests
import time
from typing import List, Optional, Dict, Any
from .models import VideoInfo, PageInfo, BilibiliAPIError


class BilibiliAPIClient:
    """统一的B站API客户端"""

    BASE_URL = "https://api.bilibili.com"
    
    # 默认配置
    DEFAULT_TIMEOUT = 10
    DEFAULT_RETRY_TIMES = 3
    DEFAULT_RETRY_DELAY = 1  # 秒

    def __init__(
        self,
        timeout: int = DEFAULT_TIMEOUT,
        retry_times: int = DEFAULT_RETRY_TIMES,
        retry_delay: int = DEFAULT_RETRY_DELAY
    ):
        """
        初始化API客户端
        :param timeout: 请求超时时间（秒）
        :param retry_times: 重试次数
        :param retry_delay: 重试延迟（秒）
        """
        self.timeout = timeout
        self.retry_times = retry_times
        self.retry_delay = retry_delay
        
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Referer": "https://www.bilibili.com"
        }

    def _make_request(
        self,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        method: str = "GET"
    ) -> Dict[str, Any]:
        """
        发起HTTP请求（带重试）
        :param url: 请求URL
        :param params: 请求参数
        :param method: 请求方法
        :return: 响应数据
        :raises: BilibiliAPIError
        """
        for attempt in range(self.retry_times):
            try:
                if method.upper() == "GET":
                    response = requests.get(
                        url,
                        params=params,
                        headers=self.headers,
                        timeout=self.timeout
                    )
                else:
                    response = requests.post(
                        url,
                        data=params,
                        headers=self.headers,
                        timeout=self.timeout
                    )
                
                response.raise_for_status()
                data = response.json()
                
                # 检查B站API返回的错误码
                if data.get("code") != 0:
                    error_msg = data.get("message", "未知错误")
                    # 如果是最后一次尝试，抛出异常
                    if attempt == self.retry_times - 1:
                        raise BilibiliAPIError(error_msg, data.get("code"))
                    # 否则继续重试
                    print(f"API返回错误: {error_msg}, 正在重试 ({attempt + 1}/{self.retry_times})")
                    time.sleep(self.retry_delay)
                    continue
                
                return data
                
            except requests.exceptions.Timeout:
                if attempt == self.retry_times - 1:
                    raise BilibiliAPIError(f"请求超时（{self.timeout}秒）")
                print(f"请求超时，正在重试 ({attempt + 1}/{self.retry_times})")
                time.sleep(self.retry_delay)
                
            except requests.exceptions.RequestException as e:
                if attempt == self.retry_times - 1:
                    raise BilibiliAPIError(f"网络错误: {str(e)}")
                print(f"网络错误: {str(e)}, 正在重试 ({attempt + 1}/{self.retry_times})")
                time.sleep(self.retry_delay)
        
        # 理论上不会执行到这里
        raise BilibiliAPIError("请求失败，已达到最大重试次数")

    def get_video_info(self, bvid: str) -> VideoInfo:
        """
        获取视频信息
        :param bvid: BV号
        :return: VideoInfo对象
        :raises: BilibiliAPIError
        """
        url = f"{self.BASE_URL}/x/web-interface/view"
        params = {"bvid": bvid}
        
        data = self._make_request(url, params)
        return VideoInfo.from_dict(data["data"])

    def get_video_pagelist(self, bvid: str) -> List[PageInfo]:
        """
        获取视频分P列表
        :param bvid: BV号
        :return: PageInfo对象列表
        :raises: BilibiliAPIError
        """
        url = f"{self.BASE_URL}/x/player/pagelist"
        params = {"bvid": bvid}
        
        data = self._make_request(url, params)
        return [PageInfo.from_dict(item) for item in data["data"]]

    def get_fans_count(self, uid: int) -> Dict[str, Any]:
        """
        获取粉丝数
        :param uid: 用户UID
        :return: 包含粉丝数的字典
        :raises: BilibiliAPIError
        """
        url = f"{self.BASE_URL}/x/relation/stat"
        params = {"vmid": uid}
        
        data = self._make_request(url, params)
        return {
            "uid": uid,
            "follower": data["data"]["follower"],
            "following": data["data"]["following"],
        }

    def batch_get_video_info(self, bvids: List[str]) -> Dict[str, VideoInfo]:
        """
        批量获取视频信息
        :param bvids: BV号列表
        :return: {bvid: VideoInfo} 字典
        :raises: BilibiliAPIError
        """
        result = {}
        for bvid in bvids:
            try:
                result[bvid] = self.get_video_info(bvid)
            except BilibiliAPIError as e:
                print(f"获取 {bvid} 信息失败: {e.message}")
                result[bvid] = None
        return result