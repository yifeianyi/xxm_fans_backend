from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import SongRecord, Songs

def update_song_statistics(song):
    records = song.records.all()
    song.perform_count = records.count()
    song.last_performed = records.order_by('-performed_at').first().performed_at if records.exists() else None
    song.save()

@receiver(post_save, sender=SongRecord)
def update_song_on_save(sender, instance, **kwargs):
    update_song_statistics(instance.song)

@receiver(post_delete, sender=SongRecord)
def update_song_on_delete(sender, instance, **kwargs):
    update_song_statistics(instance.song)
