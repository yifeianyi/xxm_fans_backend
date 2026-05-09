from django.db import models


class SongRecordLike(models.Model):
    song_record_id = models.IntegerField(db_index=True)
    ip_address = models.CharField(max_length=64)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['song_record_id']),
            models.Index(fields=['ip_address', 'song_record_id']),
            models.Index(fields=['created_at']),
        ]
        unique_together = [['song_record_id', 'ip_address']]

    def __str__(self):
        return f"like #{self.song_record_id} @ {self.created_at}"
