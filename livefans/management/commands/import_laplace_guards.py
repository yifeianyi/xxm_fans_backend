import json
import os

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction

from livefans.models import Guard


class Command(BaseCommand):
    help = "从 laplace_guards JSON 文件导入大航海用户数据"

    def add_arguments(self, parser):
        parser.add_argument(
            "--json-path",
            type=str,
            help="JSON 文件路径，默认使用 spider/ 下的最新文件",
        )

    def handle(self, *args, **options):
        json_path = options.get("json_path")
        if not json_path:
            spider_dir = os.path.join(settings.PROJECT_ROOT, "spider")
            candidates = sorted(
                [f for f in os.listdir(spider_dir) if f.startswith("laplace_guards_") and f.endswith(".json")],
                reverse=True,
            )
            if not candidates:
                self.stderr.write("未找到 laplace_guards JSON 文件，请用 --json-path 指定")
                return
            json_path = os.path.join(spider_dir, candidates[0])

        self.stdout.write(f"读取文件: {json_path}")
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        guards = data.get("guards", [])
        if not guards:
            self.stderr.write("文件中没有 guard 数据")
            return

        created = 0
        updated = 0
        total = len(guards)

        with transaction.atomic():
            existing_uids = set(Guard.objects.values_list("uid", flat=True))
            to_create = []
            to_update = []

            for g in guards:
                obj = Guard(
                    uid=g["uid"],
                    username=g["username"],
                    face=g["face"],
                    guard_level=g["guard_level"],
                    guard_type=g["guard_type"],
                    medal_name=g["medal_name"],
                    medal_level=g["medal_level"],
                    accompany=g.get("accompany", 0),
                )
                if g["uid"] in existing_uids:
                    to_update.append(obj)
                else:
                    to_create.append(obj)

            if to_create:
                Guard.objects.bulk_create(to_create, batch_size=500)
                created = len(to_create)

            if to_update:
                for obj in to_update:
                    Guard.objects.filter(uid=obj.uid).update(
                        username=obj.username,
                        face=obj.face,
                        guard_level=obj.guard_level,
                        guard_type=obj.guard_type,
                        medal_name=obj.medal_name,
                        medal_level=obj.medal_level,
                        accompany=obj.accompany,
                    )
                updated = len(to_update)

        self.stdout.write(self.style.SUCCESS(
            f"导入完成: 新增 {created}, 更新 {updated}, 总计 {total}"
        ))
