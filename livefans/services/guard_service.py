from django.core.paginator import Paginator

from ..models import Guard


class GuardService:

    @staticmethod
    def get_guards_by_type(guard_level: int, page: int = 1, page_size: int = 20):
        queryset = Guard.objects.filter(guard_level=guard_level).order_by("-accompany", "-medal_level")
        paginator = Paginator(queryset, page_size)
        page_obj = paginator.get_page(page)
        return list(page_obj.object_list.values(
            "uid", "username", "face", "guard_level", "guard_type",
            "medal_name", "medal_level", "accompany",
        )), paginator.count

    @staticmethod
    def get_all_guards(page: int = 1, page_size: int = 20):
        queryset = Guard.objects.all().order_by("guard_level", "-accompany", "-medal_level")
        paginator = Paginator(queryset, page_size)
        page_obj = paginator.get_page(page)
        return list(page_obj.object_list.values(
            "uid", "username", "face", "guard_level", "guard_type",
            "medal_name", "medal_level", "accompany",
        )), paginator.count
