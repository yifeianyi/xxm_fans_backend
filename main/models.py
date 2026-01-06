from django.db import models

# Create your models here.
class Style(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name = "曲风表"
        verbose_name_plural = "曲风表"
        ordering = ['name']

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name = "标签表"
        verbose_name_plural = "标签表"
        ordering = ['name']

    def __str__(self):
        return self.name


class Songs(models.Model):
    song_name = models.CharField(max_length=200)
    singer = models.CharField(max_length=200, blank=True, null=True)
    last_performed = models.DateField(blank=True, null=True)
    perform_count = models.IntegerField(default=0)
    language = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        verbose_name = "歌单"
        verbose_name_plural = "歌单"
        ordering = ['song_name']

    def __str__(self):
        return self.song_name

    def get_search_result(self):
        return f"{self.song_name} - {self.singer if self.singer else '未知歌手'}"
    
    @property
    def styles(self):
        """获取歌曲的曲风列表"""
        return [song_style.style.name for song_style in self.songstyle_set.all()]
        
    @property
    def tags(self):
        """获取歌曲的标签列表"""
        return [song_tag.tag.name for song_tag in self.songtag_set.all()]


class SongRecord(models.Model):
    song = models.ForeignKey(Songs, on_delete=models.CASCADE, related_name='records')
    performed_at = models.DateField()
    url = models.URLField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    cover_url = models.CharField(max_length=300, blank=True, null=True)


    class Meta:
        verbose_name = "演唱记录"
        verbose_name_plural = "演唱记录"
        ordering = ['-performed_at']
    def __str__(self):
        return f"{self.song.song_name} @ {self.performed_at}"


class SongStyle(models.Model):
    song = models.ForeignKey(Songs, on_delete=models.CASCADE)
    style = models.ForeignKey(Style, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("song", "style")
        verbose_name = "歌曲曲风"
        verbose_name_plural = "歌曲曲风"

    def __str__(self):
        return f"{self.song.song_name} - {self.style.name}"


class SongTag(models.Model):
    song = models.ForeignKey(Songs, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("song", "tag")
        verbose_name = "歌曲标签"
        verbose_name_plural = "歌曲标签"

    def __str__(self):
        return f"{self.song.song_name} - {self.tag.name}"


class ViewBaseMess(models.Model):
    name = models.CharField(max_length=255)
    bvid = models.CharField(max_length=100)
    pubtime = models.DateTimeField()
    pic_path = models.CharField(max_length=500)

    def __str__(self):
        return f"{self.name} ({self.bvid})"


class ViewRealTimeInformation(models.Model):
    view = models.OneToOneField(ViewBaseMess, on_delete=models.CASCADE, primary_key=True, related_name='real_time_info')
    play = models.IntegerField(default=0)
    like = models.IntegerField(default=0)
    coin = models.IntegerField(default=0)
    share = models.IntegerField(default=0)
    fetchtime = models.DateTimeField()

    def __str__(self):
        return f"RT info for {self.view.name} at {self.fetchtime}"


class Recommendation(models.Model):
    content = models.TextField(help_text="推荐语内容")
    recommended_songs = models.ManyToManyField('Songs', blank=True, help_text="推荐的歌曲")
    is_active = models.BooleanField(default=True, help_text="是否激活显示")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "推荐语"
        verbose_name_plural = "推荐语"

    def __str__(self):
        return f"推荐语: {self.content[:50]}..." if len(self.content) > 50 else f"推荐语: {self.content}"


class SiteSettings(models.Model):
    favicon = models.ImageField(upload_to='', blank=True, null=True, verbose_name="网站图标")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "网站设置"
        verbose_name_plural = "网站设置"

    def __str__(self):
        return "网站设置"
        
    def favicon_url(self):
        """返回favicon的URL路径"""
        if self.favicon:
            return self.favicon.url
        return None


# 数据分析相关模型
class WorkStatic(models.Model):
    """作品静态信息表"""
    platform = models.CharField(max_length=50, verbose_name="平台")
    work_id = models.CharField(max_length=100, verbose_name="作品ID")
    title = models.CharField(max_length=500, verbose_name="标题")
    author = models.CharField(max_length=200, verbose_name="作者")
    publish_time = models.DateTimeField(verbose_name="发布时间")
    cover_url = models.URLField(max_length=500, blank=True, null=True, verbose_name="封面URL")
    is_valid = models.BooleanField(default=True, verbose_name="投稿是否有效")

    class Meta:
        verbose_name = "作品静态信息"
        verbose_name_plural = "作品静态信息"
        unique_together = ("platform", "work_id")
        ordering = ['-publish_time']

    def __str__(self):
        return f"{self.title} - {self.author}"


class WorkMetricsHour(models.Model):
    """作品小时级指标表"""
    platform = models.CharField(max_length=50, verbose_name="平台")
    work_id = models.CharField(max_length=100, verbose_name="作品ID")
    crawl_time = models.DateTimeField(verbose_name="爬取时间")
    view_count = models.IntegerField(default=0, verbose_name="播放数")
    like_count = models.IntegerField(default=0, verbose_name="点赞数")
    coin_count = models.IntegerField(default=0, verbose_name="投币数")
    favorite_count = models.IntegerField(default=0, verbose_name="收藏数")
    danmaku_count = models.IntegerField(default=0, verbose_name="弹幕数")
    comment_count = models.IntegerField(default=0, verbose_name="评论数")
    session_id = models.IntegerField(verbose_name="会话ID")
    ingest_time = models.DateTimeField(auto_now_add=True, verbose_name="入库时间")

    class Meta:
        verbose_name = "作品小时指标"
        verbose_name_plural = "作品小时指标"
        ordering = ['-crawl_time']
        indexes = [
            models.Index(fields=['platform', 'work_id']),
            models.Index(fields=['crawl_time']),
            models.Index(fields=['session_id']),
        ]

    def __str__(self):
        return f"{self.work_id} @ {self.crawl_time}"


class CrawlSession(models.Model):
    """爬取会话表"""
    source = models.CharField(max_length=50, verbose_name="数据源")
    node_id = models.CharField(max_length=100, verbose_name="节点ID")
    start_time = models.DateTimeField(verbose_name="开始时间")
    end_time = models.DateTimeField(blank=True, null=True, verbose_name="结束时间")
    total_work_count = models.IntegerField(default=0, verbose_name="总作品数")
    success_count = models.IntegerField(default=0, verbose_name="成功数")
    fail_count = models.IntegerField(default=0, verbose_name="失败数")
    note = models.TextField(blank=True, null=True, verbose_name="备注")

    class Meta:
        verbose_name = "爬取会话"
        verbose_name_plural = "爬取会话"
        ordering = ['-start_time']

    def __str__(self):
        return f"{self.source} - {self.node_id} @ {self.start_time}"