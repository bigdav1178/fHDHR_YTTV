import datetime


class OriginEPG():

    def __init__(self, fhdhr):
        self.fhdhr = fhdhr

    def get_content_thumbnail(self, content_id):
        return ("https://i.ytimg.com/vi/%s/maxresdefault.jpg" % (str(content_id)))

    def update_epg(self, fhdhr_channels):
        programguide = {}

        timestamps = []
        xtimestart = datetime.datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
        xtimeend = xtimestart + datetime.timedelta(days=6)
        xtime = datetime.datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
        while xtime <= xtimeend:
            timestampdict = {
                            "time_start": xtime.timestamp(),
                            "time_end": (xtime + datetime.timedelta(hours=1)).timestamp(),
                            }
            xtime = xtime + datetime.timedelta(hours=1)
            timestamps.append(timestampdict)

        for fhdhr_id in list(fhdhr_channels.list.keys()):
            chan_obj = fhdhr_channels.list[fhdhr_id]

            if str(chan_obj.number) not in list(programguide.keys()):
                programguide[str(chan_obj.number)] = chan_obj.epgdict

            for timestamp in timestamps:
                clean_prog_dict = {
                                    "time_start": timestamp['time_start'],
                                    "time_end": timestamp['time_end'],
                                    "duration_minutes": 60,
                                    "thumbnail": self.get_content_thumbnail(chan_obj.dict["origin_id"]),
                                    "title": fhdhr_channels.origin.video_reference[chan_obj.dict["origin_id"]]["title"],
                                    "sub-title": "Unavailable",
                                    "description": fhdhr_channels.origin.video_reference[chan_obj.dict["origin_id"]]["description"],
                                    "rating": "N/A",
                                    "episodetitle": None,
                                    "releaseyear": None,
                                    "genres": [],
                                    "seasonnumber": None,
                                    "episodenumber": None,
                                    "isnew": False,
                                    "id": str(chan_obj.dict["origin_id"]) + "_" + str(timestamp['time_start']).split(" ")[0],
                                    }

                if not any(d['id'] == clean_prog_dict['id'] for d in programguide[str(chan_obj.number)]["listing"]):
                    programguide[str(chan_obj.number)]["listing"].append(clean_prog_dict)

        return programguide
