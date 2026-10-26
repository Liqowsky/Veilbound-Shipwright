"""VEILBOUND Cove v2: COMPLETE REBUILD. Script creates a NEW Blender scene.
No assets or meshes from the previous flat-cliff scene are loaded.
Usage: blender -b -t 4 --python tools/vaeloria_cove_v2.py
"""
import bpy, math, random, os
from pathlib import Path
from mathutils import Vector
R=random.Random(4421)
bpy.ops.object.select_all(action="SELECT");bpy.ops.object.delete(use_global=False)
out=Path(os.getenv("VAELORIA_OUT","/tmp/vaeloria_v2"));out.mkdir(parents=True,exist_ok=True)
def material(name,col,emit=0):
 m=bpy.data.materials.new(name);m.diffuse_color=(*col,1);m.use_nodes=True
 bs=m.node_tree.nodes.get("Principled BSDF");bs.inputs["Base Color"].default_value=(*col,1);bs.inputs["Roughness"].default_value=.85
 if emit and "Emission" in bs.inputs:bs.inputs["Emission"].default_value=(*col,1)
 if emit and "Emission Color" in bs.inputs:bs.inputs["Emission Color"].default_value=(*col,1)
 if emit:bs.inputs["Emission Strength"].default_value=emit
 return m
sand=material("Gold sand",(0.78,.42,.19));stone=material("Vermilion red sandstone",(.56,.22,.11))
highlight=material("Sunlit sandstone",(.9,.48,.23));plaster=material("Warm cream stucco",(.95,.78,.53))
wood=material("Dark dock timber",(.3,.13,.06));tile=material("Sunbaked terracotta",(.59,.19,.11))
sea=material("Turquoise bay",(.025,.45,.56));foam=material("Crest foam",(.75,.96,.86))
dark=material("Shadowed doorway",(.10,.085,.075));crystal=material("Emerald",(.05,.9,.45),5);lamp=material("Beacon",(1,.58,.17),7)
def mesh(name,v,f,mat):
 me=bpy.data.meshes.new(name);me.from_pydata(v,[],f);me.update();ob=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(ob);ob.data.materials.append(mat);return ob
def cube(n,p,sz,ma):
 bpy.ops.mesh.primitive_cube_add(size=1,location=p);o=bpy.context.object;o.name=n;o.dimensions=sz;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(ma);return o
def cyl(n,p,r,d,ma,nverts=12):
 bpy.ops.mesh.primitive_cylinder_add(vertices=nverts,radius=r,depth=d,location=p);o=bpy.context.object;o.name=n;o.data.materials.append(ma);return o
def cone(n,p,r,d,ma):
 bpy.ops.mesh.primitive_cone_add(vertices=10,radius1=r,radius2=r*.52,depth=d,location=p);o=bpy.context.object;o.name=n;o.data.materials.append(ma);return o
# The bay is open to the SUNSET behind it, rather than a straight channel.
# Coordinate system: x left/right, y distance toward horizon, z elevation.
cube("SEA continuous turquoise bay",(0,65,-2.5),(270,370,.4),sea)
# Each cape is a 2D height-field mesh; no walls or hanging slabs.
def cape(side):
 W=48;H=76;verts=[];faces=[]
 for j in range(H):
  t=j/(H-1);y=-78+t*240
  center=side*(53+10*math.sin(t*2.9)+7*math.sin(t*7.2))
  for i in range(W):
   u=i/(W-1)
   x=center+side*u*112
   # Near shoreline cliff rising dramatically; plateau inland.
   shore_rise=max(0,min(1,u/.19))
   shore_rise=shore_rise*shore_rise*(3-2*shore_rise)
   cliff= (20 if side<0 else 43)*(0.77+.19*math.sin(t*4.0)+.10*math.sin(t*9))
   terrace=(2 if side<0 else 3)*math.sin(u*11+t*7)*math.sin(math.pi*u)
   z=-2+shore_rise*(cliff+2)+terrace
   verts.append((x,y,z))
   if i and j:
    a=(j-1)*W+i-1;b=j*W+i-1
    faces.extend([(a,b,a+1),(a+1,b,b+1)])
 o=mesh(("WEST VILLAGE COAST" if side<0 else "EAST LIGHTHOUSE HEADLAND"),verts,faces,sand if side<0 else stone)
 sub=o.modifiers.new("Soften weathered coast","SUBSURF");sub.levels=1;sub.render_levels=1
 return o
cape(-1);cape(1)
# Main scene landmarks placed against the left and right banks.
def house(n,x,y,z,w,d,h):
 cube(n+" walls",(x,y,z+h*.5),(w,d,h),plaster)
 verts=[(x-w*.6,y-d*.6,z+h),(x+w*.6,y-d*.6,z+h),(x+w*.6,y+d*.6,z+h),(x-w*.6,y+d*.6,z+h),(x,y-d*.6,z+h+3),(x,y+d*.6,z+h+3)]
 mesh(n+" handmade pitched roof",verts,[(0,1,4),(3,5,2),(0,4,5,3),(1,2,5,4)],tile)
 cube(n+" carved door",(x,y-d/2-.25,z+3),(2.6,.3,5),wood)
 for dx in [-w*.3,w*.3]:
  cube(n+" window",(x+dx,y-d/2-.3,z+6.7),(1.6,.25,2.4),dark)
