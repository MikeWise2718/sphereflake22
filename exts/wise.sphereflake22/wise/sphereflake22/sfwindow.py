import omni.ui as ui
from omni.ui import color as clr
from .sfgen.sphereflake import SphereMeshFactory, SphereFlakeFactory
from .sfcontrols import SfControls
from ._widgets import TabGroup
from .ovut import get_setting, save_setting
import carb


class SfcWindow(ui.Window):

    darkgreen = clr("#004000")
    darkblue = clr("#000040")
    darkred = clr("#400000")
    darkyellow = clr("#404000")
    darkpurple = clr("#400040")
    darkcyan = clr("#004040")

    marg = 2

    # Status
    _statuslabel: ui.Label = None
    _memlabel: ui.Label = None

    # Sphereflake params
    prframe: ui.CollapsableFrame = None
    drframe: ui.CollapsableFrame = None
    physcollidersframe: ui.CollapsableFrame = None
    optlogframe: ui.CollapsableFrame = None
    optremoteframe: ui.CollapsableFrame = None
    optstartupframe: ui.CollapsableFrame = None

    docollapse_prframe = False
    docollapse_drframe = False
    docollapse_optlogframe = False
    docollapse_physcollidersframe = False
    docollapse_optremoteframe = False
    docollapse_optstartupframe = False

    _sf_depth_but: ui.Button = None
    _sf_spawn_but: ui.Button = None
    _sf_nlat_but: ui.Button = None
    _sf_nlng_but: ui.Button = None
    _sf_radratio_slider_model: ui.SimpleFloatModel = None

    _genmodebox: ui.ComboBox = None
    _genmodebox_model: ui.SimpleIntModel = None

    _genformbox: ui.ComboBox = None
    _genformbox_model: ui.SimpleIntModel = None

    # Material tab
    _sf_matbox: ui.ComboBox = None
    _sf_matbox_model: ui.SimpleIntModel = None

    _sf_alt_matbox: ui.ComboBox = None
    _sf_alt_matbox_model: ui.SimpleIntModel = None

    _bb_matbox: ui.ComboBox = None
    _bb_matbox_model: ui.SimpleIntModel = None

    _sf_floor_matbox: ui.ComboBox = None
    _sf_floor_matbox_model: ui.SimpleIntModel = None

    # Options
    writelog_checkbox: ui.CheckBox = None
    writelog_checkbox_model: ui.SimpleBoolModel = None
    writelog_seriesname: ui.StringField = None
    writelog_seriesname_model: ui.SimpleStringModel = None

    doremote_checkbox: ui.CheckBox = None
    doremote_checkbox_model: ui.SimpleBoolModel = None
    doremote_type: ui.ComboBox = None
    doremote_type_model: ui.SimpleIntModel = None
    doremote_url: ui.StringField = None
    doremote_url_model: ui.SimpleStringModel = None

    doregister_remote_checkbox: ui.CheckBox = None
    doregister_remote_checkbox_model: ui.SimpleBoolModel = None

    doloadusd_checkbox: ui.CheckBox = None
    doloadusd_checkbox_model: ui.SimpleBoolModel = None
    doloadusd_url: ui.StringField = None
    doloadusd_url_model: ui.SimpleStringModel = None
    doloadusd_session_checkbox: ui.CheckBox = None
    doloadusd_session_checkbox_model: ui.SimpleBoolModel = None
    doloadusd_sessionname: ui.StringField = None
    doloadusd_sessionname_model: ui.SimpleStringModel = None

    # Physic
    addcolliders_checkbox_model: ui.SimpleBoolModel = None

    # state
    sfc: SfControls
    smf: SphereMeshFactory
    sff: SphereFlakeFactory

    def __init__(self, *args, **kwargs):
        self.wintitle = "SphereFlake Controls"
        super().__init__(title=self.wintitle, height=300, width=300,  *args, **kwargs)
        print("SfcWindow.__init__ (trc)")
        # print("SfcWindow.__init__ (trc)")
        self.sfc = kwargs["sfc"]
        self.sfc.sfw = self  # intentionally circular
        self.smf = self.sfc.smf
        self.sff = self.sfc.sff
        self.LoadSettings()
        self.BuildControlModels()
        self.BuildWindow()
        print("Calling sfc.LateInit")
        self.sfc.LateInit()

    def ShowTheDamnWindow(self):
        ui.Workspace.show_window(self.wintitle, True)

    def BuildControlModels(self):
        # models for controls that are used in the logic need to be built outside the build_fn
        # since that will only be called when the tab is selected and displayed

        sfc = self.sfc
        sff = sfc.sff

        # sphereflake params
        self._sf_radratio_slider_model = ui.SimpleFloatModel(sff.p_radratio)
        idx = sff.GetGenModes().index(sff.p_genmode)
        self._genmodebox_model = ui.SimpleIntModel(idx)
        idx = sff.GetGenForms().index(sff.p_genform)
        self._genformbox_model = ui.SimpleIntModel(idx)

        # materials
        matlist = sfc._matkeys
        idx = matlist.index(sff.p_sf_matname)
        self._sf_matbox_model = ui.SimpleIntModel(idx)
        idx = matlist.index(sff.p_sf_alt_matname)
        self._sf_alt_matbox_model = ui.SimpleIntModel(idx)
        idx = matlist.index(sff.p_bb_matname)
        self._bb_matbox_model = ui.SimpleIntModel(idx)
        idx = matlist.index(sfc._current_floor_material_name)
        self._sf_floor_matbox_model = ui.SimpleIntModel(idx)

        # options
        self.writelog_checkbox_model = ui.SimpleBoolModel(sfc.p_writelog)
        self.writelog_seriesname_model = ui.SimpleStringModel(sfc.p_logseriesname)

        self.doremote_checkbox_model = ui.SimpleBoolModel(sfc.p_doremote)
        idx = sfc._remotetypes.index(sfc.p_doremotetype)
        self.doremote_type_model = ui.SimpleIntModel(idx)

        self.doloadusd_checkbox_model = ui.SimpleBoolModel(sfc.p_doloadusd)
        self.doloadusd_session_checkbox_model = ui.SimpleBoolModel(sfc.p_doloadusd_session)
        self.doremote_url_model = ui.SimpleStringModel(sfc.p_doremoteurl)
        self.doloadusd_sessionname_model = ui.SimpleStringModel(sfc.p_doloadusd_sessionname)
        self.doloadusd_url_model = ui.SimpleStringModel(sfc.p_doloadusd_url)

        self.addcolliders_checkbox_model = ui.SimpleBoolModel(sfc.p_addcolliders)

        self.doregister_remote_checkbox_model = ui.SimpleBoolModel(sfc.p_register_endpoint)

    def BuildWindow(self):
        print("SfcWindow.BuildWindow  (trc1)")
        sfc = self.sfc
        sfw = self
        from .sfwintabs import SfcTabMulti, SfcTabSphereFlake, SfcTabShapes, SfcTabMaterials
        from .sfwintabs import SfcTabOptions, SfcTabPhysics
        from .sfwinsess import SfcTabSessionInfo

        with self.frame:
            with ui.VStack():
                t1 = SfcTabMulti(self)
                t2 = SfcTabSphereFlake(self)
                t3 = SfcTabShapes(self)
                t4 = SfcTabMaterials(self)
                t5 = SfcTabOptions(self)
                t6 = SfcTabPhysics(self)
                t7 = SfcTabSessionInfo(self)
                print("Creating Tab Group  (trc1)")
                self.tab_group = TabGroup([t1, t2, t3, t4, t5, t6, t7])
                if self.start_tab_idx is not None:
                    self.tab_group.select_tab(self.start_tab_idx)
                with ui.HStack():
                    ui.Button("Clear Primitives",
                              style={'background_color': self.darkyellow},
                              clicked_fn=lambda: sfc.on_click_clearprims())
                    clkfn = lambda x, y, b, m: sfw.on_click_save_settings(x, y, b, m) # noqa : E731                  
                    ui.Button("Save Settings",
                              style={'background_color': self.darkpurple},
                              mouse_pressed_fn=clkfn)
                self._statuslabel = ui.Label("Status: Ready")
                self._memlabel = ui.Button("Memory tot/used/free", clicked_fn=sfc.UpdateGpuMemory)

    def on_click_setup_code_env(self, x, y, button, modifier):
        from omni.kit.window.extensions import ext_controller
        extid = "omni.kit.window.extensions"
        ext_controller.toggle_autoload(extid, True)
        showit = True if button == 0 else False
        viewwintitle = "Viewport"
        viewhandle = ui._ui.Workspace.get_window(viewwintitle)
        extwintitle = "Extensions"
        exthandle = ui._ui.Workspace.get_window(extwintitle)
        # print(f"Set up environment (trc) exthandle: {exthandle} viewhandle:{viewhandle} showit: {showit}")
        if viewhandle is not None:
            if exthandle is not None:
                exthandle.dock_in(viewhandle, ui._ui.DockPosition.SAME)
        ui.Workspace.show_window(extwintitle, showit)
        # Environment
        brsid0 = "omni.kit.environment.core"
        ext_controller.toggle_autoload(brsid0, True)
        brsid1 = "omni.kit.property.environment"
        ext_controller.toggle_autoload(brsid1, True)
        brsid2 = "omni.kit.window.environment"
        ext_controller.toggle_autoload(brsid2, True)
        envwintitle = "Environments"
        ui.Workspace.show_window(envwintitle, showit)

    def on_click_save_settings(self, x, y, button, modifier):
        self.SaveSettings()
        self.sfc.SaveSettings()
        print("Saved Settings")

    def DockWindow(self, wintitle="Property"):
        # print(f"Docking to {wintitle} (trc)")
        handle = ui._ui.Workspace.get_window(wintitle)
        self.dock_in(handle, ui._ui.DockPosition.SAME)
        self.deferred_dock_in(wintitle, ui._ui.DockPolicy.TARGET_WINDOW_IS_ACTIVE)

    def LoadSettings(self):
        print("SfcWindow.LoadSettings (trc1)")
        self.docollapse_prframe = get_setting("ui_pr_frame_collapsed", False)
        self.docollapse_drframe = get_setting("ui_dr_frame_collapsed", False)
        self.docollapse_physcollidersframe = get_setting("ui_phys_collidersframe", False)
        self.docollapse_optlogframe = get_setting("ui_opt_logframe", False)
        self.docollapse_optremoteframe = get_setting("ui_opt_remoteframe", False)
        self.docollapse_optstartupframe = get_setting("ui_opt_startupframe", False)
        self.start_tab_idx = get_setting("ui_selected_tab", 0)
        print(f"SfcWindow.LoadSettings start_tab_idx:{self.start_tab_idx} (trc1)")
        # print(f"docollapse_prframe: {self.docollapse_prframe} docollapse_drframe: {self.docollapse_drframe}")

    def SaveSettings(self):
        try:
            # print("SfcWindow.SaveSettings")
            if (self.prframe is not None):
                save_setting("ui_pr_frame_collapsed", self.prframe.collapsed)
            if (self.drframe is not None):
                save_setting("ui_dr_frame_collapsed", self.drframe.collapsed)
            if (self.physcollidersframe is not None):
                save_setting("ui_phys_collidersframe", self.physcollidersframe.collapsed)
            if (self.optlogframe is not None):
                save_setting("ui_opt_logframe", self.optlogframe.collapsed)
            if (self.optremoteframe is not None):
                save_setting("ui_opt_remoteframe", self.optremoteframe.collapsed)
            if (self.optstartupframe is not None):
                save_setting("ui_opt_startupframe", self.optstartupframe.collapsed)
            curidx = self.tab_group.get_selected_tab_index()
            save_setting("ui_selected_tab", curidx)
            print(f"SaveSettings - ui_selected_tab:{curidx} (trc1)")
        except Exception as e:
            carb.log_error(f"Exception in SfcWindow.SaveSettings: {e}")
        # print(f"docollapse_prframe: {self.prframe.collapsed} docollapse_drframe: {self.drframe.collapsed}")
