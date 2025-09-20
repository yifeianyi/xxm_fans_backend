from .models import SongRecord, Songs
from tools.bilibili_importer import BilibiliImporter
from tools.cover_downloader import CoverDownloader

# 保持向后兼容的函数接口
def import_bv_song(bvid, selected_song_id=None, pending_parts=None):
    """
    导入BV歌曲，支持循环处理
    :param bvid: BV号
    :param selected_song_id: 选定的歌曲ID（用于处理冲突）
    :param pending_parts: 待处理的分P列表，如果为None则解析整个BV
    :return: (results, remaining_parts, conflict_info)
    """
    importer = BilibiliImporter()
    return importer.import_bv_song(bvid, selected_song_id, pending_parts)

def download_and_save_cover(cover_url, performed_date):
    """下载并保存封面图片"""
    downloader = CoverDownloader()
    return downloader.download_and_save_cover(cover_url, performed_date)


