import carb
import time
import asyncio
import math
import socket
from pxr import Gf, Usd, UsdGeom, UsdShade
from pxr import UsdPhysics, Gf, UsdGeom
from .spheremesh import SphereMeshFactory
from .sfut import MatMan, get_setting, save_setting

# import omni.services.client

latest_sf_gen_time = 0


def cross_product(v1: Gf.Vec3f, v2: Gf.Vec3f) -> Gf.Vec3f:
    x = v1[1] * v2[2] - v1[2] * v2[1]
    y = v1[2] * v2[0] - v1[0] * v2[2]
    z = v1[0] * v2[1] - v1[1] * v2[0]
    rv = Gf.Vec3f(x, y, z)
    return rv


class SphereFlakeFactory():
    _matman: MatMan = None
    _smf: SphereMeshFactory = None
    p_genmode = "UsdSphere"
    p_genform = "Classic"
    p_depth = 1
    p_rad = 50
    p_radratio = 0.3
    p_nsfx = 1
    p_nsfy = 1
    p_nsfz = 1
    p_partialRender = False
    p_partial_ssfx = 0
    p_partial_ssfy = 0
    p_partial_ssfz = 0
    p_partial_nsfx = 1
    p_partial_nsfy = 1
    p_partial_nsfz = 1
    p_parallelRender = False
    p_parallel_nxbatch = 1
    p_parallel_nybatch = 1
    p_parallel_nzbatch = 1

    p_sf_matname = "Mirror"
    p_sf_alt_matname = "Red_Glass"
    p_bb_matname = "Blue_Glass"
    p_make_bounds_visible = False
    p_tag = None
    p_equipforphysics = False
    _start_time = 0
    _createlist: list = []
    _bbcubelist: list = []

    _org = Gf.Vec3f(0, 0, 0)
    _xax = Gf.Vec3f(1, 0, 0)
    _yax = Gf.Vec3f(0, 1, 0)
    _zax = Gf.Vec3f(0, 0, 1)

    def __init__(self, stage: Usd.Stage, matman: MatMan, smf: SphereMeshFactory) -> None:
        # self._stage = omni.usd.get_context().get_stage()
        self._count = 0
        self._matman = matman
        self._smf = smf
        self._stage = stage
        print(f"SFF initialized with stage:{stage} (trc1)")

    def ResetStage(self, stage: Usd.Stage):
        self._stage = stage
        self._smf.ResetStage(stage)

    def GenPrep(self):
        self._smf.GenPrep()
        pass

    def LoadSettings(self):
        print("SphereFlakeFactory.LoadSettings (trc)")
        self.p_genmode = get_setting("p_genmode", self.p_genmode)
        self.p_genform = get_setting("p_genform", self.p_genform)
        self.p_depth = get_setting("p_depth", self.p_depth)
        self.p_rad = get_setting("p_rad", self.p_rad)
        self.p_radratio = get_setting("p_radratio", self.p_radratio)
        self.p_nsfx = get_setting("p_nsfx", self.p_nsfx, db=True)
        self.p_nsfy = get_setting("p_nsfy", self.p_nsfy, db=True)
        self.p_nsfz = get_setting("p_nsfz", self.p_nsfz, db=True)
        self.p_partialRender = get_setting("p_partialRender", self.p_partialRender)
        self.p_partial_ssfx = get_setting("p_partial_ssfx", self.p_partial_ssfx)
        self.p_partial_ssfy = get_setting("p_partial_ssfy", self.p_partial_ssfy)
        self.p_partial_ssfz = get_setting("p_partial_ssfz", self.p_partial_ssfz)
        self.p_partial_nsfx = get_setting("p_partial_nsfx", self.p_partial_nsfx)
        self.p_partial_nsfy = get_setting("p_partial_nsfy", self.p_partial_nsfy)
        self.p_partial_nsfz = get_setting("p_partial_nsfz", self.p_partial_nsfz)
        self.p_parallelRender = get_setting("p_parallelRender", self.p_parallelRender)
        self.p_parallel_nxbatch = get_setting("p_parallel_nxbatch", self.p_parallel_nxbatch)
        self.p_parallel_nybatch = get_setting("p_parallel_nybatch", self.p_parallel_nybatch)
        self.p_parallel_nzbatch = get_setting("p_parallel_nzbatch", self.p_parallel_nzbatch)
        self.p_sf_matname = get_setting("p_sf_matname", self.p_sf_matname)
        self.p_sf_alt_matname = get_setting("p_sf_alt_matname", self.p_sf_alt_matname)
        self.p_bb_matname = get_setting("p_bb_matname", self.p_bb_matname)
        self.p_bb_matname = get_setting("p_bb_matname", self.p_bb_matname)
        self.p_make_bounds_visible = get_setting("p_make_bounds_visible", self.p_make_bounds_visible)
        print(f"SphereFlakeFactory.LoadSettings: p_nsfx:{self.p_nsfx} p_nsfy:{self.p_nsfy} p_nsfz:{self.p_nsfz}")

    def SaveSettings(self):
        print("SphereFlakeFactory.SaveSettings (trc)")
        save_setting("p_genmode", self.p_genmode)
        save_setting("p_genform", self.p_genform)
        save_setting("p_depth", self.p_depth)
        save_setting("p_rad", self.p_rad)
        save_setting("p_radratio", self.p_radratio)
        save_setting("p_nsfx", self.p_nsfx)
        save_setting("p_nsfy", self.p_nsfy)
        save_setting("p_nsfz", self.p_nsfz)
        save_setting("p_partialRender", self.p_partialRender)
        save_setting("p_partial_ssfx", self.p_partial_ssfx)
        save_setting("p_partial_ssfy", self.p_partial_ssfy)
        save_setting("p_partial_ssfz", self.p_partial_ssfz)
        save_setting("p_partial_nsfx", self.p_partial_nsfx)
        save_setting("p_partial_nsfy", self.p_partial_nsfy)
        save_setting("p_partial_nsfz", self.p_partial_nsfz)
        save_setting("p_parallelRender", self.p_parallelRender)
        save_setting("p_parallel_nxbatch", self.p_parallel_nxbatch)
        save_setting("p_parallel_nybatch", self.p_parallel_nybatch)
        save_setting("p_parallel_nzbatch", self.p_parallel_nzbatch)
        save_setting("p_sf_matname", self.p_sf_matname)
        save_setting("p_sf_alt_matname", self.p_sf_alt_matname)
        save_setting("p_bb_matname", self.p_bb_matname)
        save_setting("p_make_bounds_visible", self.p_make_bounds_visible)

    @staticmethod
    def GetGenModes():
        return ["UsdSphere", "DirectMesh", "AsyncMesh", "OmniSphere"]

    @staticmethod
    def GetGenForms():
        return ["Classic", "Flat-8"]

    @staticmethod
    def GetRemoteTypes():
        return ["InProcess", "RemoteUrl", "RemoteProcess", "RemoteBatchFile"]

    @staticmethod
    def GetDefaultRemoteType():
        return "RemoteBatchFile"

    def Clear(self):
        self._createlist = []
        self._bbcubelist = []

    def Set(self, attname: str, val: float):
        if hasattr(self, attname):
            self.__dict__[attname] = val
        else:
            carb.log.error(f"SphereFlakeFactory.Set: no attribute {attname}")

    def CalcQuadsAndPrims(self):
        nring = 9 if self.p_genform == "Classic" else 8
        nlat = self._smf.p_nlat
        nlng = self._smf.p_nlng
        totquads = 0
        totprims = 0
        for i in range(self.p_depth+1):
            nspheres = nring**(i)
            nquads = nspheres * nlat * nlng
            totquads += nquads
            totprims += nspheres
        return totquads, totprims

    def CalcTrisAndPrims(self):
        totquads, totprims = self.CalcQuadsAndPrims()
        return totquads * 2, totprims

    def GetCenterPosition(self, ix: int, iy: int, iz: int,
                          extentvec: Gf.Vec3f, gap: float = 1.1):
        nx = self.p_nsfx
        # ny = self.p_nsfy
        nz = self.p_nsfz

        ixoff = (nx-1)/2
        iyoff = -0.28  # wierd offset to make it have the same height as single sphereflake
        izoff = (nz-1)/2

        x = (ix-ixoff) * extentvec[0] * gap * 2
        y = (iy-iyoff) * extentvec[1] * gap * 2
