"""
访客地理信息收集中间件
自动记录访问者的IP地址和地理位置信息
"""
import logging
from django.utils import timezone
from django.contrib.auth.models import AnonymousUser

try:
    from data_analytics.models import VisitorGeo
    MODELS_AVAILABLE = True
except ImportError:
    MODELS_AVAILABLE = False

logger = logging.getLogger(__name__)


class VisitorGeoMiddleware:
    """
    访客地理信息收集中间件
    自动记录每个请求的IP地址和地理位置信息
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # 处理请求
        response = self.get_response(request)
        
        # 记录访客地理信息（排除静态文件和API请求）
        if MODELS_AVAILABLE and self._should_record(request):
            self._record_visitor(request)
        
        return response
    
    def _should_record(self, request):
        """判断是否需要记录该请求"""
        path = request.path
        
        # 排除静态文件
        if path.startswith(('/static/', '/media/', '/admin/')):
            return False
        
        # 排除API接口（除了地理信息相关的）
        if path.startswith('/api/') and 'geo' not in path:
            return False
        
        # 排除robots.txt和sitemap.xml
        if path in ['/robots.txt', '/sitemap.xml']:
            return False
        
        return True
    
    def _record_visitor(self, request):
        """记录访客地理信息"""
        try:
            # 获取IP地址
            ip_address = self._get_client_ip(request)
            
            # 获取User-Agent
            user_agent = request.META.get('HTTP_USER_AGENT', '')
            
            # 获取来源页面
            referer = request.META.get('HTTP_REFERER', '')
            
            # 获取访问路径
            path = request.path
            
            # 检查是否为回访用户（同一天内同一IP）
            today = timezone.now().date()
            is_returning = VisitorGeo.objects.filter(
                ip_address=ip_address,
                visit_time__date=today
            ).exists()
            
            # 获取地理位置信息
            geo_info = self._get_geo_info(ip_address)
            
            # 创建访客记录
            VisitorGeo.objects.create(
                ip_address=ip_address,
                country=geo_info.get('country', ''),
                country_code=geo_info.get('country_code', ''),
                region=geo_info.get('region', ''),
                region_code=geo_info.get('region_code', ''),
                city=geo_info.get('city', ''),
                district=geo_info.get('district', ''),
                latitude=geo_info.get('latitude'),
                longitude=geo_info.get('longitude'),
                isp=geo_info.get('isp', ''),
                user_agent=user_agent,
                referer=referer,
                path=path,
                is_returning=is_returning
            )
            
        except Exception as e:
            logger.error(f"记录访客地理信息失败: {e}")
    
    def _get_client_ip(self, request):
        """获取客户端真实IP地址"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def _get_geo_info(self, ip_address):
        """
        获取IP地址的地理位置信息
        这里使用IP地理位置查询服务（如IP2Location、MaxMind等）
        返回包含地理位置信息的字典
        """
        geo_info = {
            'country': '',
            'country_code': '',
            'region': '',
            'region_code': '',
            'city': '',
            'district': '',
            'latitude': None,
            'longitude': None,
            'isp': ''
        }
        
        try:
            # 这里可以集成第三方IP地理位置查询服务
            # 例如：IP2Location、MaxMind GeoIP、IPAPI等
            
            # 临时实现：返回测试数据
            # 实际部署时需要替换为真实的IP地理位置查询服务
            if ip_address in ['127.0.0.1', 'localhost']:
                # 本地访问
                geo_info.update({
                    'country': '中国',
                    'country_code': 'CN',
                    'region': '湖北省',
                    'region_code': '42',
                    'city': '武汉市',
                    'latitude': 30.5928,
                    'longitude': 114.3055,
                    'isp': '本地网络'
                })
            else:
                # 实际项目中，这里应该调用IP地理位置查询API
                # 例如：
                # import requests
                # response = requests.get(f'https://ipapi.co/{ip_address}/json/')
                # if response.status_code == 200:
                #     data = response.json()
                #     geo_info.update({
                #         'country': data.get('country_name', ''),
                #         'country_code': data.get('country_code', ''),
                #         'region': data.get('region', ''),
                #         'region_code': data.get('region_code', ''),
                #         'city': data.get('city', ''),
                #         'latitude': data.get('latitude'),
                #         'longitude': data.get('longitude'),
                #         'isp': data.get('org', '')
                #     })
                pass
                
        except Exception as e:
            logger.error(f"获取IP地理位置信息失败: {e}")
        
        return geo_info
