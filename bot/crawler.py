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
    async def get_new_videos():
        try:
            youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)
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
            if not response or "items" not in response:
                return
            target_url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&channelId={YOUTUBE_CHANNEL_ID}&maxResults=5&order=date&type=video"
            await Crawler.register_crawl(
                target_url,
                "YouTube_Data_API",
            )
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
            print(e)
            return "ERROR"
