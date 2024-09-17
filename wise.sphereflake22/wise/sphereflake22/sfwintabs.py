import omni.ui as ui
import asyncio
from ._widgets import BaseTab
from .sfgen.sphereflake import SphereFlakeFactory
from .sfcontrols import SfControls
from .sfwindow import SfWindow


class SfcTabMulti(BaseTab):

    sfw: SfWindow
    sfc: SfControls

    def __init__(self, sfw: SfWindow):
        super().__init__("Multi")
        self.sfw = sfw
        self.sfc = sfw.sfc
        # print(f"SfcTabMulti.init {type(sfc)}")

    def build_fn(self):
        # print("SfcTabMulti.build_fn (trc)")
        sfw: SfWindow = self.sfw
        sfc: SfControls = self.sfc
        sff: SphereFlakeFactory = self.sfw.sff
        # print(f"SfcTabMulti.build_fn {type(sfc)}")
        with ui.VStack(style={"margin": sfw.marg}):
            with ui.VStack():
                with ui.HStack():
                    clkfn = lambda: asyncio.ensure_future(sfc.on_click_multi_sphereflake()) # noqa : E731
                    sfw._msf_spawn_but = ui.Button("Multi ShereFlake",
                                                   style={'background_color': sfw.darkred},
                                                   clicked_fn=clkfn)
                    with ui.VStack(width=200):
                        clkfn = lambda x, y, b, m: sfc.on_click_sfx(x, y, b, m) # noqa : E731
                        sfw._nsf_x_but = ui.Button(f"SF x: {sff.p_nsfx}",
                                                   style={'background_color': sfw.darkblue},
                                                   mouse_pressed_fn=clkfn)
                        clkfn = lambda x, y, b, m: sfc.on_click_sfy(x, y, b, m) # noqa : E731
                        sfw._nsf_y_but = ui.Button(f"SF y: {sff.p_nsfy}",
                                                   style={'background_color': sfw.darkblue},
                                                   mouse_pressed_fn=clkfn)
                        clkfn = lambda x, y, b, m: sfc.on_click_sfz(x, y, b, m) # noqa : E731
                        sfw._nsf_z_but = ui.Button(f"SF z: {sff.p_nsfz}",
                                                   style={'background_color': sfw.darkblue},
                                                   mouse_pressed_fn=clkfn)
                    sfw._tog_bounds_but = ui.Button(f"Bounds:{sfc._bounds_visible}",
                                                    style={'background_color': sfw.darkcyan},
                                                    clicked_fn=sfc.toggle_bounds)
                sfw.prframe = ui.CollapsableFrame("Partial Renders", collapsed=sfw.docollapse_prframe)
                with sfw.prframe:
                    with ui.VStack():
                        sfw._partial_render_but = ui.Button(f"Partial Render {sff.p_partialRender}",
                                                            style={'background_color': sfw.darkcyan},
                                                            clicked_fn=sfc.toggle_partial_render)
                        with ui.HStack():
                            clkfn = lambda x, y, b, m: sfc.on_click_parital_sfsx(x, y, b, m) # noqa : E731
                            sfw._part_nsf_sx_but = ui.Button(f"SF partial sx: {sff.p_partial_ssfx}",
                                                             style={'background_color': sfw.darkblue},
                                                             mouse_pressed_fn=clkfn)
                            clkfn = lambda x, y, b, m: sfc.on_click_parital_sfsy(x, y, b, m) # noqa : E731
                            sfw._part_nsf_sy_but = ui.Button(f"SF partial sy: {sff.p_partial_ssfy}",
                                                             style={'background_color': sfw.darkblue},
                                                             mouse_pressed_fn=clkfn)
                            clkfn = lambda x, y, b, m: sfc.on_click_parital_sfsz(x, y, b, m) # noqa : E731
                            sfw._part_nsf_sz_but = ui.Button(f"SF partial sz: {sff.p_partial_ssfz}",
                                                             style={'background_color': sfw.darkblue},
                                                             mouse_pressed_fn=clkfn)
                        with ui.HStack():
                            clkfn = lambda x, y, b, m: sfc.on_click_parital_sfnx(x, y, b, m) # noqa : E731
                            sfw._part_nsf_nx_but = ui.Button(f"SF partial nx: {sff.p_partial_nsfx}",
                                                             style={'background_color': sfw.darkblue},
                                                             mouse_pressed_fn=clkfn)
                            clkfn = lambda x, y, b, m: sfc.on_click_parital_sfny(x, y, b, m) # noqa : E731
                            sfw._part_nsf_ny_but = ui.Button(f"SF partial ny: {sff.p_partial_nsfy}",
                                                             style={'background_color': sfw.darkblue},
                                                             mouse_pressed_fn=clkfn)
                            clkfn = lambda x, y, b, m: sfc.on_click_parital_sfnz(x, y, b, m) # noqa : E731
                            sfw._part_nsf_nz_but = ui.Button(f"SF partial nz: {sff.p_partial_nsfz}",
                                                             style={'background_color': sfw.darkblue},
                                                             mouse_pressed_fn=clkfn)
                sfw.drframe = ui.CollapsableFrame("Distributed Renders", collapsed=sfw.docollapse_drframe)
                with sfw.drframe:
                    with ui.VStack():
                        sfw._parallel_render_but = ui.Button(f"Distributed Render {sff.p_parallelRender}",
                                                             style={'background_color': sfw.darkcyan},
                                                             clicked_fn=sfc.toggle_parallel_render)
                        with ui.HStack():
                            clkfn = lambda x, y, b, m: sfc.on_click_parallel_nxbatch(x, y, b, m) # noqa : E731
                            sfw._parallel_nxbatch_but = ui.Button(f"SF batch x: {sff.p_parallel_nxbatch}",
                                                                  style={'background_color': sfw.darkblue},
                                                                  mouse_pressed_fn=clkfn)
                            clkfn = lambda x, y, b, m: sfc.on_click_parallel_nybatch(x, y, b, m) # noqa : E731
                            sfw._parallel_nybatch_but = ui.Button(f"SF batch y: {sff.p_parallel_nybatch}",
                                                                  style={'background_color': sfw.darkblue},
                                                                  mouse_pressed_fn=clkfn)
                            clkfn = lambda x, y, b, m: sfc.on_click_parallel_nzbatch(x, y, b, m) # noqa : E731
                            sfw._parallel_nzbatch_but = ui.Button(f"SF batch z: {sff.p_parallel_nzbatch}",
                                                                  style={'background_color': sfw.darkblue},
                                                                  mouse_pressed_fn=clkfn)


