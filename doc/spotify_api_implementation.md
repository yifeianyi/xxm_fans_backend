# Spotify API集成实现

## 1. 安装依赖

首先需要安装Spotipy库：

```bash
pip install spotipy
```

## 2. 创建Spotify开发者应用

1. 访问 https://developers.spotify.com/
2. 登录或创建Spotify账号
3. 进入开发者控制台
4. 创建新应用：
   - 应用名称：xxm_fans_home
   - 应用描述：音乐粉丝网站曲风分类
   - 重定向URI：http://127.0.0.1:8080
   - 选择Web API

5. 记录下Client ID和Client Secret

## 3. 环境变量配置

在项目根目录创建.env文件，添加以下内容：

```
SPOTIPY_CLIENT_ID=your_client_id_here
SPOTIPY_CLIENT_SECRET=your_client_secret_here
SPOTIPY_REDIRECT_URI=http://127.0.0.1:8080
```

## 4. 实现代码

创建spotify_style_assign.py文件：

```python
#!/usr/bin/env python
"""
使用Spotify API为歌曲分配曲风
"""

import os
import django
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import time

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xxm_fans_home.settings')
django.setup()

def get_spotify_client():
    """
    获取Spotify客户端
    """
    # 使用客户端凭证流程（不需要用户授权，只能访问公开数据）
    client_credentials_manager = SpotifyClientCredentials()
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
    return sp

def search_song_on_spotify(sp, song_name, singer):
    """
    在Spotify上搜索歌曲
    """
    # 构造搜索查询
    query = f"track:{song_name} artist:{singer}"
    
    try:
        # 搜索歌曲
        results = sp.search(q=query, type='track', limit=1)
        
        # 检查是否有搜索结果
        if results['tracks']['items']:
            track = results['tracks']['items'][0]
            return track
        else:
            # 如果没有找到，尝试只搜索歌曲名
            query = f"track:{song_name}"
            results = sp.search(q=query, type='track', limit=1)
            if results['tracks']['items']:
                track = results['tracks']['items'][0]
                return track
    except Exception as e:
        print(f"搜索歌曲时出错: {e}")
    
    return None

def get_artist_genres(sp, artist_id):
    """
    获取艺术家的曲风分类
    """
    try:
        artist = sp.artist(artist_id)
        return artist.get('genres', [])
    except Exception as e:
        print(f"获取艺术家曲风时出错: {e}")
        return []

def assign_styles_via_spotify():
    """
    使用Spotify API为歌曲分配曲风
    """
    from main.models import Songs, Style, SongStyle
    
    print("开始使用Spotify API为歌曲分配曲风...")
    
    # 获取Spotify客户端
    sp = get_spotify_client()
    
    # 获取所有歌曲
    songs = list(Songs.objects.all())
    print(f"找到 {len(songs)} 首歌曲")
    
    # 为每首歌曲分配曲风
    assigned_count = 0
    for i, song in enumerate(songs):
        print(f"处理歌曲 {i+1}/{len(songs)}: {song.song_name} - {song.singer}")
        
        # 在Spotify上搜索歌曲
        track = search_song_on_spotify(sp, song.song_name, song.singer or '')
        
        if track:
            # 获取艺术家ID
            artist_id = track['artists'][0]['id'] if track['artists'] else None
            
            if artist_id:
                # 获取艺术家的曲风分类
                genres = get_artist_genres(sp, artist_id)
                
                if genres:
                    print(f"  找到曲风: {genres}")
                    
                    # 为每个曲风创建关联
                    for genre in genres:
                        # 获取或创建曲风对象
                        style_obj, _ = Style.objects.get_or_create(name=genre)
                        
                        # 创建歌曲曲风关联
                        song_style, created = SongStyle.objects.get_or_create(
                            song=song, style=style_obj
                        )
                        
                        if created:
                            assigned_count += 1
                            print(f"  为歌曲 '{song.song_name}' 添加曲风 '{genre}'")
                else:
                    print(f"  未找到曲风信息")
            else:
                print(f"  未找到艺术家信息")
        else:
            print(f"  未在Spotify上找到歌曲")
        
        # 添加延迟以避免API限制
        time.sleep(0.1)
    
    print(f"成功创建 {assigned_count} 个歌曲曲风关联")

if __name__ == "__main__":
    assign_styles_via_spotify()
```