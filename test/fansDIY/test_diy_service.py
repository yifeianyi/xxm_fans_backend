"""
粉丝二创服务测试 - Commit #2
覆盖：作品列表 select_related 优化
"""
from django.test import TestCase

from fansDIY.models import Collection, Work
from fansDIY.services import DIYService


class DIYWorkQueryTest(TestCase):
    """粉丝二创作品查询测试"""

    def setUp(self):
        self.collections = []
        for i in range(3):
            collection = Collection.objects.create(
                name=f"合集{i}",
                position=i,
                display_order=i,
            )
            self.collections.append(collection)
            for j in range(5):
                Work.objects.create(
                    collection=collection,
                    title=f"作品{i}-{j}",
                    author=f"作者{j}",
                    position=j,
                    display_order=j,
                )

    def test_works_list_query_count_constant(self):
        """作品列表查询数应 ≤ 2（1 次 works + 1 次 count）"""
        with self.assertNumQueries(2):
            result = DIYService.get_works(page=1, page_size=10)

        self.assertEqual(result["page_size"], 10)
        self.assertEqual(len(result["results"]), 10)

    def test_works_list_includes_collection_info(self):
        """作品列表应包含完整的 collection 信息"""
        result = DIYService.get_works(page=1, page_size=10)
        self.assertIn("results", result)
        self.assertGreaterEqual(len(result["results"]), 1)

        for work in result["results"]:
            self.assertIn("collection", work)
            self.assertIn("id", work["collection"])
            self.assertIn("name", work["collection"])
            # 验证 collection name 与数据库一致
            collection = Collection.objects.get(id=work["collection"]["id"])
            self.assertEqual(work["collection"]["name"], collection.name)
