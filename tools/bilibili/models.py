"""
B站数据模型
提供VideoInfo和PageInfo数据类，用于封装B站API返回的数据
"""
from datetime import datetime
from typing import Dict, Any, Optional


class BilibiliAPIError(Exception):
    """B站API错误"""
    def __init__(self, message: str, code: int = -1):
        self.message = message
        self.code = code
        super().__init__(f"B站API错误 [{code}]: {message}")


class VideoInfo:
    """视频信息数据类"""

    def __init__(
        self,
        bvid: str,
        title: str,
        pic: str,
        owner: Dict[str, Any],
        pubdate: int,
        desc: str = "",
        duration: int = 0,
        stat: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        self.bvid = bvid
        self.title = title
        self.pic = pic  # 封面URL
        self.owner = owner  # dict: {"mid": 123, "name": "作者", "face": "..."}
        self.pubdate = pubdate  # 时间戳
        self.desc = desc
        self.duration = duration
        self.stat = stat or {}  # dict: {"view": 100, "danmaku": 10, ...}
        self._raw_data = kwargs  # 保留原始数据，便于扩展

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'VideoInfo':
        """从字典创建对象"""
        return cls(**data)

    def get_cover_url(self) -> str:
        """获取封面URL"""
        return self.pic

    def get_author_name(self) -> str:
        """获取作者名称"""
        return self.owner.get("name", "")

    def get_author_mid(self) -> int:
        """获取作者ID"""
        return self.owner.get("mid", 0)

    def get_publish_time(self) -> datetime:
        """获取发布时间（datetime对象）"""
        return datetime.fromtimestamp(self.pubdate)

    def get_view_count(self) -> int:
        """获取播放量"""
        return self.stat.get("view", 0)

    def get_danmaku_count(self) -> int:
        """获取弹幕数"""
        return self.stat.get("danmaku", 0)

    def get_like_count(self) -> int:
        """获取点赞数"""
        return self.stat.get("like", 0)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "bvid": self.bvid,
            "title": self.title,
            "pic": self.pic,
            "author": self.get_author_name(),
            "author_mid": self.get_author_mid(),
            "publish_time": self.get_publish_time(),
            "description": self.desc,
            "duration": self.duration,
            "statistics": self.stat,
        }

    def __repr__(self) -> str:
        return f"VideoInfo(bvid={self.bvid}, title={self.title})"


class PageInfo:
    """分P信息数据类"""

    def __init__(
        self,
        page: int,
        cid: int,
        part: str,
        duration: int = 0,
        **kwargs
    ):
        self.page = page  # 分P序号
        self.cid = cid  # 分P的CID
        self.part = part  # 分P标题
        self.duration = duration  # 时长（秒）
        self._raw_data = kwargs

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PageInfo':
        """从字典创建对象"""
        return cls(**data)

    def get_player_url(self, bvid: str) -> str:
        """获取播放器URL"""
        return f"https://player.bilibili.com/player.html?bvid={bvid}&p={self.page}"

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "page": self.page,
            "cid": self.cid,
            "part": self.part,
            "duration": self.duration,
            "player_url": self._raw_data.get("bvid", ""),
        }

    def __repr__(self) -> str:
        return f"PageInfo(page={self.page}, part={self.part})"