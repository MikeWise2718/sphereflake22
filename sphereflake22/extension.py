import omni.ext  # this needs to be included in an extension's extension.py
from .ovut import write_out_syspath, write_out_path
from .sfgen.sfut import MatMan
from .sfgen.sphereflake import SphereMeshFactory, SphereFlakeFactory
from .sfcontrols import SfControls
from .sfwindow import SfWindow
import omni.kit.extensions
import carb
import carb.events
import time
from pxr import Usd


# Omni imports
# import omni.client
# import omni.usd_resolver

# import os
# import contextlib
# @contextlib.asynccontextmanager

update_count = -1
start_time = time.time()
last_update_time = start_time
triggered_show = False
initialized_objects = False
gap = 1.0

_instance_handle: omni.ext.IExt = None


def on_update_event(e: carb.events.IEvent):
    global update_count, last_update_time, triggered_show, start_time, instance_handle, gap
    update_count += 1
    # if update_count % 50 == 0:
    #     print(f"Update: {e.payload} count: {update_count} (trc)")
    elap = time.time() - last_update_time
    if elap > gap:
        last_update_time = time.time()
        totelap = time.time() - start_time
        # stage = omni.usd.get_context().get_stage()
        # stagewd = stage if stage is not None else "None"
        # print(f"on_update_event {update_count} {totelap:.3f}: typ:{e.type} pay:{e.payload} elap: {elap:.3f} stage:{stagewd} (trc)")
        if not triggered_show and totelap > 10:
            if _instance_handle is not None and _instance_handle._sfw is not None:
                print("Triggering ShowTheDamnWindow (trc)")
                _instance_handle._sfw.ShowTheDamnWindow()
                _instance_handle._sfw.DockWindow()
                triggered_show = True
                gap = 5.0


def on_stage_event(e: carb.events.IEvent):
    global initialized_objects, instance_handle, update_count, start_time
    totelap = time.time() - start_time
    # print(f"on_stage_event {update_count} {totelap:.3f} typ:{e.type} pay:{e.payload} (trc1)")
    if not initialized_objects:
        stage = omni.usd.get_context().get_stage()
        if stage is not None:
            _instance_handle.InitializeObjects()
            print("Initializing objectsw (trc)")
            initialized_objects = True


# Any class derived from `omni.ext.IExt` in top level module (defined in `python.modules` of `extension.toml`) will be
# instantiated when extension gets enabled and `on_startup(ext_id)` will be called. Later when extension gets disabled
# on_shutdown() is called.
class SphereflakeBenchmarkExtension(omni.ext.IExt):
    # ext_id is current extension id. It can be used with extension manager to query additional information, like where
    # this extension is located on filesystem.
    _window_sfcon = None
    _matman: MatMan = None
    _smf: SphereMeshFactory = None
    _sff: SphereFlakeFactory = None
    _sfc: SfControls = None
    _sfw: SfWindow = None
    _settings = None
    _stage: Usd.Stage = None

    def WriteOutPathAndSysPath(self, basename="d:/nv/ov/sphereflake_benchmark"):
        write_out_syspath(f"{basename}_syspath.txt")
        write_out_path(f"{basename}_path.txt")

    def setup_event_handlers(self):
        update_stream = omni.kit.app.get_app().get_update_event_stream()
        self._sub1 = update_stream.create_subscription_to_pop(on_update_event, name="SFB_UpdateSub")

        stage_stream = omni.usd.get_context().get_stage_event_stream()
        self._sub2 = stage_stream.create_subscription_to_pop(on_stage_event, name="SFB_StageSub")
        print("Setup on_stage_event handler")

    def InitializeObjects(self):
        self._stage = omni.usd.get_context().get_stage()

        # sesslayer = self._stage.GetSessionLayer()
        # rootlayer = self._stage.GetRootLayer()
        # print(f"Sesslayer: {sesslayer} (trc)")
        # print(f"Rootlayer: {rootlayer} (trc)")

        print(f"SphereflakeBenchmarkExtension on_startup - stage:{self._stage} (trc)")
        self._stageid = omni.usd.get_context().get_stage_id()
        # pid = os.getpid()

        # Write out syspath and path
        # self.WriteOutPathAndSysPath()

        # Model objects
        self._matman = MatMan(self._stage)
        self._smf = SphereMeshFactory(self._stage, self._matman)
        self._sff = SphereFlakeFactory(self._stage, self._matman, self._smf)
        self._sff.LoadSettings()

        # Controller objects
        self._sfc = SfControls(self._matman, self._smf, self._sff)
        print("SphereflakeBenchmarkExtension - _sfc assigned (trc)")

        # View objects
        self._sfw = SfWindow(sfc=self._sfc)
        print("SphereflakeBenchmarkExtension - _sfw assigned (trc)")
        self._sfw.DockWindow()
        self._sfw.ShowTheDamnWindow()
        print("SphereflakeBenchmarkExtension - InitialzeObjects done (trc)")

    def on_startup(self, ext_id):
        global _instance_handle
        _instance_handle = self
        print(f"[{ext_id}] SphereflakeBenchmarkExtension on_startup  (trc))")
        self._ext_id = ext_id

        self.setup_event_handlers()

        print("Subscribing to update events")

        print(f"[{self._ext_id}] SphereflakeBenchmarkExtension on_startup - done (trc))")

    def on_shutdown(self):
        global initialized_objects
        try:
            print(f"[{self._ext_id}] SphereflakeBenchmarkExtension on_shutdown objs_inited:{initialized_objects}")
            if initialized_objects:
                if self._sfc is not None:
                    self._sfc.SaveSettings()
                    self._sfc.Close()
                else:
                    carb.log_error(f"on_shutdown - _sfc is Unexpectedly None objs_inited:{initialized_objects}")
                if self._sfw is not None:
                    self._sfw.SaveSettings()
                    self._sfw.destroy()
                else:
                    carb.log_error(f"on_shutdown - _sfw is Unexpectedly None objs_inited:{initialized_objects}")
        except Exception as e:
            carb.log_error(f"on_shutdown - Exception: {e}")