class SfcTabSphereFlake(BaseTab):

    sfc: SfControls = None

    def __init__(self, sfw: SfWindow):
        super().__init__("SphereFlake")
        self.sfw = sfw
        self.sfc = sfw.sfc

    def build_fn(self):
        # print("SfcTabSphereFlake.build_fn (trc)")
        sfw = self.sfw
        sfc = self.sfc
        sff = self.sfw.sff
        smf = self.sfw.smf
        # print(f"SfcTabMulti.build_fn sfc:{type(sfc)} ")

        with ui.VStack(style={"margin": sfw.marg}):

            with ui.VStack():
                with ui.HStack():
                    sfw._sf_spawn_but = ui.Button("Spawn SphereFlake",
                                                  style={'background_color': sfw.darkred},
                                                  clicked_fn=lambda: sfc.on_click_sphereflake())
                    with ui.VStack(width=200):
                        sfw._sf_depth_but = ui.Button(f"Depth:{sff.p_depth}",
                                                      style={'background_color': sfw.darkgreen},
                                                      mouse_pressed_fn= # noqa : E251
                                                      lambda x, y, b, m: sfc.on_click_sfdepth(x, y, b, m))
                        with ui.HStack():
                            ui.Label("Radius Ratio: ",
                                     style={'background_color': sfw.darkgreen},
                                     width=50)
                            sfw._sf_radratio_slider = ui.FloatSlider(model=sfw._sf_radratio_slider_model,
                                                                     min=0.0, max=1.0, step=0.01,
                                                                     style={'background_color': sfw.darkblue}).model

                        # SF Gen Mode Combo Box
                        with ui.HStack():
                            ui.Label("Gen Mode:")
                            model = sfw._genmodebox_model
                            idx = model.as_int
                            sfw._genmodebox_model = ui.ComboBox(idx, *sff.GetGenModes()).model.get_item_value_model()

                        # SF Form Combo Box
                        with ui.HStack():
                            ui.Label("Gen Form1:")
                            model = sfw._genformbox_model
                            idx = model.as_int
                            sfw._genformbox_model = ui.ComboBox(idx, *sff.GetGenForms()).model.get_item_value_model()

                    with ui.VStack():
                        sfw._sf_nlat_but = ui.Button(f"Nlat:{smf.p_nlat}",
                                                     style={'background_color': sfw.darkgreen},
                                                     mouse_pressed_fn= # noqa : E251
                                                     lambda x, y, b, m: sfc.on_click_nlat(x, y, b, m))
                        sfw._sf_nlng_but = ui.Button(f"Nlng:{smf.p_nlng}",
                                                     style={'background_color': sfw.darkgreen},
                                                     mouse_pressed_fn= # noqa : E251
                                                     lambda x, y, b, m: sfc.on_click_nlng(x, y, b, m))


