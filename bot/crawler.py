from common import *
from use_mysql import UseMySQL


class Crawler:
    @staticmethod
    async def register_crawl(target_url: str, method: str):
        await UseMySQL.run_sql(
            "INSERT INTO crawls (target_url, method, service) VALUES (%s, %s, %s)",
            (target_url, method, SERVICE_NAME),
        )

    @staticmethod
    async def register_api_status_code(status_code: int, method: str):
        latest_crawl_id = await UseMySQL.run_sql(
            "SELECT id FROM crawls WHERE method = %s AND service = %s ORDER BY created_at DESC LIMIT 1",
            (method, SERVICE_NAME),
        )
        if not latest_crawl_id:
            return
        await UseMySQL.run_sql(
            "INSERT INTO api_status_codes (crawl_id, status_code) VALUES (%s, %s)",
            (latest_crawl_id[0], status_code),
        )

    @classmethod
    async def get_new_videos(cls):
        try:
            youtube = build(
                "youtube", "v3", developerKey=YOUTUBE_API_KEY, cache_discovery=False
            )
            response = (
                youtube.search()
                .list(
                    part="snippet",
                    channelId=YOUTUBE_CHANNEL_ID,
                    maxResults=5,
                    order="date",
                    type="video",
                )
                .execute()
            )
            target_url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&channelId={YOUTUBE_CHANNEL_ID}&maxResults=5&order=date&type=video"
            await cls.register_crawl(
                target_url,
                "YouTube_Data_API",
            )
            if not response or "items" not in response:
                await cls.register_api_status_code(400, "YouTube_Data_API")
                return
            await cls.register_api_status_code(200, "YouTube_Data_API")
            video_urls = []
            for item in response["items"]:
                video_url = f"https://www.youtube.com/watch?v={item['id']['videoId']}"
                sent = (
                    await UseMySQL.run_sql(
                        "SELECT url FROM sent_urls WHERE service = %s AND url = %s",
                        (SERVICE_NAME, video_url),
                    )
                    != []
                )
                if sent:
                    continue
                title = item["snippet"]["title"]
                await UseMySQL.run_sql(
                    "INSERT INTO sent_urls (url, title, category, service) VALUES (%s,  %s, %s, %s)",
                    (video_url, title, "new_video", SERVICE_NAME),
                )
                video_urls.append(video_url)
            return video_urls
        except Exception as e:
            await write_log_message(f"{e}", "ERROR")
            return "ERROR"
