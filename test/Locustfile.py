from locust import HttpUser, task, between
import random
import time

class FansHomeUser(HttpUser):
    wait_time = between(1, 3)  # 基础操作间隔

    @task
    def user_journey(self):
        # 1. 歌单页（必访问，多页停留）
        for _ in range(random.randint(1, 3)):  # 模拟翻页 1-3 次
            page = random.choices([1, 2, 3, 4, 5], weights=[40, 30, 15, 10, 5])[0]
            limit = 20
            ordering = random.choice(["", "singer", "last_performed", "perform_count"])
            q = random.choice(["","", "周深", "", "林俊杰"])
            songs_resp = self.client.get(
                "/api/songs/",
                params={"page": page, "limit": limit, "ordering": ordering, "q": q},
                name="songs_list"
            )
            time.sleep(random.uniform(1, 2))  # 模拟用户停留

        # 2. 演唱记录（50% 概率，可能点 1-2 次）
        if random.random() < 0.5 and songs_resp.status_code == 200:
            results = songs_resp.json().get("results", [])
            for _ in range(random.randint(1, 2)):
                if results:
                    song_id = random.choice(results)["id"]
                    self.client.get(
                        f"/api/songs/{song_id}/records/",
                        name="song_records"
                    )
                    time.sleep(random.uniform(1, 2))

        # 3. 热歌榜（必访问，可能切换 1-2 次范围）
        for _ in range(random.randint(1, 2)):
            range_choice = random.choices(
                ["all", "1m", "3m", "1y"],
                weights=[20, 40, 30, 10]
            )[0]
            self.client.get(
                "/api/top_songs/",
                params={"range": range_choice, "limit": 20},
                name="top_songs"
            )
            time.sleep(random.uniform(1, 2))

        # 4. 合集列表（60% 概率，翻页 1-2 次）
        if random.random() < 0.6:
            for _ in range(random.randint(1, 2)):
                collections_resp = self.client.get(
                    "/api/footprint/collections/",
                    params={"page": random.randint(1, 3), "limit": 20},
                    name="collections"
                )
                time.sleep(random.uniform(1, 2))

            # 5. 合集详情（50% 概率）
            if random.random() < 0.5 and collections_resp.status_code == 200:
                collections = collections_resp.json().get("results", [])
                if collections:
                    collection_id = random.choice(collections)["id"]
                    self.client.get(
                        f"/api/footprint/collections/{collection_id}/",
                        name="collection_detail"
                    )
                    time.sleep(random.uniform(1, 2))

                    # 6. 作品列表（进入合集详情后，70% 概率再点作品）
                    if random.random() < 0.7:
                        self.client.get(
                            "/api/footprint/works/",
                            params={"collection": collection_id, "limit": 10},
                            name="collection_works"
                        )
                        time.sleep(random.uniform(1, 2))