class SfcTabShapes(BaseTab):

    sfw: SfWindow
    sfc: SfControls

    def __init__(self, sfw: SfWindow):
        super().__init__("Shapes")
        self.sfw = sfw
        self.sfc = sfw.sfc

    def build_fn(self):
        # print("SfcTabShapes.build_fn (trc)")
        sfc = self.sfc
        sfw = self.sfw
        # print(f"SfcTabShapes.build_fn {type(sfc)}")

        with ui.VStack(style={"margin": sfw.marg}):

            with ui.HStack():
                sfw._sf_spawn_but = ui.Button("Spawn Prim",
                                              style={'background_color': sfw.darkred},
                                              clicked_fn=lambda: sfc.on_click_spawnprim())
                sfw._sf_primtospawn_but = ui.Button(f"{sfc._curprim}",
                                                    style={'background_color': sfw.darkpurple},
                                                    clicked_fn=lambda: sfc.on_click_changeprim())


class SfcTabMaterials(BaseTab):
    sfw: SfWindow
    sfc: SfControls

    def __init__(self, sfw: SfWindow):
        super().__init__("Materials")
        self.sfw = sfw
        self.sfc = sfw.sfc
        # print("SfcTabMaterials.build_fn {sfc}")

    def build_fn(self):
        # print("SfcTabMaterials.build_fn (trc)")
        sfw = self.sfw
        sfc = self.sfc

        with ui.VStack(style={"margin": sfw.marg}):

            # Material Combo Box
            with ui.HStack():
                ui.Label("SF Material 1:")
                idx = sfc._matkeys.index(sfc._current_material_name)
                sfw._sf_matbox = ui.ComboBox(idx, *sfc._matkeys)
                sfw._sf_matbox_model = sfw._sf_matbox.model.get_item_value_model()

                print("built sfw._sf_matbox")

            with ui.HStack():
                ui.Label("SF Material 2:")
                # use the alternate material name
                idx = sfc._matkeys.index(sfc._current_alt_material_name)
                sfw._sf_alt_matbox = ui.ComboBox(idx, *sfc._matkeys)
                sfw._sf_alt_matbox_model = sfw._sf_alt_matbox.model.get_item_value_model()
                print("built sfw._sf_matbox")

            # Bounds Material Combo Box
            with ui.HStack():
                ui.Label("Bounds Material:")
                idx = sfc._matkeys.index(sfc._current_bbox_material_name)
                sfw._bb_matbox = ui.ComboBox(idx, *sfc._matkeys)
                sfw._bb_matbox_model = sfw._bb_matbox.model.get_item_value_model()

            # Bounds Material Combo Box
            with ui.HStack():
                ui.Label("Floor Material:")
                idx = sfc._matkeys.index(sfc._current_floor_material_name)
                sfw._sf_floor_matbox = ui.ComboBox(idx, *sfc._matkeys)
                sfw._sf_floor_matbox_model = sfw._sf_floor_matbox.model.get_item_value_model()

            sfw.reset_materials_but = ui.Button(f"Reset Materials",
                                                style={'background_color': sfw.darkpurple},
                                                clicked_fn=lambda: sfc.on_click_resetmaterials())


