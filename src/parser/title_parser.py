import logging

from parser.analyser import RawParser, DownloadParser
from parser.internet_parser import TMDBParser, BangumiParser
from dataset import MainData
from conf import settings

logger = logging.getLogger(__name__)


class TitleParser:
    def __init__(self):
        self._raw_parser = RawParser()
        self._download_parser = DownloadParser()
        self._tmdb_parser = TMDBParser()

    def raw_parser(self, raw: str):
        return self._raw_parser.analyse(raw)

    def download_parser(self, download_raw, folder_name, season, suffix, method=settings.method):
        return self._download_parser.download_rename(download_raw, folder_name, season, suffix, method)

    def tmdb_parser(self, title: str, season: int):
        try:
            tmdb_info = self._tmdb_parser.tmdb_search(title)
            logger.debug(f"TMDB Matched, title is {tmdb_info.title_zh}")
        except Exception as e:
            logger.warning("Not Matched with TMDB")
            return title, season
        if settings.title_language == "zh":
            official_title = f"{tmdb_info.title_zh}({tmdb_info.year_number})"
        elif settings.title_language == "jp":
            official_title = f"{tmdb_info.title_jp}({tmdb_info.year_number})"
        season = tmdb_info.last_season
        return official_title, season

    def return_dict(self, raw: str) -> MainData:
        try:
            episode = self.raw_parser(raw)
            title_search = episode.title_zh if episode.title_zh != "" else episode.title_en
            if settings.enable_tmdb:
                official_title, season = self.tmdb_parser(title_search, episode.season)
            else:
                official_title = title_search
                season = episode.season
            # TODO TMDB引入
            data = MainData(
                None,
                episode.title_zh,
                episode.title_jp,
                episode.title_en,
                episode.year,
                season,
                "cover_url",
                episode.group,
                episode.resolution,
                episode.source,
                episode.contain,
                settings.not_contain,
                False,
                True if settings.eps_complete and episode.episode > 1 else False,
                0
            )
            logger.debug(f"RAW:{raw} >> {episode.title_en}")
            return data
        except Exception as e:
            logger.debug(e)


if __name__ == '__main__':
    import re
    from conf import DEV_SETTINGS
    settings.init(DEV_SETTINGS)
    T = TitleParser()
    raw = "[Lilith-Raws] 在地下城寻求邂逅是否搞错了什么 / Danmachi S04 - 00 [Baha][WEB-DL][1080p][AVC AAC][CHT][MP4]"
    season = int(re.search(r"\d{1,2}", "S02").group())
    dict = T.return_dict(raw)
    print(dict)
