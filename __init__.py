from os.path import join, dirname

from ovos_plugin_common_play.ocp import MediaType, PlaybackType
from ovos_utils.log import LOG
from ovos_workshop.skills.common_play import OVOSCommonPlaybackSkill, \
    ocp_search, ocp_featured_media
from youtube_archivist import YoutubeMonitor


class RTDocumentariesSkill(OVOSCommonPlaybackSkill):
    def __init__(self):
        super().__init__("RT Documentaries")
        self.skill_icon = self.default_bg = join(dirname(__file__), "ui", "rt_icon.jpg")
        self.supported_media = [MediaType.GENERIC,
                                MediaType.DOCUMENTARY]
        # load video catalog
        self.archive = YoutubeMonitor("RTDocumentaries", logger=LOG, blacklisted_kwords=["subscribe"])

    def initialize(self):
        url = "https://www.youtube.com/user/RTDocumentaries"
        bootstrap = f"https://raw.githubusercontent.com/OpenJarbas/streamindex/main/{self.archive.db.name}.json"
        self.archive.bootstrap_from_url(bootstrap)
        self.archive.monitor(url)
        self.archive.setDaemon(True)
        self.archive.start()

    def match_skill(self, phrase, media_type):
        score = 0
        if self.voc_match(phrase, "music") or media_type == MediaType.DOCUMENTARY:
            score += 10
        if self.voc_match(phrase, "rt_documentaries"):
            score += 80
        return score

    @ocp_search()
    def ocp_rt_documentaries(self, phrase, media_type):
        score = self.match_skill(phrase, media_type)
        if score < 50:
            return
        pl = self.featured_media()[:250]
        yield {
            "match_confidence": score,
            "media_type": MediaType.DOCUMENTARY,
            "playlist": pl,
            "playback": PlaybackType.VIDEO,
            "skill_icon": self.skill_icon,
            "skill_id": self.skill_id,
            "image": self.skill_icon,
            "bg_image": self.default_bg,
            "title": "RussiaToday Documentaries (Playlist)"
        }

    @ocp_featured_media()
    def featured_media(self, num_entries=250):
        return [
                   {
                       "match_confidence": 90,
                       "media_type": MediaType.DOCUMENTARY,
                       "uri": "youtube//" + entry["url"],
                       "playback": PlaybackType.VIDEO,
                       "image": entry["thumbnail"],
                       "bg_image": self.default_bg,
                       "skill_icon": self.skill_icon,
                       "skill_id": self.skill_id,
                       "title": entry["title"]
                   } for entry in self.archive.sorted_entries()
               ][:num_entries]


def create_skill():
    return RTDocumentariesSkill()