for n,x,y,z,w,d,h in [
 ("FAMILY_HOME",-106,-19,21,27,21,14),
 ("FISHERMAN",-85,28,19,14,12,10),
 ("STORE",-95,67,22,17,12,10),
 ("INN",-87,99,22,14,12,10),
 ("SALT_WAREHOUSE",-71,44,16,13,11,8)]:
 house(n,x,y,z,w,d,h)
# Non-rectangular lighthouse promontory extends into the bay on right.
# Upright tower with rings and bright turret, away from image border.
cyl("LIGHTHOUSE conical masonry",(95,64,56),6,42,plaster,16)
for zz in (37,48,68,78):
 cyl("LIGHTHOUSE sandstone trim",(95,64,zz),7,.85,highlight,16)
cyl("LIGHTHOUSE lantern room",(95,64,81),7.3,7,dark,12)
cyl("LIGHTHOUSE glowing lens",(95,64,81),3.0,5,lamp,12)
cone("LIGHTHOUSE terracotta cap",(95,64,87),9,5,tile)
# Cave entrance has a curved stone arch on the cliff facing the viewer.
cube("CAVE DARK MOUTH",(72,-27,9),(1.5,19,15),dark)
for i in range(15):
 a=math.pi*i/14
 cyl("CAVE arch block %02d"%i,(69,-27+10*math.cos(a),9+11*math.sin(a)),3,4,highlight,7)
for i in range(12):
 cone("CAVE EMERALD %02d"%i,(69,-28+R.uniform(-6,6),2+R.uniform(0,9)),R.uniform(.5,1.5),R.uniform(2,6),crystal)
# Actual layered coastline stones, not 100 identical floating shards.
def boulder(n,pos,scale):
 bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2,location=pos)
 o=bpy.context.object;o.name=n;o.scale=scale;o.rotation_euler=(R.random()*.5,R.random()*.6,R.random()*6);o.data.materials.append(stone if R.random()<.65 else highlight)
for i in range(75):
 side=-1 if i%2 else 1
 yy=R.uniform(-65,145);xx=side*R.uniform(50,92)
 boulder("COAST rounded rock %02d"%i,(xx,yy,R.uniform(1,10)),(R.uniform(2,6),R.uniform(2,6),R.uniform(1.3,5)))
for i in range(15):
 boulder("BAY sea stack %02d"%i,(R.uniform(-30,35),R.uniform(-35,145),-.9),(R.uniform(1.7,4),R.uniform(2,5),R.uniform(2,6)))
# Wharf and its support piles.
for i in range(12):
 x=-45+i*1.8
 cube("OLD PIER plank %02d"%i,(x,-20,1),(1.6,20,.6),wood)
 if i%3==0:
  cyl("PIER support %02d"%i,(x,-20,-1),.4,5,wood)
# Shallow surf only in bay, no black-screen geometry.
for i in range(75):
 xx=R.uniform(-50,50);yy=R.uniform(-65,85)
 cube("SURF %02d"%i,(xx,yy,-2.17),(R.uniform(1,4),.08,.03),foam)
# A sun disc geometry and backdrop haze, both REAL geometry.
sun=material("Sunset sun disc",(1,.64,.26),4)
bpy.ops.mesh.primitive_uv_sphere_add(segments=32,ring_count=16,radius=16,location=(0,225,27))
bpy.context.object.name="SUN OVER DISTANT SEA";bpy.context.object.data.materials.append(sun)
# Framing: camera must see village roof at left, turquoise water middle, entire tower at right.
bpy.ops.object.camera_add(location=(0,-188,68));camera=bpy.context.object
def aim(obj,target):obj.rotation_euler=(Vector(target)-obj.location).to_track_quat("-Z","Y").to_euler()
aim(camera,(0,36,32));camera.data.type="PERSP";camera.data.lens=29
bpy.context.scene.camera=camera
bpy.ops.object.light_add(type="SUN",location=(-80,145,100))
sunlight=bpy.context.object;sunlight.data.energy=2.8;sunlight.data.color=(1,.57,.29);aim(sunlight,(0,0,0))
for name,power,pos,color in [("Cave green",2000,(65,-25,10),(.05,1,.4)),("Tower light",1300,(95,64,81),(1,.67,.27))]:
 bpy.ops.object.light_add(type="POINT",location=pos);o=bpy.context.object;o.name=name;o.data.energy=power;o.data.color=color
world=bpy.data.worlds.new("Gold hour");world.use_nodes=True;world.node_tree.nodes["Background"].inputs["Color"].default_value=(.42,.25,.22,1);world.node_tree.nodes["Background"].inputs["Strength"].default_value=.8;bpy.context.scene.world=world
sc=bpy.context.scene;sc.render.engine="CYCLES";sc.cycles.samples=24
sc.cycles.use_denoising=False
for layer in sc.view_layers:
 if hasattr(layer,"cycles"):layer.cycles.use_denoising=False
sc.render.resolution_x=1600;sc.render.resolution_y=900;sc.render.resolution_percentage=100
sc.view_settings.view_transform="Standard"
bpy.ops.wm.save_as_mainfile(filepath=str(out/"VAELORIA_COVE_V2.blend"))
sc.render.filepath=str(out/"VAELORIA_COVE_V2_RENDER.png")
bpy.ops.render.render(write_still=True)
print("COMPLETE NEW COVE",len(bpy.data.objects))
