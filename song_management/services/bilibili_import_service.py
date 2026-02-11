import re
from datetime import datetime
from collections import defaultdict
from django.conf import settings
from song_management.models import SongRecord as SongRecord, Song as Songs
from django.core.exceptions import MultipleObjectsReturned

# 使用新的B站工具
from tools.bilibili import BilibiliAPIClient, BilibiliCoverDownloader, BilibiliAPIError

class BilibiliImporter:
    """B站视频信息导入器"""

    def __init__(self):
        self.api_client = BilibiliAPIClient(timeout=10, retry_times=3)
        self.cover_downloader = BilibiliCoverDownloader()
    
    def import_bv_song(self, bvid, selected_song_id=None, pending_parts=None):
        """
        导入BV歌曲，支持循环处理
        :param bvid: BV号
        :param selected_song_id: 选定的歌曲ID（用于处理冲突）
        :param pending_parts: 待处理的分P列表，如果为None则解析整个BV
        :return: (results, remaining_parts, conflict_info)
        """
        print(f"[BV:{bvid}] 开始导入")
        print(f"[BV:{bvid}] 参数: selected_song_id={selected_song_id}, pending_parts={'None' if pending_parts is None else len(pending_parts)}")
        
        # 如果没有待处理分P，则解析整个BV
        error_info = None
        if pending_parts is None:
            try:
                pending_parts = self._parse_bv_parts(bvid)
                print(f"[BV:{bvid}] 解析完成，找到 {len(pending_parts)} 个分P")
            except BilibiliAPIError as e:
                error_msg = f"B站API错误: {e.message}"
                print(f"[BV:{bvid}] {error_msg}")
                error_info = {"error": error_msg}
            except Exception as e:
                error_msg = f"解析异常: {str(e)}"
                print(f"[BV:{bvid}] {error_msg}")
                error_info = {"error": error_msg}
        
        results = []
        cur_song_counts = defaultdict(int)
        remaining_parts = []
        conflict_info = None
        
        # 如果有错误，返回错误信息
        if error_info:
            return results, [], error_info
        
        # 如果没有待处理分P，直接返回
        if not pending_parts:
            print(f"[BV:{bvid}] 没有找到有效的分P信息")
            return results, [], conflict_info
        
        # 处理当前分P（如果有选定的歌曲ID）
        if selected_song_id and pending_parts:
            results, remaining_parts, conflict_info = self._process_current_part(
                bvid, pending_parts, selected_song_id, cur_song_counts
            )
            if conflict_info:
                return results, remaining_parts, conflict_info
        
        # 处理剩余分P（包括没有 selected_song_id 的情况）
        parts_to_process = remaining_parts if selected_song_id else pending_parts
        print(f"[BV:{bvid}] 开始处理剩余分P，共 {len(parts_to_process)} 个")
        new_results, new_remaining, new_conflict = self._process_remaining_parts(bvid, parts_to_process, cur_song_counts)
        
        # 如果发生冲突，立即返回
        if new_conflict:
            print(f"[BV:{bvid}] 处理过程中发生冲突，中断导入")
            return results + new_results, new_remaining, new_conflict
        
        results.extend(new_results)
        print(f"[BV:{bvid}] 剩余分P处理完成，新增 {len(new_results)} 条")
        
        print(f"[BV:{bvid}] 导入完成，共导入 {len(results)} 条")
        return results, [], conflict_info
    
    def _parse_bv_parts(self, bvid):
        """解析BV的所有分P信息"""
        print(f"[BV:{bvid}] 开始解析分P信息")

        # Step 1: 获取分P信息
        try:
            pagelist = self.api_client.get_video_pagelist(bvid)
            print(f"[BV:{bvid}] 获取分P信息成功，共 {len(pagelist)} 个分P")
        except BilibiliAPIError as e:
            print(f"[BV:{bvid}] 获取分P信息失败: {e.message}")
            return []

        # Step 2: 获取视频总封面
        fallback_cover_url = None
        try:
            video_info = self.api_client.get_video_info(bvid)
            fallback_cover_url = video_info.get_cover_url()
            print(f"[BV:{bvid}] 获取总封面成功: {fallback_cover_url}")
        except BilibiliAPIError as e:
            print(f"[BV:{bvid}] 获取总封面失败: {e.message}，将使用默认封面")

        # 解析所有分P信息并下载封面
        pending_parts = []
        if pagelist:
            print(f"[BV:{bvid}] 开始解析 {len(pagelist)} 个分P")

            # 如果没有获取到封面，使用默认值
            if not fallback_cover_url:
                print(f"[BV:{bvid}] 警告：没有获取到总封面，将使用分P默认封面")

            # 先收集所有有效的分P信息
            valid_parts = []
            total_parts = len(pagelist)
            valid_count = 0
            skipped_count = 0

            for page_info in pagelist:
                page = page_info.page
                cid = page_info.cid
                title = page_info.part
                print(f"[BV:{bvid}] 解析分P {page}: {title}")

                # 提取日期（例如：2025年6月12日）
                match = re.search(r"(\d{4})年(\d{1,2})月(\d{1,2})日", title)
                if match:
                    try:
                        year, month, day = map(int, match.groups())
                        performed_date = datetime(year, month, day).date()
                        song_name = re.sub(r"\d{4}年\d{1,2}月\d{1,2}日", "", title).strip("- ").strip()
                        song_name = song_name.split("-")[0].strip()
                        print(f"[BV:{bvid}] 成功解析: {song_name} @ {performed_date}")
                        valid_count += 1

                        # 所有分P都使用总封面
                        valid_parts.append({
                            "page": page,
                            "cid": cid,
                            "title": title,
                            "song_name": song_name,
                            "performed_date": performed_date,
                            "part_url": page_info.get_player_url(bvid),
                            "cover_url": fallback_cover_url,
                        })
                    except Exception as e:
                        print(f"[BV:{bvid}] 日期解析失败: {e} - 标题: {title}")
                        skipped_count += 1
                else:
                    print(f"[BV:{bvid}] 分P标题不含时间: {title}")
                    skipped_count += 1

            # Step 4: 下载封面（每个日期只下载一次）
            downloaded_covers = {}
            for part in valid_parts:
                performed_date = part["performed_date"]
                date_str = performed_date.strftime("%Y-%m-%d")

                # 如果这个日期的封面还没下载过
                if date_str not in downloaded_covers:
                    print(f"[BV:{bvid}] 下载封面: {date_str}")
                    final_cover_url = self.cover_downloader.download_by_date(
                        part["cover_url"],
                        performed_date
                    )
                    # 如果下载失败，使用原始URL
                    if not final_cover_url:
                        print(f"[BV:{bvid}] 封面下载失败，使用原始URL: {part['cover_url']}")
                        final_cover_url = part["cover_url"]
                    downloaded_covers[date_str] = final_cover_url
                else:
                    print(f"[BV:{bvid}] 使用已下载的封面: {date_str}")
                    final_cover_url = downloaded_covers[date_str]

                # 更新分P信息中的封面路径
                part["cover_url"] = final_cover_url
                part["performed_date"] = performed_date.strftime("%Y-%m-%d")
                pending_parts.append(part)
                print(f"[BV:{bvid}] 添加到待处理列表: {part['song_name']}")

            print(f"[BV:{bvid}] 解析完成，共 {len(pending_parts)} 个有效分P (总计: {total_parts}, 有效: {valid_count}, 跳过: {skipped_count})")

        return pending_parts
    
    def _process_current_part(self, bvid, pending_parts, selected_song_id, cur_song_counts):
        """处理当前分P (由用户在冲突页面选择歌曲后调用)"""
        current_part = pending_parts[0]
        song_name = current_part["song_name"]
        performed_date = datetime.strptime(current_part["performed_date"], "%Y-%m-%d").date()
        part_url = current_part["part_url"]
        cover_url = current_part["cover_url"]
        results = []
        remaining_parts = []
        conflict_info = None
        
        # 当用户提供 selected_song_id 时，直接使用它关联歌曲
        # 这是解决冲突的关键步骤
        if selected_song_id:
            # 特殊值 "__new__" 表示创建新歌曲
            if selected_song_id == "__new__":
                song_obj = Songs.objects.create(song_name=song_name)
                created_song = True
                print(f"[BV:{bvid}] 创建新歌曲: {song_name} (ID: {song_obj.id})")
            else:
                try:
                    song_obj = Songs.objects.get(id=selected_song_id)
                    created_song = False
                    print(f"[BV:{bvid}] 使用现有歌曲: {song_name} (ID: {song_obj.id})")
                except Songs.DoesNotExist:
                    # 如果选定的歌曲不存在，这通常不应该发生，但为了健壮性还是处理一下
                    results.append({
                        "song_name": song_name,
                        "url": part_url,
                        "note": "❌ 选定的歌曲不存在",
                        "created_song": False,
                        "cover_url": cover_url,
                    })
                    remaining_parts = pending_parts[1:]
                    return results, remaining_parts, conflict_info
            
            # 检查记录是否已存在
            existing = SongRecord.objects.filter(song=song_obj, performed_at=performed_date).first()
            if existing:
                # 判断是本次导入创建的还是之前数据库就有的
                is_same_url = existing.url == part_url
                if is_same_url:
                    note = "✅ 已导入（同P）"
                elif created_song:
                    note = "❌ 新歌曲但该日期已有记录"
                else:
                    note = "❌ 已存在，跳过"
                results.append({
                    "song_name": song_name,
                    "url": part_url,
                    "note": note,
                    "created_song": False,  # 实际没有创建新记录
                    "cover_url": cover_url,
                })
            else:
                cur_song_counts[song_name] += 1
                count = cur_song_counts[song_name]
                note = f"同批版本 {count}" if count > 1 else None
                
                # ✅ 创建记录（封面已提前下载）
                SongRecord.objects.create(
                    song=song_obj,
                    performed_at=performed_date,
                    url=part_url,
                    notes=note,
                    cover_url=cover_url  # 直接使用已下载的封面路径
                )
                
                results.append({
                    "song_name": song_name,
                    "url": part_url,
                    "note": note,
                    "created_song": created_song,
                    "cover_url": cover_url
                })
        
        # 移除已处理的分P
        remaining_parts = pending_parts[1:]
        return results, remaining_parts, conflict_info
    
    def _process_remaining_parts(self, bvid, parts_to_process, cur_song_counts):
        """处理剩余分P"""
        results = []
        print(f"[BV:{bvid}] _process_remaining_parts 开始，共 {len(parts_to_process)} 个分P")
        
        for i, part in enumerate(parts_to_process):
            print(f"[BV:{bvid}] 处理第 {i+1}/{len(parts_to_process)} 个分P")
            song_name = part["song_name"]
            performed_date = datetime.strptime(part["performed_date"], "%Y-%m-%d").date()
            part_url = part["part_url"]
            cover_url = part["cover_url"]
            
            try:
                song_obj, created_song = Songs.objects.get_or_create(song_name=song_name)
            except MultipleObjectsReturned:
                # 遇到冲突，返回冲突信息
                candidates = Songs.objects.filter(song_name=song_name)
                # 构建从当前 part 开始的剩余部分列表
                # 首先添加当前有冲突的 part
                conflict_parts = [part]
                # 然后添加当前 part 之后的所有 parts
                remaining_index = parts_to_process.index(part) + 1
                if remaining_index < len(parts_to_process):
                    conflict_parts.extend(parts_to_process[remaining_index:])
                
                conflict_info = {
                    "song_name": song_name,
                    "candidates": candidates,
                    "current_part": part,
                    "remaining_parts": conflict_parts # 传递包含当前冲突和后续所有待处理的部分
                }
                # 当发生冲突时，立即返回当前已处理的结果和冲突信息
                # remaining_parts 返回空列表，表示中断主循环
                return results, [], conflict_info
            
            existing = SongRecord.objects.filter(song=song_obj, performed_at=performed_date).first()
            if existing:
                # 判断是否是同一分P（URL相同）
                if existing.url == part_url:
                    note = "✅ 已导入（同P）"
                else:
                    note = "❌ 已存在，跳过"
                results.append({
                    "song_name": song_name,
                    "url": part_url,
                    "note": note,
                    "created_song": False,
                    "cover_url": cover_url,
                })
                continue
            
            cur_song_counts[song_name] += 1
            count = cur_song_counts[song_name]
            note = f"同批版本 {count}" if count > 1 else None
            
            # ✅ 创建记录（封面已提前下载）
            SongRecord.objects.create(
                song=song_obj,
                performed_at=performed_date,
                url=part_url,
                notes=note,
                cover_url=cover_url  # 直接使用已下载的封面路径
            )
            
            results.append({
                "song_name": song_name,
                "url": part_url,
                "note": note,
                "created_song": created_song,
                "cover_url": cover_url
            })
        
        # 正常完成，返回结果、空的剩余列表、无冲突
        return results, [], None
    
    