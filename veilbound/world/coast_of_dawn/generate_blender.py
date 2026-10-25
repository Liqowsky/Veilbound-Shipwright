"""VEILBOUND: blockout pustynnego wybrzeża w dwóch epokach.
Blender 4.x: Scripting > Run Script. Saves nothing and does not modify SoH.
Coordinates are in metres; visual blockout only (NOT playable yet).
"""
import bpy
import math
from mathutils import Vector

# Explicitly reset scene; user should run in a new Blender file.
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
for col in list(bpy.data.collections):
    if col.name != bpy.context.scene.collection.name and col.users == 0:
        bpy.data.collections.remove(col)

def collection(name):
    c = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(c)
    return c

shared = collection("SHARED_TERRAIN")
past = collection("PAST_DESERT")
future = collection("FUTURE_SNOW_25Y")
markers = collection("LANDMARK_MARKERS")

def mat(name, color, rough=1):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1.0)
    m.use_nodes = True
    principled = m.node_tree.nodes.get("Principled BSDF")
    principled.inputs["Base Color"].default_value = (*color, 1.0)
    principled.inputs["Roughness"].default_value = rough
    return m

sand = mat("PAST | golden sand", (.66,.42,.18))
rock = mat("SHARED | terracotta rock", (.41,.23,.17))
water = mat("SHARED | turquoise sea", (.03,.30,.39), .25)
sandstone = mat("PAST | sandstone houses", (.71,.53,.30))
timber = mat("PAST | dark wood", (.26,.16,.10))
roof = mat("PAST | red clay rooftops", (.56,.22,.13))
snow = mat("FUTURE | pale snow", (.77,.87,.91))
ice = mat("FUTURE | sea ice", (.33,.65,.75), .22)
ash = mat("FUTURE | ruined stone", (.39,.46,.46))
emerald = mat("SHARED | rift accent", (.02,.9,.50), .3)

def relocate(obj, coll):
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    coll.objects.link(obj)
    return obj

def cube(name, pos, scale, material, coll, bevel=0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=pos)
    o = bpy.context.object
    o.name = name
    o.dimensions = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    o.data.materials.append(material)
    relocate(o, coll)
    if bevel:
        mod=o.modifiers.new("stylized chunky corners","BEVEL")
        mod.width=bevel
        mod.segments=1
        o.modifiers.new("weighted normals","WEIGHTED_NORMAL")
    return o

def cylinder(name, pos, radius, depth, material, coll, verts=12):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=radius, depth=depth, location=pos)
    o=bpy.context.object; o.name=name
    o.data.materials.append(material)
    relocate(o, coll)
    return o

def cone(name, pos, r1, r2, depth, material, coll, verts=4):
    bpy.ops.mesh.primitive_cone_add(vertices=verts, radius1=r1, radius2=r2, depth=depth, location=pos)
    o=bpy.context.object; o.name=name
    o.data.materials.append(material)
    relocate(o, coll)
    return o

# Sea stays to the west. A raised sandy coast rises to the east.
def terrain_height(x,y):
    coast = 11 + 4 * math.sin(y/38.0)
    shore = max(0.0, min(1.0, (x+30)/35))
    dune = 4.0 * math.sin(x/23.0)*math.cos(y/34.0)
    headland = 13.0 * math.exp(-((x-38)/31)**2 - ((y-86)/29)**2)
    return 1.0 + 14 * shore + shore * dune + headland

N = 48
verts=[]; faces=[]
for j in range(N+1):
    y=-130+260*j/N
    for i in range(N+1):
        x=-160+320*i/N
        verts.append((x,y,terrain_height(x,y)))
for j in range(N):
    for i in range(N):
        a=j*(N+1)+i
        faces.append((a,a+1,a+N+2,a+N+1))
mesh=bpy.data.meshes.new("base_coast_mesh")
mesh.from_pydata(verts,[],faces)
mesh.update()
obj=bpy.data.objects.new("Coastline | shared walkable geometry prototype",mesh)
shared.objects.link(obj)
obj.data.materials.append(sand)
cube("Sea | water surface",(-120,0,0),(165,290,.5),water,shared)

