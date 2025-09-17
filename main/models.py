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