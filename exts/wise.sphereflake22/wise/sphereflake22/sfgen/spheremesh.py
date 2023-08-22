import math
import numpy as np
from pxr import Gf, Sdf, Usd, UsdGeom, UsdShade, Vt
from .sfut import MatMan


class SphereMeshFactory():

    _show_normals = False
    _matman: MatMan = None
    p_nlat = 8
    p_nlng = 8
    _total_quads = 0
    _dotexcoords = True

    def __init__(self, stage: Usd.Stage, matman: MatMan) -> None:
        self._matman = matman
        self._stage = stage
        # self._stageid = stageid
        # if stageid>0:
        #     self._stage = omni.usd.get_context().
        # else:
        #     self._stage = omni.usd.get_context().get_stage()

    def GenPrep(self):
        self._nquads = self.p_nlat*self.p_nlng
        self._nverts = (self.p_nlat+1)*(self.p_nlng)
        self._normbuf = np.zeros((self._nverts, 3), dtype=np.float32)
        self._txtrbuf = np.zeros((self._nverts, 2), dtype=np.float32)
        self._facebuf = np.zeros((self._nquads, 1), dtype=np.int32)
        self._vidxbuf = np.zeros((self._nquads, 4), dtype=np.int32)
        self.MakeArrays()

    def Clear(self):
        pass

    def MakeMarker(self, name: str, matname: str, cenpt: Gf.Vec3f, rad: float):
        primpath = f"/World/markers/{name}"
        # stage = omni.usd.get_context().get_stage()
        stage = self._stage
        xformPrim = UsdGeom.Xform.Define(stage, primpath)
        sz = rad
        UsdGeom.XformCommonAPI(xformPrim).SetTranslate((cenpt[0], cenpt[1], cenpt[2]))
        UsdGeom.XformCommonAPI(xformPrim).SetScale((sz, sz, sz))
        spheremesh = UsdGeom.Sphere.Define(stage, primpath)
        mtl = self._matman.GetMaterial(matname)
        UsdShade.MaterialBindingAPI(spheremesh).Bind(mtl)

    def MakeArrays(self):
        nlat = self.p_nlat
        nlong = self.p_nlng
        for i in range(nlat):
            offset = i * nlong
            for j in range(nlong):
                if j < nlong - 1:
                    i1 = offset+j
                    i2 = offset+j+1
                    i3 = offset+j+nlong+1
                    i4 = offset+j+nlong
                else:
                    i1 = offset+j
                    i2 = offset
                    i3 = offset+nlong
                    i4 = offset+j+nlong
                vidx = i*nlong+j
                self._facebuf[vidx] = 4
                self._vidxbuf[vidx] = [i1, i2, i3, i4]

        polegap = 0.01  # prevents the vertices from being exactly on the poles
        for i in range(nlat+1):
            theta = polegap + (i * (math.pi-2*polegap) / float(nlat))
            st = math.sin(theta)
            ct = math.cos(theta)
            for j in range(nlong):
                phi = j * 2 * math.pi / float(nlong)
                sp = math.sin(phi)
                cp = math.cos(phi)
                nx = st*cp
                ny = ct
                nz = st*sp
                nrmvek = Gf.Vec3f(nx, ny, nz)
                vidx = i*nlong+j
                self._normbuf[vidx] = nrmvek
                self._txtrbuf[vidx] = (nx, ny)
        #  print("MakeArrays done")

    def ShowNormals(self, vertbuf):
        nlat = self.p_nlat
        nlong = self.p_nlng
        for i in range(nlat+1):
            for j in range(nlong):
                vidx = i*nlong+j
                ptname = f"ppt_{i}_{j}"
                (x, y, z) = vertbuf[vidx]
                (nx, ny, nz) = self._nromtbuf[vidx]
                pt = Gf.Vec3f(x, y, z)
                npt = Gf.Vec3f(x+nx, y+ny, z+nz)
                nmname = f"npt_{i}_{j}"
                self.MakeMarker(ptname, "red", pt, 1)
                self.MakeMarker(nmname, "blue", npt, 1)

    def CreateMesh(self, name: str, matname: str, cenpt: Gf.Vec3f, radius: float):
        # This will create nlat*nlog quads or twice that many triangles
        # it will need nlat+1 vertices in the latitude direction and nlong vertices in the longitude direction
        # so a total of (nlat+1)*(nlong) vertices

        # stage = omni.usd.get_context().get_stage()
        stage = self._stage
        spheremesh = UsdGeom.Mesh.Define(stage, name)

        # note that vertbuf is local to this function allowing it to be changed in a multithreaded environment
        vertbuf = self._normbuf*radius + cenpt

        if self._show_normals:
            self.ShowNormals(vertbuf)

        if self._dotexcoords:
            texCoords = UsdGeom.PrimvarsAPI(spheremesh).CreatePrimvar("st",
                                                                      Sdf.ValueTypeNames.TexCoord2fArray,
                                                                      UsdGeom.Tokens.varying)
            texCoords.Set(Vt.Vec2fArray.FromNumpy(self._txtrbuf))

        spheremesh.CreatePointsAttr(Vt.Vec3dArray.FromNumpy(vertbuf))
        spheremesh.CreateNormalsAttr(Vt.Vec3dArray.FromNumpy(self._normbuf))
        spheremesh.CreateFaceVertexCountsAttr(Vt.IntArrayFromBuffer(self._facebuf))
        spheremesh.CreateFaceVertexIndicesAttr(Vt.IntArrayFromBuffer(self._vidxbuf))

        mtl = self._matman.GetMaterial(matname)
        UsdShade.MaterialBindingAPI(spheremesh).Bind(mtl)

        self._total_quads += self._nquads  # face vertex counts

        return None

    async def CreateVertBuf(self, radius, cenpt):
        vertbuf = self._normbuf*radius + cenpt
        return vertbuf

    async def CreateStuff(self, spheremesh, vertbuf, normbuf, facebuf, vidxbuf):
        spheremesh.CreatePointsAttr(Vt.Vec3dArray.FromNumpy(vertbuf))
        spheremesh.CreateNormalsAttr(Vt.Vec3dArray.FromNumpy(normbuf))
        spheremesh.CreateFaceVertexCountsAttr(Vt.IntArrayFromBuffer(facebuf))
        spheremesh.CreateFaceVertexIndicesAttr(Vt.IntArrayFromBuffer(vidxbuf))
        return

    async def CreateMeshAsync(self, name: str, matname: str, cenpt: Gf.Vec3f, radius: float):
        # This will create nlat*nlog quads or twice that many triangles
        # it will need nlat+1 vertices in the latitude direction and nlong vertices in the longitude direction
        # so a total of (nlat+1)*(nlong) vertices

        # stage = omni.usd.get_context().get_stage()
        stage = self._stage

        spheremesh = UsdGeom.Mesh.Define(stage, name)

        # note that vertbuf is local to this function allowing it to be changed in a multithreaded environment
        vertbuf = await self.CreateVertBuf(radius, cenpt)

        if self._show_normals:
            self.ShowNormals(vertbuf)

        if self._dotexcoords:
            texCoords = UsdGeom.PrimvarsAPI(spheremesh).CreatePrimvar("st",
                                                                      Sdf.ValueTypeNames.TexCoord2fArray,
                                                                      UsdGeom.Tokens.varying)
            texCoords.Set(Vt.Vec2fArray.FromNumpy(self._txtrbuf))

        await self.CreateStuff(spheremesh, vertbuf, self._normbuf, self._facebuf, self._vidxbuf)

        mtl = self._matman.GetMaterial(matname)
        UsdShade.MaterialBindingAPI(spheremesh).Bind(mtl)

        self._total_quads += self._nquads  # face vertex counts

        return None
