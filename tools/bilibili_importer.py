import requests
import re
import os
from datetime import datetime
from collections import defaultdict
from django.conf import settings
from song_management.models import SongRecord as SongRecord, Song as Songs
from django.core.exceptions import MultipleObjectsReturned

class BilibiliImporter:
    """B站视频信息导入器"""
    
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0"
        }
    
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
        if pending_parts is None:
            try:
                pending_parts = self._parse_bv_parts(bvid)
                print(f"[BV:{bvid}] 解析完成，找到 {len(pending_parts)} 个分P")
            except Exception as e:
                print(f"[BV:{bvid}] 解析过程中发生异常: {e}")
                return [], [], None
        
        results = []
        cur_song_counts = defaultdict(int)
        remaining_parts = []
        conflict_info = None
        
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
        new_results = self._process_remaining_parts(bvid, parts_to_process, cur_song_counts)
        results.extend(new_results)
        print(f"[BV:{bvid}] 剩余分P处理完成，新增 {len(new_results)} 条")
        
        print(f"[BV:{bvid}] 导入完成，共导入 {len(results)} 条")
        return results, [], conflict_info
    
    def _parse_bv_parts(self, bvid):
        """解析BV的所有分P信息"""
        print(f"[BV:{bvid}] 开始解析分P信息")
        
        # Step 1: 获取分P信息
        pagelist_url = f"https://api.bilibili.com/x/player/pagelist?bvid={bvid}"
        try:
            print(f"[BV:{bvid}] 请求分P信息API: {pagelist_url}")
            response = requests.get(pagelist_url, headers=self.headers, timeout=5)
            response.raise_for_status()
            json_data = response.json()
            print(f"[BV:{bvid}] 分P信息API响应成功")
        except requests.exceptions.Timeout:
            print(f"[BV:{bvid}] 获取分P信息超时")
            return []
        except requests.exceptions.RequestException as e:
            print(f"[BV:{bvid}] 获取分P信息网络错误: {e}")
            return []
        except Exception as e:
            print(f"[BV:{bvid}] 获取分P信息失败: {e}")
            return []
        
        # Step 2: 获取视频总封面
        fallback_cover_url = None
        try:
            print(f"[BV:{bvid}] 请求视频信息API")
            response = requests.get(f"https://api.bilibili.com/x/web-interface/view?bvid={bvid}", headers=self.headers, timeout=3)
            response.raise_for_status()
            video_info = response.json()
            if video_info.get("code") == 0 and video_info.get("data"):
                fallback_cover_url = video_info["data"].get("pic")
                print(f"[BV:{bvid}] 获取总封面成功: {fallback_cover_url}")
            else:
                print(f"[BV:{bvid}] 视频信息API返回错误: {video_info.get('message', '未知错误')}")
        except requests.exceptions.Timeout:
            print(f"[BV:{bvid}] 获取总封面超时，将使用默认封面")
        except requests.exceptions.RequestException as e:
            print(f"[BV:{bvid}] 获取总封面网络错误: {e}，将使用默认封面")
        except Exception as e:
            print(f"[BV:{bvid}] 获取总封面失败: {e}，将使用默认封面")
        
# 解析所有分P信息并下载封面
        pending_parts = []
        if json_data.get("code") == 0 and isinstance(json_data.get("data"), list):
            print(f"[BV:{bvid}] 开始解析 {len(json_data['data'])} 个分P")
            
            # 如果没有获取到封面，使用默认值
            if not fallback_cover_url:
                print(f"[BV:{bvid}] 警告：没有获取到总封面，将使用分P默认封面")
            
            # 先收集所有有效的分P信息
            valid_parts = []
            total_parts = len(json_data["data"])
            valid_count = 0
            skipped_count = 0
            for page_info in json_data["data"]:
                page = page_info["page"]
                cid = page_info["cid"]
                title = page_info["part"]
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
                            "part_url": f"https://player.bilibili.com/player.html?bvid={bvid}&p={page}",
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
                    final_cover_url = self.download_and_save_cover(part["cover_url"], performed_date)
                    # 如果下载失败，使用原始URL
                    if not final_cover_url or final_cover_url == part["cover_url"]:
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
        else:
            print(f"[BV:{bvid}] API返回数据格式错误: code={json_data.get('code')}, data类型={type(json_data.get('data'))}")
            return []
        
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
            try:
                song_obj = Songs.objects.get(id=selected_song_id)
                created_song = False
                
                if SongRecord.objects.filter(song=song_obj, performed_at=performed_date).exists():
                    results.append({
                        "song_name": song_name,
                        "url": part_url,
                        "note": "❌ 已存在，跳过",
                        "created_song": created_song,
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
            
            except Songs.DoesNotExist:
                # 如果选定的歌曲不存在，这通常不应该发生，但为了健壮性还是处理一下
                results.append({
                    "song_name": song_name,
                    "url": part_url,
                    "note": "❌ 选定的歌曲不存在",
                    "created_song": False,
                    "cover_url": cover_url,
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
            
            if SongRecord.objects.filter(song=song_obj, performed_at=performed_date).exists():
                results.append({
                    "song_name": song_name,
                    "url": part_url,
                    "note": "❌ 已存在，跳过",
                    "created_song": created_song,
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
        
        return results
    
    def download_and_save_cover(self, cover_url, performed_date):
        """下载并保存封面图片"""
        if not cover_url:
            return None
        
        try:
            # 构建本地保存路径
            date_str = performed_date.strftime("%Y-%m-%d")
            year = performed_date.strftime("%Y")
            month = performed_date.strftime("%m")
            
            # 本地封面目录根（已迁移到media/covers目录）
            # 使用相对路径
            BASE_DIR = os.path.join("..", "..", "media", "covers")
            save_dir = os.path.join(BASE_DIR, year, month)
            
            # 确保目录存在
            try:
                os.makedirs(save_dir, exist_ok=True)
            except Exception as dir_error:
                print(f"创建目录失败: {dir_error}, 使用临时目录")
                # 如果创建目录失败，使用临时目录
                import tempfile
                save_dir = tempfile.gettempdir()
            
            filename = f"{date_str}.jpg"
            file_path = os.path.join(save_dir, filename)
            local_path = f"/covers/{year}/{month}/{filename}"
            
            # 如果文件已存在，直接返回本地路径
            if os.path.exists(file_path):
                print(f"封面已存在: {local_path}")
                return local_path
            
            # 下载图片
            print(f"开始下载封面: {cover_url}")
            try:
                response = requests.get(cover_url, headers=self.headers, timeout=5)
                response.raise_for_status()
                image_data = response.content
            except requests.exceptions.Timeout:
                print(f"封面下载超时: {cover_url}")
                return cover_url
            except requests.exceptions.RequestException as e:
                print(f"封面下载网络错误: {e}")
                return cover_url
            
            # 保存图片
            with open(file_path, "wb") as f:
                f.write(image_data)
            
            print(f"封面已下载: {local_path}")
            return local_path
            
        except requests.exceptions.RequestException as e:
            print(f"封面下载网络错误: {e}")
            return cover_url  # 返回原始URL作为备选
        except Exception as e:
            print(f"封面下载失败: {e}")
            return cover_url  # 返回原始URL作为备选