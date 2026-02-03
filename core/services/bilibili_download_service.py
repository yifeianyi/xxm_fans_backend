"""
B站视频音频下载地址生成服务
使用 yt-dlp 获取音频流地址，不实际下载文件
"""
from typing import Dict, Optional
import subprocess
import json
import re


class BilibiliDownloadService:
    """B站视频音频下载地址生成服务"""

    @staticmethod
    def generate_audio_download_url(bvid: str, title: str) -> Dict[str, str]:
        """
        使用 yt-dlp 生成B站视频音频下载地址

        Args:
            bvid: B站视频BV号
            title: 视频标题

        Returns:
            dict: 包含下载地址和文件名的字典
        """
        if not bvid:
            raise ValueError("BV号不能为空")

        # 构建视频URL
        video_url = f"https://www.bilibili.com/video/{bvid}"

        try:
            # 使用 yt-dlp 获取音频流地址
            # -f bestaudio/best: 选择最佳音频质量
            # --no-playlist: 不下载播放列表
            # --skip-download: 跳过下载，只获取信息
            # --print "%(url)s": 只打印URL
            result = subprocess.run(
                [
                    'yt-dlp',
                    '-f', 'bestaudio/best',
                    '--no-playlist',
                    '--skip-download',
                    '--print', '%(url)s',
                    '--print', '%(filename)s',
                    '--print', '%(title)s',
                    '--print', '%(duration)s',
                    video_url
                ],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode != 0:
                raise Exception(f"yt-dlp 执行失败: {result.stderr}")

            # 解析输出
            output_lines = result.stdout.strip().split('\n')
            if len(output_lines) < 2:
                raise Exception("yt-dlp 输出格式异常")

            audio_url = output_lines[0].strip()
            filename = output_lines[1].strip() if len(output_lines) > 1 else f"{title}_{bvid}.mp3"
            video_title = output_lines[2].strip() if len(output_lines) > 2 else title
            duration_str = output_lines[3].strip() if len(output_lines) > 3 else '0'

            # 解析时长
            try:
                duration = float(duration_str)
            except ValueError:
                duration = 0

            if not audio_url:
                raise Exception("未能获取音频下载地址")

            return {
                'download_url': audio_url,
                'filename': filename,
                'bvid': bvid,
                'title': video_title,
                'duration': duration
            }

        except subprocess.TimeoutExpired:
            raise Exception("获取下载地址超时")
        except FileNotFoundError:
            raise Exception("yt-dlp 未安装，请先安装: pip install yt-dlp")
        except Exception as e:
            raise Exception(f"获取下载地址失败: {str(e)}")

    @staticmethod
    def get_audio_formats(bvid: str) -> Dict:
        """
        获取所有可用的音频格式

        Args:
            bvid: B站视频BV号

        Returns:
            dict: 包含所有音频格式的信息
        """
        if not bvid:
            raise ValueError("BV号不能为空")

        video_url = f"https://www.bilibili.com/video/{bvid}"

        try:
            # 获取所有格式信息
            result = subprocess.run(
                [
                    'yt-dlp',
                    '--print', 'json',
                    '--list-formats',
                    '--no-playlist',
                    video_url
                ],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode != 0:
                raise Exception(f"获取格式列表失败: {result.stderr}")

            # 解析格式信息
            video_info = json.loads(result.stdout)
            formats = video_info.get('formats', [])

            # 筛选出音频格式
            audio_formats = []
            for fmt in formats:
                if fmt.get('vcodec') == 'none' or fmt.get('acodec') != 'none':
                    audio_formats.append({
                        'format_id': fmt.get('format_id'),
                        'ext': fmt.get('ext'),
                        'format': fmt.get('format'),
                        'url': fmt.get('url'),
                        'filesize': fmt.get('filesize'),
                        'abr': fmt.get('abr'),  # 音频比特率
                        'asr': fmt.get('asr'),  # 采样率
                    })

            return {
                'bvid': bvid,
                'title': video_info.get('title'),
                'audio_formats': audio_formats
            }

        except Exception as e:
            raise Exception(f"获取格式列表失败: {str(e)}")

    @staticmethod
    def validate_bvid(bvid: str) -> bool:
        """
        验证BV号格式是否有效

        Args:
            bvid: B站视频BV号

        Returns:
            bool: BV号是否有效
        """
        if not bvid:
            return False

        # BV号格式: BV + 10位字母数字
        pattern = r'^BV[a-zA-Z0-9]{10}$'
        return bool(re.match(pattern, bvid))


# Demo 测试代码
if __name__ == "__main__":
    # 测试生成下载地址
    test_bvid = "BV1i868B1ESw"
    test_title = "测试视频"

    print("=== B站音频下载服务 Demo ===\n")

    # 验证BV号
    print(f"1. 验证BV号: {test_bvid}")
    is_valid = BilibiliDownloadService.validate_bvid(test_bvid)
    print(f"   BV号有效: {is_valid}\n")

    # 检查 yt-dlp 是否安装
    print("2. 检查 yt-dlp 安装状态")
    try:
        result = subprocess.run(['yt-dlp', '--version'], capture_output=True, text=True)
        print(f"   yt-dlp 版本: {result.stdout.strip()}\n")
    except FileNotFoundError:
        print("   ❌ yt-dlp 未安装")
        print("   请运行: pip install yt-dlp\n")
        print("=== Demo 完成 ===")
        exit(1)

    # 生成下载地址
    print(f"3. 生成音频下载地址")
    try:
        download_info = BilibiliDownloadService.generate_audio_download_url(
            test_bvid, test_title
        )
        print(f"   ✅ 下载地址: {download_info['download_url']}")
        print(f"   文件名: {download_info['filename']}")
        print(f"   BV号: {download_info['bvid']}")
        print(f"   标题: {download_info['title']}")
        print(f"   时长: {download_info['duration']}秒\n")
    except Exception as e:
        print(f"   ❌ 获取失败: {str(e)}\n")

    # 获取音频格式列表
    print("4. 获取可用音频格式")
    try:
        formats_info = BilibiliDownloadService.get_audio_formats(test_bvid)
        print(f"   标题: {formats_info['title']}")
        print(f"   可用格式数量: {len(formats_info['audio_formats'])}")
        for i, fmt in enumerate(formats_info['audio_formats'][:3], 1):
            print(f"   格式 {i}:")
            print(f"     - ID: {fmt['format_id']}")
            print(f"     - 扩展名: {fmt['ext']}")
            print(f"     - 比特率: {fmt.get('abr', 'N/A')}")
            print(f"     - 采样率: {fmt.get('asr', 'N/A')}")
    except Exception as e:
        print(f"   ❌ 获取失败: {str(e)}\n")

    print("\n=== Demo 完成 ===")