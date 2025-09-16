#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
修复数据库中乱码的中文字符
"""
import os
import sys
import django

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xxm_fans_home.settings')

# 初始化Django
django.setup()

from main.models import Style, Songs

def fix_garbled_text(text):
    """尝试修复乱码文本"""
    if not text:
        return text
        
    # 如果已经是正常的中文，直接返回
    if all(ord(char) < 10000 and char != '�' for char in text):
        return text
        
    try:
        # 尝试多种编码修复方法
        # 方法1: latin1 -> utf-8
        if isinstance(text, str):
            fixed = text.encode('latin1').decode('utf-8')
            return fixed
    except (UnicodeError, UnicodeEncodeError, UnicodeDecodeError):
        pass
        
    try:
        # 方法2: gbk -> utf-8
        if isinstance(text, str):
            fixed = text.encode('gbk').decode('utf-8')
            return fixed
    except (UnicodeError, UnicodeEncodeError, UnicodeDecodeError):
        pass
        
    # 如果都无法修复，返回原文本
    return text

def safe_print(text):
    """安全打印，避免编码错误"""
    try:
        print(text)
    except UnicodeEncodeError:
        try:
            # 如果打印失败，使用repr显示
            print(repr(text))
        except UnicodeEncodeError:
            # 如果repr也失败，转换为ASCII
            print(text.encode('ascii', 'ignore').decode('ascii'))

def fix_style_names():
    """修复曲风表中的乱码"""
    print("修复曲风表...")
    styles = Style.objects.all()
    fixed_count = 0
    for style in styles:
        original_name = style.name
        fixed_name = fix_garbled_text(original_name)
        if fixed_name != original_name:
            safe_print(f"修复曲风: {original_name} -> {fixed_name}")
            style.name = fixed_name
            style.save()
            fixed_count += 1
    print(f"曲风表修复完成，共修复 {fixed_count} 条记录")

def fix_song_fields():
    """修复歌曲表中的乱码"""
    print("修复歌曲表...")
    songs = Songs.objects.all()
    fixed_count = 0
    for song in songs:
        updated = False
        
        # 修复歌曲名
        original_song_name = song.song_name
        fixed_song_name = fix_garbled_text(original_song_name)
        if fixed_song_name != original_song_name:
            try:
                safe_print(f"修复歌曲名: {original_song_name} -> {fixed_song_name}")
            except:
                safe_print(f"修复歌曲名: [无法显示] -> [已修复]")
            song.song_name = fixed_song_name
            updated = True
            
        # 修复歌手名
        original_singer = song.singer
        fixed_singer = fix_garbled_text(original_singer)
        if fixed_singer != original_singer:
            try:
                safe_print(f"修复歌手名: {original_singer} -> {fixed_singer}")
            except:
                safe_print(f"修复歌手名: [无法显示] -> [已修复]")
            song.singer = fixed_singer
            updated = True
            
        # 修复语言
        original_language = song.language
        fixed_language = fix_garbled_text(original_language)
        if fixed_language != original_language:
            try:
                safe_print(f"修复语言: {original_language} -> {fixed_language}")
            except:
                safe_print(f"修复语言: [无法显示] -> [已修复]")
            song.language = fixed_language
            updated = True
            
        if updated:
            song.save()
            fixed_count += 1
            
    print(f"歌曲表修复完成，共修复 {fixed_count} 条记录")

if __name__ == '__main__':
    fix_style_names()
    fix_song_fields()