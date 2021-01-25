from flask import redirect, request, session


class Root_URL():
    endpoints = ["/"]
    endpoint_name = "page_root_html"
    endpoint_methods = ["GET", "POST"]

    def __init__(self, fhdhr):
        self.fhdhr = fhdhr

    def __call__(self, *args):
        return self.get(*args)

    def get(self, *args):

        user_agent = request.headers.get('User-Agent')

        # Client Devices Discovering Device Information
        if not user_agent or session["is_plexmediaserver"]:

            # Plex Remote Media Grabber redirect
            if self.fhdhr.config.dict["rmg"]["enabled"] and session["is_plexmediaserver"]:
                return redirect("/rmg")

            # Client Device is looking for HDHR type device
            else:
                return redirect("/hdhr/device.xml")

        # Anything Else is likely a Web Browser
        else:
            return redirect("/index")