#         y = extentvec[1]
        z = (iz-izoff) * extentvec[2] * gap * 2
        return Gf.Vec3f(x, y, z)

    @staticmethod
    def GetLastGenTime():
        global latest_sf_gen_time
        return latest_sf_gen_time

    def SpawnBBcube(self, primpath, cenpt, extent, bbmatname):
        # stage = omni.usd.get_context().get_stage()
        stage = self._stage
        xformPrim = UsdGeom.Xform.Define(stage, primpath)
        UsdGeom.XformCommonAPI(xformPrim).SetTranslate((cenpt[0], cenpt[1], cenpt[2]))
        UsdGeom.XformCommonAPI(xformPrim).SetScale((extent[0], extent[1], extent[2]))
        cube = UsdGeom.Cube.Define(stage, primpath)
        mtl = self._matman.GetMaterial(bbmatname)
        UsdShade.MaterialBindingAPI(cube).Bind(mtl)
        return cube

    def GetSphereFlakeBoundingBox(self) -> Gf.Vec3f:
        # sz = rad  +  (1+(radratio))**depth # old method
        sz = self.p_rad
        nrad = sz
        for i in range(self.p_depth):
            nrad = self.p_radratio*nrad
            sz += 2*nrad
        return Gf.Vec3f(sz, sz, sz)

    def GetSphereFlakeBoundingBoxNxNyNz(self, gap: float = 1.1) -> Gf.Vec3f:
        # sz = rad  +  (1+(radratio))**depth # old method
        ext = self.GetSphereFlakeBoundingBox()
        fx = -1
        fy = -1
        fz = -1
        lx = self.p_nsfx
        ly = self.p_nsfy
        lz = self.p_nsfz
        lcorn = self.GetCenterPosition(fx, fy, fz, ext, gap)
        rcorn = self.GetCenterPosition(lx, ly, lz, ext, gap)
        rv = rcorn - lcorn
        return rv

    def RemoteInit(self, remoteurl):
        self.tasks = []
        if self.remotetype == "RemoteUrl":
            self.baseurl = remoteurl
            import aiohttp  # late import to keep it from dying at startup - probably a Kit 105 bug
            self.session = aiohttp.ClientSession()
        elif self.remotetype == "RemoteBatchFile":
            self.process_cmd_list = []
            self.urlname = "omniverse://localhost/Users/mike/SfBase.usda"
            self.sessname = "base1"
            if self.p_tag is None:
                hostname = socket.gethostname()
                datestr = time.datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
                self.p_tag = f"{hostname}-{datestr}"
            rlayer = self._stage.GetRootLayer()
            realpath = rlayer.identifier
            if realpath is not None:
                if realpath.startswith("omniverse://"):
                    self.urlname = realpath
                    from .sfsession import fish_out_session_name
                    self.sessname = fish_out_session_name(self._stage)
                    print(f"RemoteInit: urlname:{self.urlname} fished-out sessname:{self.sessname}")
                else:
                    carb.log_error(f"RemoteInit Error - stage is not from a nucleus session: {realpath}")

    async def RemoteFetch(self, sx, sy, sz, nx, ny, nz, nnx, nny, nnz):
        url = f"{self.baseurl}"
        url += f"?stagestr={self._stage}"
        url += f"&matname={self.p_sf_matname}"
        url += f"&sx={sx}&nx={nx}&nnx={nnx}"
        url += f"&sy={sy}&ny={ny}&nny={nny}"
        url += f"&sz={sz}&nz={nz}&nnz={nnz}"
        print(f"GMP sf_ - url:{url}")
        async with self.session.get(url) as response:
            return await response.text()

    def RemoteCreateTask(self, ib, sx, sy, sz, nx, ny, nz, nnx, nny, nnz):
        if self.remotetype == "RemoteUrl":
            t = asyncio.create_task(self.RemoteFetch(sx, sy, sz, nx, ny, nz, nnx, nny, nnz))
            t.add_done_callback(self.tasks.remove)
            self.tasks.append(t)
        elif self.remotetype == "RemoteBatchFile":
            cmd = f"start /b \"{ib}\" run_sfseeder -u {self.urlname} -n {self.sessname} -p "
            cmd += f"i={ib},matname={self.p_sf_matname},bbmatname={self.p_bb_matname}"
            cmd += f",sx={sx},nx={nx},nnx={nnx}"
            cmd += f",sy={sy},ny={ny},nny={nny}"
            cmd += f",sz={sz},nz={nz},nnz={nnz}"
            cmd += f",form={self.p_genform},mode={self.p_genmode},depth={self.p_depth}"
            cmd += f",rad={self.p_rad},radratio={self.p_radratio:.4f}"
            cmd += f",tag={self.p_tag},logdir=d:/nv/ov/log/"
            self.process_cmd_list.append(cmd)

    async def RemoteClose(self):
        print(f"GMP: sf_ waiting for tasks to complete ln:{len(self.tasks)}")
        rettxts = await asyncio.gather(*self.tasks)
        print(f"GMP: sf_ tasks {len(rettxts)} completed")
        i = 0
        for txt in rettxts:
            print(f"GMP: sf_ txt {i}:{txt}")
            i += 1
        if self.remotetype == "RemoteUrl":
            await self.session.close()
        elif self.remotetype == "RemoteBatchFile":
            cmds = "\n".join(self.process_cmd_list)
            path = "d:/nv/ov/app/ovcon/"
            filename = f"{path}sphereflake_cmdlist.bat"
            with open(filename, "w") as f:
                f.write(cmds)

    async def GenerateManyParallel(self, doremote: bool = False, remotetype: str = "---",
                                   remoteurl: str = "http://localhost:8211/sphereflake/build-sf-set"):
        nxchunk = math.ceil(self.p_nsfx / self.p_parallel_nxbatch)
        nychunk = math.ceil(self.p_nsfy / self.p_parallel_nybatch)
        nzchunk = math.ceil(self.p_nsfz / self.p_parallel_nzbatch)
        nnx = self.p_nsfx
        nny = self.p_nsfy
        nnz = self.p_nsfz
        print(f"GMP: nnx:{nnx} nny:{nny} nnz:{nnz} remote:{doremote} type:{remotetype} url:{remoteurl} (trc))")

        # realize all configured materials
        self._matman.GetMaterial(self.p_sf_matname)
        self._matman.GetMaterial(self.p_sf_alt_matname)
        self._matman.GetMaterial(self.p_bb_matname)

        original_matname = self.p_sf_matname
        original_alt_matname = self.p_sf_alt_matname

        omatname = self.p_sf_matname
        amatname = self.p_sf_alt_matname
        ibatch = 0
        sfcount = 0
        print(f"GenerateManyParallel: nxchunk:{nxchunk} nychunk:{nychunk} nzchunk:{nzchunk}")
        # available_trans_sync = omni.services.client.get_available_transports(is_async=False)
        # available_trans_async = omni.services.client.get_available_transports(is_async=True)
        # # availprot = omni.services.client.get_available_protocols()
        # client = omni.services.client.AsyncClient("http://localhost:8211/sphereflake")

        self._createlist = []
        self._bbcubelist = []
        if doremote:
            self.remotetype = remotetype
            self.RemoteInit(remoteurl)
        for iix in range(self.p_parallel_nxbatch):
            for iiy in range(self.p_parallel_nybatch):
                for iiz in range(self.p_parallel_nzbatch):
                    iixyz = iix + iiy + iiz
                    if iixyz % 2 == 0:
                        self.p_sf_matname = omatname
                    else:
                        self.p_sf_matname = amatname
                    print(f"   GenerateManyParallel: batch:{ibatch} mat:{self.p_sf_matname}")
                    sx = iix*nxchunk
                    sy = iiy*nychunk
                    sz = iiz*nzchunk
                    nx = nxchunk
                    ny = nychunk
                    nz = nzchunk
                    nnx = self.p_nsfx
                    nny = self.p_nsfy
                    nnz = self.p_nsfz
                    nx = min(nx, nnx-sx)
                    ny = min(ny, nny-sy)
                    nz = min(nz, nnz-sz)
                    if doremote:
                        self.RemoteCreateTask(ibatch, sx, sy, sz, nx, ny, nz, nnx, nny, nnz)
                        sfcount += nx*ny*nz
                    else:
                        sfcount += self.GenerateManySubcube(sx, sy, sz, nx, ny, nz)
                    ibatch += 1
        if doremote:
            await self.RemoteClose()

        self.p_sf_matname = original_matname
        self.p_sf_alt_matname = original_alt_matname
        return sfcount

    def GenerateMany(self):
        if self.p_partialRender:
            sx = self.p_partial_ssfx
            sy = self.p_partial_ssfy
            sz = self.p_partial_ssfz
            nx = self.p_partial_nsfx
            ny = self.p_partial_nsfy
            nz = self.p_partial_nsfz
        else:
            sx = 0
            sy = 0
            sz = 0
            nx = self.p_nsfx
            ny = self.p_nsfy
            nz = self.p_nsfz
        self._createlist = []
        self._bbcubelist = []
        sfcount = self.GenerateManySubcube(sx, sy, sz, nx, ny, nz)
        return sfcount

    def GenerateManySubcube(self, sx: int, sy: int, sz: int, nx: int, ny: int, nz: int) -> int:
        self.GenPrep()
        cpt = Gf.Vec3f(0, self.p_rad, 0)
        # extentvec = self.GetFlakeExtent(depth, self._rad, self._radratio)
        extentvec = self.GetSphereFlakeBoundingBox()
        count = self._count

        for iix in range(nx):
            for iiy in range(ny):
                for iiz in range(nz):
                    ix = iix+sx
                    iy = iiy+sy
                    iz = iiz+sz
                    count += 1
                    # primpath = f"/World/SphereFlake_{count}"
                    primpath = f"/World/SphereFlake_{ix}_{iy}_{iz}__{nx}_{ny}_{nz}"

                    cpt = self.GetCenterPosition(ix, iy, iz, extentvec)

                    self.Generate(primpath, cpt)
                    self._createlist.append(primpath)
                    bnd_cubepath = primpath+"/bounds"
                    bnd_cube = self.SpawnBBcube(bnd_cubepath, cpt, extentvec, self.p_bb_matname)
                    self._bbcubelist.append(bnd_cubepath)
                    if self.p_make_bounds_visible:
                        UsdGeom.Imageable(bnd_cube).MakeVisible()
                    else:
                        UsdGeom.Imageable(bnd_cube).MakeInvisible()
        return count

    def ToggleBoundsVisiblity(self, soll: bool):
        # print(f"ToggleBoundsVisiblity: {self._bbcubelist}")
        # okc.execute('ToggleVisibilitySelectedPrims', selected_paths=self._bbcubelist)
        for path in self._bbcubelist:
            prim = self._stage.GetPrimAtPath(path)
            if prim is not None:
                if soll:
                    # UsdGeom.Imageable(prim).MakeVisible()
                    UsdGeom.Imageable(prim).GetVisibilityAttr().Set('inherited')
                else:
                    UsdGeom.Imageable(prim).MakeInvisible()

    def Generate(self, sphflkname: str, cenpt: Gf.Vec3f):

        global latest_sf_gen_time

        self._start_time = time.time()
        self._total_quads = 0

        self._nring = 8
        # ovut.delete_if_exists(sphflkname)

        # stage = omni.usd.get_context().get_stage()
        stage = self._stage
        xformPrim = UsdGeom.Xform.Define(stage, sphflkname)
        UsdGeom.XformCommonAPI(xformPrim).SetTranslate((0, 0, 0))
        UsdGeom.XformCommonAPI(xformPrim).SetRotate((0, 0, 0))

        mxdepth = self.p_depth
        basept = cenpt
        matname = self.p_sf_matname
        self.GenRecursively(sphflkname, matname, mxdepth, self.p_depth, basept, cenpt, self.p_rad)

        elap = time.time() - self._start_time
        # print(f"GenerateSF {sphflkname} {matname} {depth} {cenpt} totquads:{self._total_quads} in {elap:.3f} secs")

        latest_sf_gen_time = elap

    def GenRecursively(self, sphflkname: str, matname: str, mxdepth: int, depth: int, basept: Gf.Vec3f,
                       cenpt: Gf.Vec3f, rad: float):

        # xformPrim = UsdGeom.Xform.Define(self._stage, sphflkname)
        # UsdGeom.XformCommonAPI(xformPrim).SetTranslate((0, 0, 0))
        # UsdGeom.XformCommonAPI(xformPrim).SetRotate((0, 0, 0))

        meshname = sphflkname + "/SphereMesh"

        # spheremesh = UsdGeom.Mesh.Define(self._stage, meshname)

        if self.p_genmode == "AsyncMesh":
            meshname = sphflkname + "/SphereMeshAsync"
            asyncio.ensure_future(self._smf.CreateMeshAsync(meshname, matname, cenpt,  rad))
        elif self.p_genmode == "DirectMesh":
            meshname = sphflkname + "/SphereMesh"
            self._smf.CreateMesh(meshname, matname, cenpt,  rad)
        elif self.p_genmode == "OmniSphere":
            import omni.kit.commands as okc
            meshname = sphflkname + "/OmniSphere"
            okc.execute('CreateMeshPrimWithDefaultXform',	prim_type="Sphere", prim_path=meshname)
            sz = rad/50  # 50 is the default radius of the sphere prim
            okc.execute('TransformMultiPrimsSRTCpp',
                        count=1,
                        paths=[meshname],
                        new_scales=[sz, sz, sz],
                        new_translations=[cenpt[0], cenpt[1], cenpt[2]])
            mtl = self._matman.GetMaterial(matname)
            # stage = omni.usd.get_context().get_stage()
            stage = self._stage
            prim: Usd.Prim = stage.GetPrimAtPath(meshname)
            UsdShade.MaterialBindingAPI(prim).Bind(mtl)
        elif self.p_genmode == "UsdSphere":
            meshname = sphflkname + "/UsdSphere"
            # stage = omni.usd.get_context().get_stage()
            stage = self._stage
            xformPrim = UsdGeom.Xform.Define(stage, meshname)
            sz = rad
            UsdGeom.XformCommonAPI(xformPrim).SetTranslate((cenpt[0], cenpt[1], cenpt[2]))
            UsdGeom.XformCommonAPI(xformPrim).SetScale((sz, sz, sz))
            spheregeom = UsdGeom.Sphere.Define(stage, meshname)
            mtl = self._matman.GetMaterial(matname)
            UsdShade.MaterialBindingAPI(spheregeom).Bind(mtl)
            # print(f"GenRecursively - equipforphysics: {self.p_equipforphysics}")
            if self.p_equipforphysics:
                spherePrim = stage.GetPrimAtPath(meshname)
                rigid_api = UsdPhysics.RigidBodyAPI.Apply(spherePrim)
                # rigid_api.SetMassAttr(1.0)
                # rigid_api.SetRestitutionAttr(0.5)
                rigid_api.CreateRigidBodyEnabledAttr(True)
                UsdPhysics.CollisionAPI.Apply(spherePrim)

        if depth > 0:
            form = self.p_genform
            if form == "Classic":
                thoff = 0
                phioff = -20*math.pi/180
                self._nring = 6
                self.GenRing(sphflkname, "r1", matname, mxdepth, depth, basept, cenpt, 6, rad, thoff, phioff)

                thoff = 30*math.pi/180
                phioff = 55*math.pi/180
                self._nring = 3
                self.GenRing(sphflkname, "r2", matname, mxdepth, depth, basept, cenpt, 3, rad, thoff, phioff)
            else:
                thoff = 0
                phioff = 0
                self._nring = 8
                self.GenRing(sphflkname, "r1", matname, mxdepth, depth, basept, cenpt, self._nring, rad, thoff, phioff)

    def GenRing(self, sphflkname: str, ringname: str, matname: str, mxdepth: int, depth: int,
                basept: Gf.Vec3f, cenpt: Gf.Vec3f,
                nring: int, rad: float,
                thoff: float, phioff: float):
        offvek = cenpt - basept
        len = offvek.GetLength()
        if len > 0:
            lxax = cross_product(offvek, self._yax)
            if lxax.GetLength() == 0:
                lxax = cross_product(offvek, self._zax)
            lxax.Normalize()
            lzax = cross_product(offvek, lxax)
            lzax.Normalize()
            lyax = offvek
            lyax.Normalize()
        else:
            lxax = self._xax
            lyax = self._yax
            lzax = self._zax
        nrad = rad * self.p_radratio
        offfak = 1 + self.p_radratio
        sphi = math.sin(phioff)
        cphi = math.cos(phioff)
        for i in range(nring):
            theta = thoff + (i*2*math.pi/nring)
            x = cphi*rad*math.sin(theta)
            y = sphi*rad
            z = cphi*rad*math.cos(theta)
            npt = x*lxax + y*lyax + z*lzax
            subname = f"{sphflkname}/{ringname}_sf_{i}"
            self.GenRecursively(subname, matname, mxdepth, depth-1, cenpt, cenpt+offfak*npt, nrad)
