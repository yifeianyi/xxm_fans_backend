from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import FanProfile, LiveAttendance
from .services.fan_ranking_service import FanRankingService


@receiver([post_save, post_delete], sender=FanProfile)
def invalidate_cache_on_profile_change(sender, instance, **kwargs):
    FanRankingService.invalidate_rank_cache()


@receiver([post_save, post_delete], sender=LiveAttendance)
def invalidate_cache_on_attendance_change(sender, instance, **kwargs):
    FanRankingService.invalidate_rank_cache()
