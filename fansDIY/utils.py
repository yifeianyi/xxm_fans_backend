from datetime import datetime
from .models import Collection, Work
from tools.bilibili import BilibiliAPIClient, BilibiliCoverDownloader, BilibiliAPIError, PageInfo

class FansDIYBilibiliImporter:
    """FansDIY专用的B站视频导入器"""

    def __init__(self):
        self.api_client = BilibiliAPIClient(timeout=10, retry_times=3)
        self.cover_downloader = BilibiliCoverDownloader()

    def import_bv_work(self, bvid, collection_name, notes=""):
        """从B站BV号导入作品到指定合集"""
        print(f"[BV:{bvid}] 开始导入到合集: {collection_name}")

        try:
            # 获取或创建合集
            collection, created_collection = Collection.objects.get_or_create(name=collection_name)
            if created_collection:
                print(f"✅ 创建新合集: {collection_name}")

            # 获取视频信息
            video_info = self.api_client.get_video_info(bvid)

            # 提取视频信息
            title = video_info.title
            author = video_info.get_author_name()
            cover_url = video_info.get_cover_url()
            pubdate = video_info.get_publish_time()

            # 构建观看链接
            view_url = f"https://player.bilibili.com/player.html?bvid={bvid}"

            # 检查是否已存在
            if Work.objects.filter(title=title, collection=collection).exists():
                return {
                    "success": False,
                    "message": f"作品《{title}》已存在于合集《{collection_name}》中",
                    "title": title,
                    "author": author,
                    "cover_url": cover_url
                }

            # 下载并保存封面
            final_cover_url = self.cover_downloader.download_by_collection(
                cover_url,
                collection_name,
                pubdate
            )
            if not final_cover_url:
                final_cover_url = cover_url

            # 创建作品记录
            work = Work.objects.create(
                collection=collection,
                title=title,
                cover_url=final_cover_url,
                view_url=view_url,
                author=author,
                notes=notes
            )

            # 更新合集作品数量
            collection.update_works_count()

            print(f"✅ 成功导入作品: {title} - {author}")

            return {
                "success": True,
                "message": f"成功导入作品《{title}》到合集《{collection_name}》",
                "title": title,
                "author": author,
                "cover_url": final_cover_url,
                "created_collection": created_collection
            }

        except BilibiliAPIError as e:
            print(f"❌ 导入失败: {e.message}")
            return {
                "success": False,
                "message": f"B站API错误: {e.message}",
                "title": "",
                "author": "",
                "cover_url": ""
            }
        except Exception as e:
            print(f"❌ 导入失败: {e}")
            return {
                "success": False,
                "message": f"导入失败: {str(e)}",
                "title": "",
                "author": "",
                "cover_url": ""
            }

# 保持向后兼容的函数接口
def import_bv_work(bvid, collection_name, notes=""):
    """从B站BV号导入作品到指定合集"""
    importer = FansDIYBilibiliImporter()
    return importer.import_bv_work(bvid, collection_name, notes) 