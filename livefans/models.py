from django.db import models


class Platform(models.TextChoices):
    BILIBILI = 'bilibili', '哔哩哔哩'


class FanProfile(models.Model):
    """B站粉丝用户画像"""

    platform = models.CharField(
        max_length=20,
        choices=Platform.choices,
        default=Platform.BILIBILI,
        verbose_name='平台'
    )
    bilibili_uid = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='B站UID'
    )
    username = models.CharField(
        max_length=100,
        verbose_name='用户名'
    )
    avatar_url = models.CharField(
        max_length=500,
        blank=True,
        default='',
        verbose_name='头像URL'
    )
    fan_badge_level = models.IntegerField(
        default=0,
        verbose_name='粉丝勋章等级',
        help_text='B站粉丝勋章等级，0表示无勋章'
    )
    first_seen_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='首次出现时间',
        help_text='用户首次在直播中被记录的时间'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='创建时间'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='更新时间'
    )

    class Meta:
        db_table = 'livefans_fan_profile'
        verbose_name = '粉丝画像'
        verbose_name_plural = '粉丝画像'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['bilibili_uid']),
            models.Index(fields=['username']),
        ]

    def __str__(self):
        return f'{self.username} ({self.bilibili_uid})'


class LiveAttendance(models.Model):
    """单场直播粉丝出勤记录"""

    fan = models.ForeignKey(
        FanProfile,
        on_delete=models.CASCADE,
        related_name='attendances',
        verbose_name='粉丝'
    )
    livestream = models.ForeignKey(
        'livestream.Livestream',
        on_delete=models.CASCADE,
        related_name='fan_attendances',
        verbose_name='直播场次'
    )
    has_danmaku = models.BooleanField(
        default=False,
        verbose_name='是否发弹幕'
    )
    danmaku_count = models.IntegerField(
        default=0,
        verbose_name='弹幕数量'
    )
    has_gift = models.BooleanField(
        default=False,
        verbose_name='是否投喂礼物'
    )
    has_sc = models.BooleanField(
        default=False,
        verbose_name='是否发SC',
        help_text='醒目留言（Super Chat）'
    )
    has_guard = models.BooleanField(
        default=False,
        verbose_name='是否有大航海',
        help_text='上舰/续舰（大航海/舰长）'
    )
    watch_duration_minutes = models.IntegerField(
        default=0,
        verbose_name='观看时长（分钟）',
        help_text='在直播间的观看时长'
    )
    is_attended = models.BooleanField(
        default=False,
        verbose_name='是否成功出勤',
        help_text='达成任一条件即为出勤：弹幕/礼物/SC/大航海/观看时长'
    )
    first_seen = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='首次检测时间',
        help_text='本场直播中首次被检测到的时间'
    )
    last_seen = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='最后检测时间',
        help_text='本场直播中最后一次被检测到的时间'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='创建时间'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='更新时间'
    )

    class Meta:
        db_table = 'livefans_attendance'
        verbose_name = '粉丝出勤记录'
        verbose_name_plural = '粉丝出勤记录'
        ordering = ['-livestream__date']
        unique_together = ('fan', 'livestream')
        indexes = [
            models.Index(fields=['fan', 'livestream']),
            models.Index(fields=['livestream', '-danmaku_count']),
            models.Index(fields=['is_attended']),
        ]

    def __str__(self):
        return f'{self.fan.username} @ {self.livestream.date}'


class Guard(models.Model):
    """大航海（舰长/提督/总督）用户数据"""

    uid = models.BigIntegerField(
        unique=True,
        verbose_name='用户UID'
    )
    username = models.CharField(
        max_length=100,
        verbose_name='用户名'
    )
    face = models.CharField(
        max_length=500,
        blank=True,
        default='',
        verbose_name='头像URL'
    )
    guard_level = models.IntegerField(
        verbose_name='大航海级别',
        help_text='1=总督, 2=提督, 3=舰长'
    )
    guard_type = models.CharField(
        max_length=20,
        verbose_name='大航海类型'
    )
    medal_name = models.CharField(
        max_length=50,
        blank=True,
        default='',
        verbose_name='粉丝牌名称'
    )
    medal_level = models.IntegerField(
        default=0,
        verbose_name='粉丝牌等级'
    )
    accompany = models.IntegerField(
        default=0,
        verbose_name='陪伴天数'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='创建时间'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='更新时间'
    )

    class Meta:
        db_table = 'livefans_guard'
        verbose_name = '大航海用户'
        verbose_name_plural = '大航海用户'
        ordering = ['guard_level', '-medal_level']
        indexes = [
            models.Index(fields=['guard_level']),
            models.Index(fields=['uid']),
        ]

    def __str__(self):
        return f'{self.username} - {self.guard_type}'
