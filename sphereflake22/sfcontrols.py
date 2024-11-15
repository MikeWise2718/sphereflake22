import omni.kit.commands as okc
import omni.usd
import time
import datetime
import json
import socket
import psutil
from pxr import Gf, Sdf, Usd, UsdGeom, UsdShade, UsdLux
from pxr import UsdPhysics, Gf, UsdGeom
from .ovut import delete_if_exists, write_out_syspath, truncf
from .sfgen.sfut import MatMan
from .sfgen.spheremesh import SphereMeshFactory
from .sfgen.sphereflake import SphereFlakeFactory
# import multiprocessing
import subprocess
import os
import carb
from .ovut import get_setting, save_setting
import asyncio
# import asyncio

# fflake8: noqa


def build_sf_set(stagestr: str,
                 sx: int = 0, nx: int = 1, nnx: int = 1,
                 sy: int = 0, ny: int = 1, nny: int = 1,
                 sz: int = 0, nz: int = 1, nnz: int = 1,
                 matname: str = "Mirror"):
    # to test open a browser at http://localhost:8211/docs or 8011 or maybe 8111
    # stageid = omni.usd.get_context().get_stage_id()
    pid = os.getpid()
    msg = f"GMP build_sf_set  - x: {sx} {nx} {nnx} - y: {sy} {ny} {nny} - z: {sz} {nz} {nnz} mat:{matname}"
    msg += f" - stagestr: {stagestr} pid:{pid}"

    try:
        loop = asyncio.get_event_loop()
    except RuntimeError as e:
        if str(e).startswith('There is no current event loop in thread'):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        else:
            raise
    # stage=Usd.Stage.Open(rootLayer=Sdf.Find('anon:0000014AF6CD0760:World0.usd'), sessionLayer=Sdf.Find('anon:0000014AF6CD0B20:World0-session.usda')),

    print(msg)
    matman = MatMan()
    context = omni.usd.get_context()
    stage = context.get_stage()
    # stage = context.open_stage(stagestr)
    smf = SphereMeshFactory(stage, matman)
    sff = SphereFlakeFactory(stage, matman, smf)
    sff.ResetStage(stage)
    sff.p_sf_matname = matname
    sff.p_nsfx = nnx
    sff.p_nsfy = nny
    sff.p_nsfz = nnz
    sff.GenerateManySubcube(sx, sy, sz, nx, ny, nz)
    return msg


def init_sf_set():
    from omni.services.core import main
    # there seems to be no main until a window is created
    main.register_endpoint("get", "/sphereflake/build-sf-set", build_sf_set, tags=["Sphereflakes"])
    print("init_sf_set - mail.registered_endpoint called")


class DummyGpuInfo:
    total = 0
    used = 0
    free = 0

    def __init__(self):
        self.total = 0
        self.used = 0
        self.free = 0