class SfcTabOptions(BaseTab):
    sfw: SfWindow
    sfc: SfControls

    def __init__(self, sfw: SfWindow):
        super().__init__("Options")
        self.sfw = sfw
        self.sfc = sfw.sfc
        # print("SfcTabOptions.build_fn {sfc}")

    def build_fn(self):
        # print("SfcTabOptions.build_fn (trc)")
        sfw = self.sfw
        sfc = self.sfc # noqa : F841

        with ui.VStack(style={"margin": sfw.marg}):
            sfw.optlogframe = ui.CollapsableFrame("Logging Parameters", collapsed=sfw.docollapse_optlogframe)
            with sfw.optlogframe:
                with ui.VStack(style={"margin": sfw.marg}):
                    with ui.HStack():
                        ui.Label("Write Perf Log: ")
                        sfw.writelog_checkbox = ui.CheckBox(model=sfw.writelog_checkbox_model,
                                                            width=40, height=10, name="writelog", visible=True)
                    with ui.HStack():
                        ui.Label("Log Series Name:")
                        sfw.writelog_seriesname = ui.StringField(model=sfw.writelog_seriesname_model,
                                                                 width=200, height=20, visible=True)

            sfw.optremoteframe = ui.CollapsableFrame("Remote Processing", collapsed=sfw.docollapse_optremoteframe)
            with sfw.optremoteframe:
                with ui.VStack(style={"margin": sfw.marg}):
                    with ui.HStack():
                        ui.Label("Do Remote: ")
                        sfw.doremote_checkbox = ui.CheckBox(model=sfw.doremote_checkbox_model,
                                                            width=40, height=10, name="doremote", visible=True)
                    with ui.HStack():
                        ui.Label("Register Remote Endpoints: ")
                        sfw.doregister_remote_checkbox = ui.CheckBox(model=sfw.doregister_remote_checkbox_model,
                                                                     width=40, height=10,
                                                                     name="register endpoint", visible=True)
                    with ui.HStack():
                        ui.Label("Remote Type:")
                        # idx = sfc._remotetypes.index(sfc.p_doremotetype)
                        idx = sfc._remotetypes.index(sfc.p_doremotetype)
                        sfw.doremote_type = ui.ComboBox(idx, *sfc._remotetypes)
                        sfw.doremote_type_model = sfw.doremote_type.model.get_item_value_model()

                    with ui.HStack():
                        ui.Label("Remote URL:")
                        sfw.doremote_url = ui.StringField(model=sfw.doremote_url_model,
                                                          width=400, height=20, visible=True)

            sfw.optgroundframe = ui.CollapsableFrame("Ground Settings", collapsed=sfw.docollapse_optremoteframe)
            with sfw.optgroundframe:
                with ui.VStack(style={"margin": sfw.marg}):
                    with ui.HStack():
                        ui.Label("Add Rand")
                        sfw.addrand_checkbox = ui.CheckBox(model=sfw.addrand_checkbox_model,
                                                            width=40, height=10, name="addrand", visible=True)


class SfcTabPhysics(BaseTab):
    sfw: SfWindow
    sfc: SfControls

    def __init__(self, sfw: SfWindow):
        super().__init__("Physics")
        self.sfw = sfw
        self.sfc = sfw.sfc
        # print("SfcTabOptions.build_fn {sfc}")

    def build_fn(self):
        # print("SfcTabOptions.build_fn (trc)")
        sfw = self.sfw
        sfc = self.sfc # noqa : F841

        with ui.VStack(style={"margin": sfw.marg}):
            sfw.physcollidersframe = ui.CollapsableFrame("Colliders", collapsed=sfw.docollapse_physcollidersframe)
            with sfw.physcollidersframe:
                with ui.VStack(style={"margin": sfw.marg}):
                    with ui.HStack():
                        ui.Label("Equip Objects for Phyics: ")
                        sfw.equipforphysics_checkbox = ui.CheckBox(model=sfw.equipforphysics_checkbox_model,
                                                                   width=40, height=10, name="equipforphysics",
                                                                   visible=True)
