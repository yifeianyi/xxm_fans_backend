from django.db import models

# Create your models here.
class Style(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Songs(models.Model):
    song_name = models.CharField(max_length=200)
    singer = models.CharField(max_length=200, blank=True, null=True)
    last_performed = models.DateField(blank=True, null=True)
    perform_count = models.IntegerField(default=0)
    language = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return self.song_name


class SongRecord(models.Model):
    song = models.ForeignKey(Songs, on_delete=models.CASCADE, related_name='records')
    performed_at = models.DateField()
    url = models.URLField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    cover_url = models.CharField(max_length=300, blank=True, null=True)
    def __str__(self):
        return f"{self.song.song_name} @ {self.performed_at}"


class SongStyle(models.Model):
    song = models.ForeignKey(Songs, on_delete=models.CASCADE)
    style = models.ForeignKey(Style, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("song", "style")

    def __str__(self):
        return f"{self.song.song_name} - {self.style.name}"


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