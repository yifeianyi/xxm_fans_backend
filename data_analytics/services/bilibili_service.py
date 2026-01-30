"""
B站视频信息导入服务
"""
from datetime import datetime
from django.conf import settings
from ..models import WorkStatic
from tools.bilibili import BilibiliAPIClient, BilibiliCoverDownloader, BilibiliAPIError
from core.thumbnail_generator import ThumbnailGenerator


class BilibiliWorkStaticImporter:
    """B站作品静态信息导入器"""

    def __init__(self):
        self.api_client = BilibiliAPIClient(timeout=10, retry_times=3)
        self.cover_downloader = BilibiliCoverDownloader()

    def import_bv_work_static(self, bvid):
        """
        导入B站视频的静态信息
        :param bvid: BV号
        :return: (success, message, work_static)
        """
        print(f"[BV:{bvid}] 开始导入作品静态信息")

        try:
            # 获取视频信息
            video_info = self.api_client.get_video_info(bvid)

            # 提取视频信息
            title = video_info.title
            author = video_info.get_author_name()
            cover_url = video_info.get_cover_url()
            publish_time = video_info.get_publish_time()

            # 检查是否已存在
            if WorkStatic.objects.filter(platform="bilibili", work_id=bvid).exists():
                return False, f"作品《{title}》已存在", None

            # 下载并保存封面到 data_analytics/covers 目录
            filename = f"{bvid}.jpg"
            sub_path = "data_analytics/covers"
            print(f"[BV:{bvid}] 开始下载封面...")
            local_cover_path = self.cover_downloader.download(cover_url, sub_path, filename)

            if local_cover_path:
                final_cover_url = f"/media/{local_cover_path}"
                print(f"[BV:{bvid}] ✅ 封面下载成功: {local_cover_path}")

                # 自动生成缩略图
                try:
                    thumbnail_path = ThumbnailGenerator.generate_thumbnail(local_cover_path)
                    if thumbnail_path != local_cover_path:
                        print(f"[BV:{bvid}] ✅ 缩略图生成成功: {thumbnail_path}")
                except Exception as e:
                    print(f"[BV:{bvid}] ⚠️ 缩略图生成失败: {e}")
            else:
                print(f"[BV:{bvid}] ❌ 封面下载失败，使用原始URL: {cover_url}")
                final_cover_url = cover_url

            # 创建WorkStatic记录
            work_static = WorkStatic.objects.create(
                platform="bilibili",
                work_id=bvid,
                title=title,
                author=author,
                publish_time=publish_time,
                cover_url=final_cover_url,
                is_valid=True
            )

            print(f"[BV:{bvid}] ✅ 成功导入作品静态信息: {title} - {author}")

            return True, f"成功导入作品《{title}》", work_static

        except BilibiliAPIError as e:
            return False, f"B站API错误: {e.message}", None
        except Exception as e:
            return False, f"导入失败: {str(e)}", None