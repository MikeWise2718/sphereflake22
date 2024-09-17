# import omni.kit.commands as okc
# import omni.usd
import os
import omni.client


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


def fish_out_session_name(stage):
    slayer = stage.GetSessionLayer()
    slayersubs = slayer.GetLoadedLayers()
    for sl in slayersubs:
        if sl.identifier.endswith(".live"):
            chunks = sl.identifier.split("/")
            session_name = chunks[-2].split(".")[0]
            return session_name
    return None
