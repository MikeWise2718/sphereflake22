import omni.ui as ui
from ._widgets import BaseTab
from .sfcontrols import SfControls
from .sfwindow import SfWindow
import os

import omni.client
import omni.usd_resolver

# Internal imports
import omni.kit.collaboration.channel_manager as cm
# import omni.kit.layers.live_session_channel_manager as lscm


class LiveSessionInfo:
    """ Live Session Info class
    This class attempts to collect all of the logic around the live session file paths and URLs.
    It should be first instantiated with the stage URL (omniverse://server/folder/stage.usd), then
    get_session_folder_path_for_stage() can be used to list the available sessions.

    Once a session is selected, set_session_name() will finish the initialization of all of the paths
    and the other methods can be used.

    In the folder that contains the USD to be live-edited, there exists this folder structure:
    <.live> / < my_usd_file.live> / <session_name> / root.live

    get_session_folder_path_for_stage:  <stage_folder> / <.live> / < my_usd_file.live>
    get_live_session_folder_path:       <stage_folder> / <.live> / < my_usd_file.live> / <session_name>
    get_live_session_url:               <stage_folder> / <.live> / < my_usd_file.live> / <session_name> / root.live
    get_live_session_toml_url:          <stage_folder> / <.live> / < my_usd_file.live> / <session_name> / __session__.toml
    get_message_channel_url:            <stage_folder> / <.live> / < my_usd_file.live> / <session_name> / __session__.channel
    """
    def __init__(self, stage_url: str):
        self.OMNIVERSE_CHANNEL_FILE_NAME = "__session__.channel"
        self.LIVE_SUBFOLDER = "/.live"
        self.LIVE_SUBFOLDER_SUFFIX = ".live"
        self.DEFAULT_LIVE_FILE_NAME = "root.live"
        self.SESSION_TOML_FILE_NAME = "__session__.toml"

        self.stage_url = stage_url
        self.live_file_url = None
        self.channel_url = None
        self.toml_url = None
        self.session_name = None
        self.omni_url = omni.client.break_url(self.stage_url)
        # construct the folder that would contain sessions - <.live> / < my_usd_file.live> / <session_name> / root.live
        self.omni_session_folder_path = os.path.dirname(self.omni_url.path) + self.LIVE_SUBFOLDER + "/" + self.get_stage_file_name() + self.LIVE_SUBFOLDER_SUFFIX
        self.session_folder_string = omni.client.make_url(self.omni_url.scheme, self.omni_url.user, self.omni_url.host, self.omni_url.port, self.omni_session_folder_path)

    def get_session_folder_path_for_stage(self):
        return self.session_folder_string

    def set_session_name(self, session_name):
        self.session_name = session_name

    def get_live_session_folder_path(self):
        return self.omni_session_folder_path + "/" + self.session_name + self.LIVE_SUBFOLDER_SUFFIX

    def get_stage_file_name(self):
        # find the stage file's root name
        usd_file_root = os.path.splitext(os.path.basename(self.omni_url.path))[0]
        return usd_file_root

    def get_live_session_url(self):
        live_session_path = self.get_live_session_folder_path() + "/" + self.DEFAULT_LIVE_FILE_NAME
        live_session_url = omni.client.make_url(self.omni_url.scheme, self.omni_url.user, self.omni_url.host, self.omni_url.port, live_session_path)
        return live_session_url

    def get_live_session_toml_url(self):
        live_session_toml_path = self.get_live_session_folder_path() + "/" + self.SESSION_TOML_FILE_NAME
        live_session_url = omni.client.make_url(self.omni_url.scheme, self.omni_url.user, self.omni_url.host, self.omni_url.port, live_session_toml_path)
        return live_session_url

    def get_message_channel_url(self):
        live_session_channel_path = self.get_live_session_folder_path() + "/" + self.OMNIVERSE_CHANNEL_FILE_NAME
        live_session_url = omni.client.make_url(self.omni_url.scheme, self.omni_url.user, self.omni_url.host, self.omni_url.port, live_session_channel_path)
        return live_session_url


g_live_session_channel_manager = None


def list_session_users():
    global g_live_session_channel_manager
    # users are cm.PeerUser types
    if g_live_session_channel_manager is None:
        return ["Live session not initialized"]
    users: set(cm.PeerUser)
    users = g_live_session_channel_manager.get_users()
    txtlst = ["Listing session users: "]
    if len(users) == 0:
        txtlst.append("No other users in session")
    for user in users:
        txtlst.append(f" - {user.user_name}[{user.from_app}")
    return txtlst


class SfcTabSessionInfo(BaseTab):
    sfw: SfWindow
    sfc: SfControls

    def __init__(self, sfw: SfWindow):
        super().__init__("Session")
        self.sfw = sfw
        self.sfc = sfw.sfc
        # print("SfcTabOptions.build_fn {sfc}")

    def GetInfoText(self):
        txt = "Session Info 1\nSession Info 2\nSession Info 3\n"
        txt += "Session Info 4\nSession Info 5\nSession Info 6\n"
        txt += "Session Info 7\nSession Info 8\nSession Info 9\n"
        return txt

    def build_fn(self):
        # print("SfcTabOptions.build_fn (trc)")
        sfw = self.sfw
        sfc = self.sfc # noqa : F841

        with ui.VStack(style={"margin": sfw.marg}, height=250):
            with ui.ScrollingFrame():
                with ui.VStack(style={"margin": sfw.marg}):

                    with ui.HStack():
                        txtlst = list_session_users()
                        txt = "/n".join(txtlst)
                        ui.Label(txt, word_wrap=True)
                    sfw.optstartupframe = ui.CollapsableFrame("Startup", collapsed=sfw.docollapse_optremoteframe)

        with sfw.optstartupframe:
            with ui.VStack(style={"margin": sfw.marg}):
                with ui.HStack():
                    ui.Label("Load USD File on Startup: ")
                    sfw.doloadusd_checkbox = ui.CheckBox(model=sfw.doloadusd_checkbox_model,
                                                         width=40, height=10, name="loadusd", visible=True)
                with ui.HStack():
                    ui.Label("USD URL:")
                    sfw.doloadusd_checkbox = ui.StringField(model=sfw.doloadusd_url_model,
                                                            width=400, height=20, visible=True)
                with ui.HStack():
                    ui.Label("Start USD Session on Startup: ")
                    sfw.doloadusd_session_checkbox = ui.CheckBox(model=sfw.doloadusd_session_checkbox_model,
                                                                 width=40, height=10, name="loadusd", visible=True)
                with ui.HStack():
                    ui.Label("Session Name:")
                    sfw.doloadusd_sessionname = ui.StringField(model=sfw.doloadusd_sessionname_model,
                                                               width=400, height=20, visible=True)
