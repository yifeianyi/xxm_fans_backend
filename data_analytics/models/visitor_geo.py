"""
访客地理分布模型
存储访问网站的粉丝地理信息（国家、省份/州、城市等）
"""
from django.db import models
from django.contrib.auth.models import AnonymousUser


class VisitorGeo(models.Model):
    """
    访客地理信息模型
    记录每次访问的IP地址和解析出的地理位置信息
    """
    
    # IP地址
    ip_address = models.GenericIPAddressField(verbose_name="IP地址")
    
    # 地理位置信息
    country = models.CharField(max_length=100, blank=True, verbose_name="国家")
    country_code = models.CharField(max_length=10, blank=True, verbose_name="国家代码")
    region = models.CharField(max_length=100, blank=True, verbose_name="省份/州")
    region_code = models.CharField(max_length=20, blank=True, verbose_name="省份代码")
    city = models.CharField(max_length=100, blank=True, verbose_name="城市")
    district = models.CharField(max_length=100, blank=True, verbose_name="区县")
    
    # 经纬度
    latitude = models.FloatField(null=True, blank=True, verbose_name="纬度")
    longitude = models.FloatField(null=True, blank=True, verbose_name="经度")
    
    # 网络信息
    isp = models.CharField(max_length=200, blank=True, verbose_name="ISP运营商")
    
    # 访问信息
    visit_time = models.DateTimeField(auto_now_add=True, verbose_name="访问时间")
    user_agent = models.TextField(blank=True, verbose_name="User-Agent")
    referer = models.TextField(blank=True, verbose_name="来源页面")
    
    # 访问页面
    path = models.CharField(max_length=500, verbose_name="访问路径")
    
    # 是否为回访用户
    is_returning = models.BooleanField(default=False, verbose_name="是否回访")
    
    class Meta:
        db_table = 'data_analytics_visitorgeo'
        verbose_name = "访客地理信息"
        verbose_name_plural = "访客地理信息"
        ordering = ['-visit_time']
        indexes = [
            models.Index(fields=['ip_address', 'visit_time']),
            models.Index(fields=['country', 'region', 'city']),
            models.Index(fields=['visit_time']),
        ]
    
    def __str__(self):
        location = []
        if self.country:
            location.append(self.country)
        if self.region:
            location.append(self.region)
        if self.city:
            location.append(self.city)
        
        location_str = " - ".join(location) if location else "未知"
        return f"{self.ip_address} ({location_str}) @ {self.visit_time.strftime('%Y-%m-%d %H:%M:%S')}"


class GeoDistribution(models.Model):
    """
    地理分布统计（聚合数据）
    按天统计各地区的访问次数，用于提高查询性能
    """
    
    date = models.DateField(verbose_name="日期")
    country = models.CharField(max_length=100, verbose_name="国家")
    country_code = models.CharField(max_length=10, verbose_name="国家代码")
    region = models.CharField(max_length=100, blank=True, verbose_name="省份/州")
    region_code = models.CharField(max_length=20, blank=True, verbose_name="省份代码")
    
    # 访问次数
    visit_count = models.IntegerField(default=0, verbose_name="访问次数")
    unique_visitor_count = models.IntegerField(default=0, verbose_name="独立访客数")
    
    # 是否为国内（中国）
    is_domestic = models.BooleanField(default=True, verbose_name="是否国内访问")
    
    class Meta:
        db_table = 'data_analytics_geodistribution'
        verbose_name = "地理分布统计"
        verbose_name_plural = "地理分布统计"
        ordering = ['-date', '-visit_count']
        unique_together = ("date", "country", "region", "region_code")
        indexes = [
            models.Index(fields=['date', 'country', 'region']),
            models.Index(fields=['country', 'region']),
        ]
    
    def __str__(self):
        location = self.country
        if self.region:
            location = f"{location} - {self.region}"
        return f"{self.date}: {location} ({self.visit_count}次访问)"