# Any class derived from `omni.ext.IExt` in top level module (defined in `python.modules` of `extension.toml`) will be
# instantiated when extension gets enabled and `on_startup(ext_id)` will be called. Later when extension gets disabled
# on_shutdown() is called.
class SfControls():
    # ext_id is current extension id. It can be used with extension manager to query additional information, like where
    # this extension is located on filesystem.
    _stage = None
    _total_quads: int = 0
    _matman: MatMan = None
    _floor_xdim = 5
    _floor_zdim = 5
    _bounds_visible = False
    _sf_size = 50
    _vsc_test8 = False
    _gpuinfo = None
    _no_nvidia_smi = False
    sfw = None  # We can't give this a type because it would be a circular reference
    p_writelog = True
    p_logseriesname = "None"
    p_doremote = False
    p_doremoteurl = "http://localhost:8211"
    p_doremotetype = "InProcess"

    p_register_endpoint = False

    p_doloadusd = False
    p_doloadusd_url = "omniverse://localhost/sphereflake.usd"
    p_doloadusd_session = False
    p_doloadusd_sessionname = "None"

    p_equipforphysics = False

    p_addrand = False

    currenttag = "Empty"

    def __init__(self, matman: MatMan, smf: SphereMeshFactory, sff: SphereFlakeFactory):
        print("SfControls __init__ (trc)")

        self._matman = matman
        self._count = 0
        self._current_material_name = "Mirror"
        self._current_alt_material_name = "Red_Glass"
        self._current_bbox_material_name = "Blue_Glass"
        self._current_floor_material_name = "Mirror"
        self._matkeys = self._matman.GetMaterialNames()
        self._total_quads = 0
        self._sf_size = 50

        # self._sf_matbox: ui.ComboBox = None
        self._prims = ["Sphere", "Cube", "Cone", "Torus", "Cylinder", "Plane", "Disk", "Capsule",
                       "Billboard", "SphereMesh"]
        self._curprim = self._prims[0]
        self._sf_gen_modes = SphereFlakeFactory.GetGenModes()
        self._sf_gen_mode = self._sf_gen_modes[0]
        self._sf_gen_forms = SphereFlakeFactory.GetGenForms()
        self._sf_gen_form = self._sf_gen_forms[0]
        # self._genmodebox = ui.ComboBox(0, *self._sf_gen_modes).model
        # self._genformbox = ui.ComboBox(0, *self._sf_gen_forms).model

        self.smf = smf
        self.sff = sff

        self._remotetypes = sff.GetRemoteTypes()

        self._write_out_syspath = False

        if self._write_out_syspath:
            write_out_syspath()

        self.LoadSettings()

    def LateInit(self):
        # Register endpoints
        try:
            # D:\nv\ov\app\sfapp\_build\windows-x86_64\release\data\Kit\sfapp.view\1.0>notepad user.config.json
            # from omni.core.utils.extensions import enable_extension
            # enable_extension("omni.services.core")
            # from omni.kit.window.extensions import ext_controller, enable_extension
            # enable_extension("omni.services.core")
            # ext_controller.toggle_autoload("omni.services.core", True)
            self.query_remote_settings()
            if self.p_register_endpoint:
                init_sf_set()
                print("SfControls LateInit - registered endpoint")
            else:
                print("SfControls LateInit - did not register endpoint")
            pass
        except Exception as e:
            print(f"sfc.LateInit - Exception registering endpoint: {e}")

    def Close(self):
        try:
            from omni.services.core import main
            main.deregister_endpoint("get", "/sphereflake/build-sf-set")
            pass
        except Exception as e:
            print(f"Exception deregistering endpoint: {e}")

        print("SfControls close")

    def SaveSettings(self):
        print("SfControls SaveSettings (trc)")
        try:
            self.query_write_log()
            self.query_remote_settings()
            self.query_physics()
            save_setting("p_writelog", self.p_writelog)
            save_setting("p_logseriesname", self.p_logseriesname)
            save_setting("p_doremote", self.p_doremote)
            save_setting("p_register_endpoint", self.p_register_endpoint)
            save_setting("p_doremotetype", self.p_doremotetype)
            save_setting("p_doremoteurl", self.p_doremoteurl)
            save_setting("p_doloadusd", self.p_doloadusd)
            save_setting("p_doloadusd_url", self.p_doloadusd_url)
            save_setting("p_doloadusd_session", self.p_doloadusd_session)
            save_setting("p_doloadusd_sessionname", self.p_doloadusd_sessionname)
            save_setting("p_equipforphysics", self.p_equipforphysics)
            save_setting("p_addrand", self.p_addrand)
            if self.sff is not None:
                self.sff.SaveSettings()
            print(f"SaveSettings: p_equipforphysics:{self.p_equipforphysics} (trc)")
        except Exception as e:
            carb.log_error(f"Exception in sfcontrols.SaveSettings: {e}")

    def LoadSettings(self):
        print("SfControls LoadSettings (trc)")
        self.p_writelog = get_setting("p_writelog", True)
        self.p_logseriesname = get_setting("p_logseriesname", "None")
        self.p_doremote = get_setting("p_doremote", False)
        self.p_register_endpoint = get_setting("p_register_endpoint", False)
        self.p_doremotetype = get_setting("p_doremotetype", SphereFlakeFactory.GetDefaultRemoteType())
        self.p_doremoteurl = get_setting("p_doremoteurl", "http://localhost")
        self.p_doloadusd = get_setting("p_doloadusd", False)
        self.p_doloadusd_url = get_setting("p_doloadusd_url", "omniverse://localhost/sphereflake.usd")
        self.p_doloadusd_session = get_setting("p_doloadusd_session", False)
        self.p_doloadusd_sessionname = get_setting("p_doloadusd_sessionname", "None")
        self.p_equipforphysics = get_setting("p_equipforphysics", False)
        self.p_addrand = get_setting("p_addrand", False)
        print(f"LoadSettings: p_equipforphysics:{self.p_equipforphysics}  (trc)")

    def create_sphere_light(self):
        path = "/World/Light/SphereLight"
        l = UsdLux.SphereLight.Define(self._stage, Sdf.Path(path))
        l.CreateColorTemperatureAttr(6500.0)
        l.CreateIntensityAttr(350000.0)
        l.CreateRadiusAttr(200)
        l.CreateColorAttr( (1.0, 1.0, 1.0 ) )
        l.CreateDiffuseAttr( 3.0 )
        try:
            l.AddTranslateOp().Set( Gf.Vec3d( 0.0, 800.0, 0.0 ) )
        except Exception as e:
            print(f"create_sphere_light exception:{e}")
        print(f"created sphere light at {path}")

    def setup_environment(self, extent3f: Gf.Vec3f,  force: bool = False):
        print("setup_environment")
        ppathstr = "/World/Floor"
        if force:
            delete_if_exists(ppathstr)

        prim_path_sdf = Sdf.Path(ppathstr)

        prim: Usd.Prim = self._stage .GetPrimAtPath(prim_path_sdf)
        if not prim.IsValid():
            okc.execute('CreateMeshPrimWithDefaultXform',	prim_type="Plane", prim_path=ppathstr)
            floormatname = self.get_curfloormat_name()
            # omni.kit.commands.execute('BindMaterialCommand', prim_path='/World/Floor',
            #                           material_path=f'/World/Looks/{floormatname}')
            mtl = self._matman.GetMaterial(floormatname)
            stage = omni.usd.get_context().get_stage()
            prim: Usd.Prim = stage.GetPrimAtPath(ppathstr)
            UsdShade.MaterialBindingAPI(prim).Bind(mtl)
            if self.p_equipforphysics:
                # rigid_api = UsdPhysics.RigidBodyAPI.Apply(prim)
                # rigid_api.CreateRigidBodyEnabledAttr(True)
                UsdPhysics.CollisionAPI.Apply(prim)

            # self._floor_xdim = extent3f[0] / 10
            # self._floor_zdim = extent3f[2] / 10
            self._floor_xdim = extent3f[0] / 100
            self._floor_zdim = extent3f[2] / 100
            okc.execute('TransformMultiPrimsSRTCpp',
                        count=1,
                        paths=[ppathstr],
                        new_scales=[self._floor_xdim, 1, self._floor_zdim])
            baseurl = 'https://omniverse-content-production.s3.us-west-2.amazonaws.com'
            okc.execute('CreateDynamicSkyCommand',
                    sky_url=f'{baseurl}/Assets/Skies/2022_1/Skies/Dynamic/CumulusLight.usd',
                    sky_path='/Environment/sky')
            skyprim: Usd.Prim = self._stage.GetPrimAtPath('/Environment/sky')
            if not skyprim.IsValid():
                print("Error: Could not execute CreateDynamicSkyCommand so creating sphere light")
                self.create_sphere_light()

            # print(f"nvidia_smi.__file__:{nvidia_smi.__file__}")
            # print(f"omni.ui.__file__:{omni.ui.__file__}")
            # print(f"omni.ext.__file__:{omni.ext.__file__}")
            print("setup_environment done")

    def ensure_stage(self):
        # print("ensure_stage")
        self._stage = omni.usd.get_context().get_stage()
        # if self._stage is None:
        #     self._stage = omni.usd.get_context().get_stage()
        #     # print(f"ensure_stage got stage:{self._stage}")
        #     UsdGeom.SetStageUpAxis(self._stage, UsdGeom.Tokens.y)
        #     self._total_quads = 0
        #     extent3f = self.sff.GetSphereFlakeBoundingBox()
        #     self.setup_environment(extent3f)

    def create_billboard(self, primpath: str, w: float = 860, h: float = 290):
        UsdGeom.SetStageUpAxis(self._stage, UsdGeom.Tokens.y)

        billboard = UsdGeom.Mesh.Define(self._stage, primpath)
        w2 = w/2
        h2 = h/2
        pts = [(-w2, -h2, 0), (w2, -h2, 0), (w2, h2, 0), (-w2, h2, 0)]
        ext = [(-w2, -h2, 0), (w2, h2, 0)]
        billboard.CreatePointsAttr(pts)
        billboard.CreateFaceVertexCountsAttr([4])
        billboard.CreateFaceVertexIndicesAttr([0, 1, 2, 3])
        billboard.CreateExtentAttr(ext)
        texCoords = UsdGeom.PrimvarsAPI(billboard).CreatePrimvar("st", Sdf.ValueTypeNames.TexCoord2fArray,
                                                                 UsdGeom.Tokens.varying)
        texCoords.Set([(0, 0), (1, 0), (1, 1), (0, 1)])
        return billboard

        self.ensure_stage()