def building(prefix, x,y, w,d,h, coll, ruin=False):
    z=terrain_height(x,y)
    wall_mat = ash if ruin else sandstone
    wall_h = h*.53 if ruin else h
    cube(prefix+" | masonry",(x,y,z+wall_h/2),(w,d,wall_h),wall_mat,coll,bevel=.5)
    if not ruin:
        # Overhanging chunky red roof; no photoreal detail.
        cone(prefix+" | roof",(x,y,z+h+2.2),max(w,d)*.72,0,4.4,roof,coll,verts=4)
        cube(prefix+" | door",(x,y-d/2-.08,z+2),(2,.22,4),timber,coll)
    else:
        cube(prefix+" | fallen wall",(x+w*.45,y,z+.5),(w*.5,d*.8,1.0),ash,coll,bevel=.3)
        cube(prefix+" | snow cover",(x,y,z+wall_h+.45),(w+.9,d+.9,.8),snow,coll)

building("Family home",42,88,17,13,12,past)
building("Family home ruin",42,88,17,13,12,future,ruin=True)
for idx,(x,y) in enumerate([(77,24),(97,17),(62,1),(88,-8),(53,39)]):
    building(f"Village {idx+1:02}",x,y,12,10,9,past)
    building(f"Village ruin {idx+1:02}",x,y,12,10,9,future,ruin=True)

def lighthouse(coll, frozen=False):
    x,y=-80,28
    z=terrain_height(x,y)
    cylinder("Lighthouse | tower", (x,y,z+17),6.5,34,ash if frozen else sandstone,coll,verts=12)
    cylinder("Lighthouse | crown", (x,y,z+35),9,3,ice if frozen else roof,coll,verts=12)
    cylinder("Lighthouse | lantern", (x,y,z+39),4,5,ice if frozen else emerald,coll,verts=12)
    if frozen:
        cone("Lighthouse | snow cone",(x,y,z+43),6,0,5,snow,coll,verts=12)
lighthouse(past)
lighthouse(future,True)

# Cave entrance: horseshoe built as actual arch pieces, hollow at center.
def cave(coll,frozen=False):
    x,y=-49,-56
    z=terrain_height(x,y)
    material=ice if frozen else rock
    cube("Cave | left buttress",(x-7,y,z+5),(4,7,10),material,coll,bevel=1)
    cube("Cave | right buttress",(x+7,y,z+5),(4,7,10),material,coll,bevel=1)
    cube("Cave | lintel",(x,y,z+11),(19,7,4),material,coll,bevel=1)
    if frozen:
        cone("Cave | icicle",(x,y,z+8),2,.01,7,ice,coll,verts=8)
cave(past)
cave(future,True)

# Stylized dunes, and their snowdrift counterparts: same coordinates.
for i,(x,y,r) in enumerate([(104,-80,20),(132,-23,15),(37,-74,14),(110,91,14)]):
    z=terrain_height(x,y)
    cone(f"Dune {i+1}",(x,y,z+2),r,0,6,sand,past,verts=9)
    cone(f"Snowdrift {i+1}",(x,y,z+2),r,0,6.5,snow,future,verts=9)
cube("Winter coastline | shelf ice",(-116,-89,1),(145,70,1.3),ice,future)

# View target and start markers, intentionally separate from terrain collision.
for name,x,y in [("START | childhood",37,63),("START | 25 years later",-97,-90),
                 ("Lighthouse landmark",-80,28),("Cave landmark",-49,-56)]:
    z=terrain_height(x,y)
    cylinder(name,(x,y,z+1),1.7,2,emerald,markers)

# Stage each epoch as collection toggle, do not delete data.
future.hide_viewport=True
future.hide_render=True

world=bpy.context.scene.world
world.color=(.10,.11,.12)
bpy.ops.object.camera_add(location=(175,-265,170))
camera=bpy.context.object
direction=Vector((12,0,8))-camera.location
camera.rotation_euler=direction.to_track_quat("-Z","Y").to_euler()
bpy.context.scene.camera=camera
camera.data.type="ORTHO"
camera.data.ortho_scale=400

bpy.context.scene.render.resolution_x=1920
bpy.context.scene.render.resolution_y=1080
bpy.context.scene.render.resolution_percentage=100
print("VEILBOUND coastline blockout generated: toggle PAST_DESERT / FUTURE_SNOW_25Y to inspect epochs.")