# Tore:
# Remove _sf_size into smf (and sff?)

    # def get_bool_model(self, option_name: str):
    #     bool_model = ui.SimpleBoolModel()
    #     return bool_model

    def toggle_write_log(self):
        self.p_writelog = not self.p_writelog
        print(f"toggle_write_log is now:{self.p_writelog}")

    def query_write_log(self):
        self.p_writelog = self.sfw.writelog_checkbox_model.as_bool
        self.p_logseriesname = self.sfw.writelog_seriesname_model.as_string
        print(f"query_write_log is now:{self.p_writelog} name:{self.p_logseriesname}")

    def query_physics(self):
        self.p_equipforphysics = self.sfw.equipforphysics_checkbox_model.as_bool
        print(f"sfc.p_equipforphysics is now:{self.p_equipforphysics}")

    def query_remote_settings(self):
        sfw = self.sfw
        if sfw.doremote_checkbox_model is not None:
            self.p_doremote = self.sfw.doremote_checkbox_model.as_bool
        if sfw.doregister_remote_checkbox_model is not None:
            self.p_register_endpoint = self.sfw.doregister_remote_checkbox_model.as_bool
        if sfw.doremote_type_model is not None:
            idx = self.sfw.doremote_type_model.as_int
            self.p_doremotetype = self._remotetypes[idx]
        if sfw.doremote_url_model is not None:
            self.p_doremoteurl = self.sfw.doremote_url_model.as_string
        print(f"query_remote_settings is now:{self.p_doremote} type:{self.p_doremotetype} url:{self.p_doremoteurl}")

    def toggle_bounds(self):
        self.ensure_stage()
        self._bounds_visible = not self._bounds_visible
        self.sfw._tog_bounds_but.text = f"Bounds:{self._bounds_visible}"
        self.sff.ToggleBoundsVisiblity(self._bounds_visible)

    def on_click_billboard(self):
        self.ensure_stage()

        primpath = f"/World/Prim_Billboard_{self._count}"
        billboard = self.create_billboard(primpath)

        material = self.get_curmat_mat()
        UsdShade.MaterialBindingAPI(billboard).Bind(material)

    def on_click_spheremesh(self):
        self.ensure_stage()

        self.smf.GenPrep()

        matname = self.get_curmat_name()
        cpt = Gf.Vec3f(0, self._sf_size, 0)
        primpath = f"/World/SphereMesh_{self._count}"
        self._count += 1
        self.smf.CreateMesh(primpath, matname, cpt, self._sf_size)

    def update_radratio(self):
        if self.sfw._sf_radratio_slider_model is not None:
            val = self.sfw._sf_radratio_slider_model.as_float
            self.sff.p_radratio = val

    def on_click_sphereflake(self):
        self.ensure_stage()

        start_time = time.time()

        sff = self.sff
        sff.p_genmode = self.get_sf_genmode()
        sff.p_genform = self.get_sf_genform()
        sff.p_rad = self._sf_size
        # print(f"slider: {type(self._sf_radratio_slider)}")
        # sff._radratio = self._sf_radratio_slider.get_value_as_float()
        self.update_radratio()
        sff.p_sf_matname = self.get_curmat_name()
        sff.p_sf_alt_matname = self.get_curaltmat_name()
        sff.p_bb_matname = self.get_curmat_bbox_name()

        cpt = Gf.Vec3f(0, self._sf_size, 0)
        primpath = f"/World/SphereFlake_{self._count}"

        self._count += 1
        sff.Generate(primpath, cpt)

        elap = time.time() - start_time
        self.sfw._statuslabel.text = f"SphereFlake took elapsed: {elap:.2f} s"
        self.UpdateStuff()

    async def generate_sflakes(self):

        sff = self.sff

        sff._matman = self._matman
        sff.p_genmode = self.get_sf_genmode()
        sff.p_genform = self.get_sf_genform()
        sff.p_rad = self._sf_size
        self.update_radratio()

        sff.p_sf_matname = self.get_curmat_name()
        sff.p_sf_alt_matname = self.get_curaltmat_name()

        sff.p_make_bounds_visible = self._bounds_visible
        sff.p_bb_matname = self.get_curmat_bbox_name()
        sff.p_tag = self.currenttag
        self.query_physics()
        sff.p_equipforphysics = self.p_equipforphysics

        if sff.p_parallelRender:
            self.query_remote_settings()
            self._stage = omni.usd.get_context().get_stage()
            sff.ResetStage(self._stage)
            await sff.GenerateManyParallel(doremote=self.p_doremote,
                                           remotetype=self.p_doremotetype,
                                           remoteurl=self.p_doremoteurl)
            new_count = sff.p_nsfx*sff.p_nsfy*sff.p_nsfz
        else:
            new_count = sff.GenerateMany()

        self._count += new_count
        sff.SaveSettings()
        self.SaveSettings()

    def write_log(self, elap: float = 0.0):
        self.query_write_log()
        if self.p_writelog:
            nflakes = self.sff.p_nsfx * self.sff.p_nsfz
            ntris, nprims = self.sff.CalcTrisAndPrims()
            dogpu = self._gpuinfo is not None
            if dogpu:
                gpuinfo = self._gpuinfo
            else:
                gpuinfo = {"total": 0, "used": 0, "free": 0}
            om = float(1024*1024*1024)
            hostname = socket.gethostname()
            memused = psutil.virtual_memory().used
            memtot = psutil.virtual_memory().total
            memfree = psutil.virtual_memory().free
            cores = psutil.cpu_count()
            # msg = f"GPU Mem tot:  {gpuinfo.total/om:.2f}: used: {gpuinfo.used/om:.2f} free: {gpuinfo.free/om:.2f} GB"
            # msg += f"\nCPU cores: {cores}"
            # msg += f"\nSys Mem tot: {memtot/om:.2f}: used: {memused/om:.2f} free: {memfree/om:.2f} GB"
            rundict = {"0-seriesname": self.p_logseriesname,
                       "0-hostname": hostname,
                       "0-date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                       "0-tag": self.currenttag,
                       "1-genmode": self.sff.p_genmode,
                       "1-genform": self.sff.p_genform,
                       "1-depth": self.sff.p_depth,
                       "1-rad": self.sff.p_rad,
                       "1-radratio": self.sff.p_radratio,
                       "1-nsfx": self.sff.p_nsfx,
                       "1-nsfy": self.sff.p_nsfy,
                       "1-nsfz": self.sff.p_nsfz,
                       "2-tris": ntris,
                       "2-prims": nprims,
                       "2-nflakes": nflakes,
                       "2-elapsed": truncf(elap, 3),
                       "3-gpu_gbmem_tot": truncf(gpuinfo.total/om, 3),
                       "3-gpu_gbmem_used": truncf(gpuinfo.used/om, 3),
                       "3-gpu_gbmem_free": truncf(gpuinfo.free/om, 3),
                       "4-sys_gbmem_tot": truncf(memtot/om, 3),
                       "4-sys_gbmem_used": truncf(memused/om, 3),
                       "4-sys_gbmem_free": truncf(memfree/om, 3),
                       "5-cpu_cores": cores,
                       }
            self.WriteRunLog(rundict)

    async def on_click_multi_sphereflake(self):
        self.ensure_stage()
        # extent3f = self.sff.GetSphereFlakeBoundingBox()
        extent3f = self.sff.GetSphereFlakeBoundingBoxNxNyNz()
        self.setup_environment(extent3f, force=True)

        start_time = time.time()
        self.sff.ResetStage(self._stage)
        hostname = socket.gethostname()
        datestr = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        self.currenttag = f"{hostname}-{datestr}"
        await self.generate_sflakes()
        elap = time.time() - start_time

        nflakes = self.sff.p_nsfx * self.sff.p_nsfz

        self.sfw._statuslabel.text = f"{nflakes} flakes took elapsed: {elap:.2f} s"

        self.UpdateStuff()
        self.write_log(elap)

    def spawnprim(self, primtype):
        self.ensure_stage()
        extent3f = self.sff.GetSphereFlakeBoundingBox()
        self.setup_environment(extent3f, force=True)

        if primtype == "Billboard":
            self.on_click_billboard()
            return
        elif primtype == "SphereMesh":
            self.on_click_spheremesh()
            return

        primpath = f"/World/Prim_{primtype}_{self._count}"
        okc.execute('CreateMeshPrimWithDefaultXform', prim_type=primtype, prim_path=primpath)

        material = self.get_curmat_mat()
        self._count += 1

        okc.execute('TransformMultiPrimsSRTCpp',
                    count=1,
                    paths=[primpath],
                    new_scales=[1, 1, 1],
                    new_translations=[0, 50, 0])
        prim: Usd.Prim = self._stage.GetPrimAtPath(primpath)
        UsdShade.MaterialBindingAPI(prim).Bind(material)

    def on_click_writerunlog(self):
        self.p_writelog = not self.p_writelog
        self.sfw._sf_writerunlog_but.text = f"Write Perf Log: {self.p_writelog}"

    def round_increment(self, val: int, butval: bool, maxval: int, minval: int = 0):
        inc = 1 if butval else -1
        val += inc
        if val > maxval:
            val = minval
        if val < minval:
            val = maxval
        return val

    def UpdateStuff(self):
        self.UpdateNQuads()
        self.UpdateMQuads()
        self.UpdateGpuMemory()

    def on_click_sfdepth(self, x, y, button, modifier):
        depth = self.round_increment(self.sff.p_depth, button == 1, 5, 0)
        self.sfw._sf_depth_but.text = f"Depth:{depth}"
        self.sff.p_depth = depth
        self.UpdateStuff()

    def on_click_nlat(self, x, y, button, modifier):
        nlat = self.round_increment(self.smf.p_nlat, button == 1, 16, 3)
        self._sf_nlat_but.text = f"Nlat:{nlat}"
        self.smf.p_nlat = nlat
        self.UpdateStuff()

    def on_click_nlng(self, x, y, button, modifier):
        nlng = self.round_increment(self.smf.p_nlng, button == 1, 16, 3)
        self._sf_nlng_but.text = f"Nlng:{nlng}"
        self.smf.p_nlng = nlng
        self.UpdateStuff()

    def on_click_sfx(self, x, y, button, modifier):
        nsfx = self.round_increment(self.sff.p_nsfx, button == 1, 20, 1)
        self.sfw._nsf_x_but.text = f"SF - x:{nsfx}"
        self.sff.p_nsfx = nsfx
        self.UpdateStuff()

    def toggle_parallel_render(self):
        self.sff.p_parallelRender = not self.sff.p_parallelRender
        self.sfw._parallel_render_but.text = f"Parallel Render: {self.sff.p_parallelRender}"

    def on_click_parallel_nxbatch(self, x, y, button, modifier):
        tmp = self.round_increment(self.sff.p_parallel_nxbatch, button == 1, self.sff.p_nsfx, 1)
        self.sfw._parallel_nxbatch_but.text = f"SF batch x: {tmp}"
        self.sff.p_parallel_nxbatch = tmp
        print(f"on_click_parallel_nxbatch:{tmp}")
        self.UpdateStuff()

    def on_click_parallel_nybatch(self, x, y, button, modifier):
        tmp = self.round_increment(self.sff.p_parallel_nybatch, button == 1, self.sff.p_nsfy, 1)
        self.sfw._parallel_nybatch_but.text = f"SF batch y: {tmp}"
        self.sff.p_parallel_nybatch = tmp
        self.UpdateStuff()

    def on_click_parallel_nzbatch(self, x, y, button, modifier):
        tmp = self.round_increment(self.sff.p_parallel_nzbatch, button == 1, self.sff.p_nsfz, 1)
        self.sfw._parallel_nzbatch_but.text = f"SF batch z: {tmp}"
        self.sff.p_parallel_nzbatch = tmp
        self.UpdateStuff()

    def toggle_partial_render(self):
        self.sff.p_partialRender = not self.sff.p_partialRender
        self.sfw._partial_render_but.text = f"Partial Render: {self.sff.p_partialRender}"

    def on_click_parital_sfsx(self, x, y, button, modifier):
        tmp = self.round_increment(self.sff.p_partial_ssfx, button == 1, self.sff.p_nsfx-1, 0)
        self.sfw._part_nsf_sx_but.text = f"SF partial sx: {tmp}"
        self.sff.p_partial_ssfx = tmp
        self.UpdateStuff()

    def on_click_parital_sfsy(self, x, y, button, modifier):
        tmp = self.round_increment(self.sff.p_partial_ssfy, button == 1, self.sff.p_nsfy-1, 0)
        self.sfw._part_nsf_sy_but.text = f"SF partial sy: {tmp}"
        self.sff.p_partial_ssfy = tmp
        self.UpdateStuff()

    def on_click_parital_sfsz(self, x, y, button, modifier):
        tmp = self.round_increment(self.sff.p_partial_ssfz, button == 1, self.sff.p_nsfz-1, 0)
        self.sfw._part_nsf_sz_but.text = f"SF partial sz: {tmp}"
        self.sff.p_partial_ssfz = tmp
        self.UpdateStuff()

    def on_click_parital_sfnx(self, x, y, button, modifier):
        tmp = self.round_increment(self.sff.p_partial_nsfx, button == 1, self.sff.p_nsfx, 1)
        self.sfw._part_nsf_nx_but.text = f"SF partial nx: {tmp}"
        self.sff.p_partial_nsfx = tmp
        self.UpdateStuff()

    def on_click_parital_sfny(self, x, y, button, modifier):
        tmp = self.round_increment(self.sff.p_partial_nsfy, button == 1, self.sff.p_nsfy, 1)
        self.sfw._part_nsf_ny_but.text = f"SF partial ny: {tmp}"
        self.sff.p_partial_nsfy = tmp
        self.UpdateStuff()

    def on_click_parital_sfnz(self, x, y, button, modifier):
        tmp = self.round_increment(self.sff.p_partial_nsfz, button == 1, self.sff.p_nsfz, 1)
        self.sfw._part_nsf_nz_but.text = f"SF partial nz: {tmp}"
        self.sff.p_partial_nsfz = tmp
        self.UpdateStuff()

    def on_click_sfy(self, x, y, button, modifier):
        nsfy = self.round_increment(self.sff.p_nsfy, button == 1, 20, 1)
        self.sfw._nsf_y_but.text = f"SF - y:{nsfy}"
        self.sff.p_nsfy = nsfy
        self.UpdateStuff()

    def on_click_sfz(self, x, y, button, modifier):
        nsfz = self.round_increment(self.sff.p_nsfz, button == 1, 20, 1)
        self.sfw._nsf_z_but.text = f"SF - z:{nsfz}"
        self.sff.p_nsfz = nsfz
        self.UpdateStuff()

    def on_click_spawnprim(self):
        self.spawnprim(self._curprim)

    def xprocess():
        pass
        # print("xprocess started")

    def on_click_launchxproc(self):
        self.ensure_stage()
        # cmdpath = "D:\\nv\\ov\\ext\\sphereflake-benchmark\\exts\\omni.sphereflake\\omni\\sphereflake"
        subprocess.call(["python.exe"])
        # subprocess.call([cmdpath,"hello.py"])
        # print("launching xproc")
        # p1 = multiprocessing.Process(target=self.xprocess)
        # p1.start()  # Casues app to stop servicing events
        # self._xproc = XProcess(self._stage, self._curprim, self.smf, self.sff)
        # self._xproc.start()

    def on_click_clearprims(self):
        self.ensure_stage()
        # check and see what we have missed
        worldprim = self._stage.GetPrimAtPath("/World")
        for child_prim in worldprim.GetAllChildren():
            cname = child_prim.GetName()
            prefix = cname.split("_")[0]
            dodelete = prefix in ["SphereFlake", "SphereMesh", "Prim"]
            if dodelete:
                # print(f"deleting {cname}")
                cpath = child_prim.GetPrimPath()
                self._stage.RemovePrim(cpath)
                # okc.execute("DeletePrimsCommand", paths=[cpath])
        self.smf.Clear()
        self.sff.Clear()
        self._count = 0

    def on_click_changeprim(self):
        idx = self._prims.index(self._curprim) + 1
        if idx >= len(self._prims):
            idx = 0
        self._curprim = self._prims[idx]
        self.sfw._sf_primtospawn_but.text = f"{self._curprim}"

    matclickcount = 0

    def on_click_resetmaterials(self):
        self._matman.Reinitialize()
        nmat = self._matman.GetMaterialCount()
        self.sfw.reset_materials_but.text = f"Reset Materials ({nmat} defined) - {self.matclickcount}"
        self.matclickcount += 1

    def UpdateNQuads(self):
        ntris, nprims = self.sff.CalcTrisAndPrims()
        elap = SphereFlakeFactory.GetLastGenTime()
        if self.sfw._sf_depth_but is not None:
            self.sfw._sf_spawn_but.text = f"Spawn ShereFlake\n tris:{ntris:,} prims:{nprims:,}\ngen: {elap:.2f} s"

    def UpdateMQuads(self):
        ntris, nprims = self.sff.CalcTrisAndPrims()
        tottris = ntris*self.sff.p_nsfx*self.sff.p_nsfz
        if self.sfw._msf_spawn_but is not None:
            self.sfw._msf_spawn_but.text = f"Multi ShereFlake\ntris:{tottris:,} prims:{nprims:,}"

    def UpdateGpuMemory(self):

        # This is not always available
        if self._no_nvidia_smi:
            gpuinfo = DummyGpuInfo()
        else:
            try:
                import nvidia_smi
                nvidia_smi.nvmlInit()

                handle = nvidia_smi.nvmlDeviceGetHandleByIndex(0)
                # card id 0 hardcoded here, there is also a call to get all available card ids, so we could iterate
                gpuinfo = nvidia_smi.nvmlDeviceGetMemoryInfo(handle)


            except Exception:
                self._no_nvidia_smi = True
                gpuinfo = DummyGpuInfo()

        self._gpuinfo = gpuinfo

        om = float(1024*1024*1024)
        if self._no_nvidia_smi:
            msg = "No GPU mem because nvidia_smi not available"
        else:
            msg = f"GPU Mem tot:  {gpuinfo.total/om:.2f}: used:  {gpuinfo.used/om:.2f} free:  {gpuinfo.free/om:.2f} GB"
        memused = psutil.virtual_memory().used
        memtot = psutil.virtual_memory().total
        memfree = psutil.virtual_memory().free
        msg += f"\nSys Mem tot: {memtot/om:.2f}: used: {memused/om:.2f} free: {memfree/om:.2f} GB"
        cores = psutil.cpu_count()
        msg += f"\nCPU cores: {cores}"
        refcnt = self._matman.refCount
        ftccnt = self._matman.fetchCount
        skpcnt = self._matman.skipCount
        msg += f"\n Materials ref: {refcnt} fetched: {ftccnt} skipped: {skpcnt}"

        self.sfw._memlabel.text = msg

    def get_curmat_mat(self):
        idx = self.sfw._sf_matbox_model.as_int
        self._current_material_name = self._matkeys[idx]
        return self._matman.GetMaterial(self._current_material_name)

    def get_curmat_name(self):
        idx = self.sfw._sf_matbox_model.as_int
        self._current_material_name = self._matkeys[idx]
        return self._current_material_name

    def get_curaltmat_mat(self):
        idx = self.sfw._sf_alt_matbox_model.as_int
        self._current_alt_material_name = self._matkeys[idx]
        return self._matman.GetMaterial(self._current_alt_material_name)

    def get_curaltmat_name(self):
        idx = self.sfw._sf_alt_matbox_model.as_int
        self._current_alt_material_name = self._matkeys[idx]
        return self._current_alt_material_name

    def get_curfloormat_mat(self):
        idx = self.sfw._sf_floor_matbox_model.as_int
        self._current_floor_material_name = self._matkeys[idx]
        return self._matman.GetMaterial(self._current_floor_material_name)

    def get_curmat_bbox_name(self):
        idx = self.sfw._bb_matbox_model.as_int
        self._current_bbox_material_name = self._matkeys[idx]
        return self._current_bbox_material_name

    def get_curmat_bbox_mat(self):
        idx = self.sfw._bb_matbox_model.as_int
        self._current_bbox_material_name = self._matkeys[idx]
        return self._matman.GetMaterial(self._current_bbox_material_name)

    def get_curfloormat_name(self):
        idx = self.sfw._sf_floor_matbox_model.as_int
        self._current_floor_material_name = self._matkeys[idx]
        return self._current_floor_material_name

    def get_sf_genmode(self):
        idx = self.sfw._genmodebox_model.as_int
        return self._sf_gen_modes[idx]

    def get_sf_genform(self):
        idx = self.sfw._genformbox_model.as_int
        return self._sf_gen_forms[idx]

    def WriteRunLog(self, rundict=None):

        if rundict is None:
            rundict = {}

        jline = json.dumps(rundict, sort_keys=True)

        try:
            fname = "log.txt"
            with open(fname, "a") as f:
                f.write(f"{jline}\n")

            print(f"wrote log to {fname}")
        except Exception:
            pass
