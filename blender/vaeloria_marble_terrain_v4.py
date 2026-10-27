"""VEILBOUND Vaeloria V4: Marble-reference terrain. ONLY land, cave, routes, ocean.
Run: blender -b --python blender/vaeloria_marble_terrain_v4.py
"""
import bpy, math, os, random
from mathutils import Vector
from pathlib import Path
from math import sin,cos,pi,exp,sqrt
random.seed(62)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
O=Path(os.environ.get("VAELORIA_OUT","/tmp/vaeloria_marble_v4"));O.mkdir(parents=True,exist_ok=True)
def mat(n,c):
 m=bpy.data.materials.new(n);m.diffuse_color=(*c,1);m.use_nodes=True
 m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(*c,1)
 return m
rock=mat("Canyon layered red stone",(.49,.235,.135))
rockside=mat("Cliff shade",(.36,.16,.11))
sand=mat("Beach ochre",(.79,.51,.26))
trail=mat("Connected walkable route",(.95,.79,.49))
ocean=mat("Lagoon water",(.025,.37,.48))
mouth=mat("Cave opening",(.025,.045,.04))
def obj(name,vertices,faces,material):
 me=bpy.data.meshes.new(name);me.from_pydata(vertices,[],faces);me.update()
 o=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(o);me.materials.append(material)
 return o
def strip(name,edge,outer,height,material,flat_depth=0.22):
 # Vertical walls with rock-cut terraces; unlike a heightfield, faces can overhang.
 N=112;V=[];F=[]
 for i in range(N+1):
  t=i/N;y=-78+197*t
  x=edge(y);far=outer(y)
  h=height(y)
  # Coastal wall segmented at levels for geology, land is behind the cliff.
  for u,z in [(0,-2.2),(.015,1),(.04,h*.31),(.08,h*.35),(.075,h*.68),(.16,h*.73),
              (.17,h*.91),(.25,h),(1,h+.55*sin(y*.12))]:
   V.append((x+(far-x)*u,y,z+.6*sin(y*.12+u*11)*u))
  if i:
   for j in range(8):
    a=(i-1)*9+j;b=i*9+j
    F.append((a,b,b+1,a+1))
 return obj(name,V,F,material)
# Looking toward +Y. Left village shelf starts low, right high headland 28-36m.
strip("LEFT sandstone terraces",lambda y:-49-8*sin((y+60)*.027),
      lambda y:-132,lambda y:11+2.1*sin(y*.032),sand)
strip("RIGHT HIGH CLIFF with vertical rock face",lambda y:49+8*sin((y+55)*.031),
      lambda y:133,lambda y:31+3*sin(y*.024),rock)
# Wide foreground continuous beach wraps around the back of ROUND COVE.
V=[];F=[];NX=105;NY=35
for j in range(NY+1):
 t=j/NY;y=-101+38*t
 for i in range(NX+1):
  u=i/NX;x=-130+260*u
  # Height beach gently increases inland; seamless at inner lagoon margin
  z=-1.4+3.4*(1-t)**1.5+1.1*(abs(x)/130)**2
  V.append((x,y,z))
  if i and j:
   a=(j-1)*(NX+1)+i-1;b=j*(NX+1)+i-1;F.append((a,b,b+1,a+1))
obj("ROUND BAY REAR CONNECTING BEACH",V,F,sand)
# Natural outer headlands taper outward to the horizon; sea corridor stays open.
# Cut-in CAVE physically created by arch with visible inward tunnel, not glow stuck on hillside.
def arc_rock(name,center,r,thickness,depth,material):
 cx,cy,cz=center;segs=28;v=[];f=[]
 for zdepth in (0,depth):
  for i in range(segs+1):
   a=pi*i/segs
   for rad in (r,r+thickness):
    v.append((cx+zdepth,cy+rad*cos(a),cz+rad*sin(a)))
 for k in range(segs):
  for ring in (0,1):
   base=ring*2*(segs+1)+2*k
   f.append((base,base+2,base+3,base+1))
 for k in range(2*(segs+1)-2):
  f.append((k,k+2,k+2+2*(segs+1),k+2*(segs+1)))
 return obj(name,v,f,material)
arc_rock("CAVE real stone arch carved into east cliff",(52,-31,3),10,3,9,rockside)
# Deep cave floor and ceiling are geometry, black rear wall reinforces its depth.
V=[(52,-41,-1),(43,-41,-1),(43,-21,-1),(52,-21,-1)]
obj("CAVE walkable floor",V,[(0,1,2,3)],sand)
V=[(42,-40,0),(42,-22,0),(42,-22,15),(42,-40,15)]
obj("CAVE shadow back wall",V,[(0,1,2,3)],mouth)
# Actual right terrace switchback segments are wide rock-cut walkable roads with retaining walls.
def right_height(x,y):
 return 31+3*sin(y*.024)-max(0,(73-x))*.48
route=[(82,-74),(106,-60),(111,-44),(93,-30),(82,-17),(107,-4),(112,15),(93,32),(100,58),(96,78)]
# Monotonic walkable road elevation (4m -> summit 33m), gentle gradients
positions=[]
for j,(a,b) in enumerate(zip(route,route[1:])):
 for i in range(14):
  t=i/14;xy=Vector(a).lerp(Vector(b),t)
  s=(j+t)/(len(route)-1)
  positions.append((xy.x,xy.y,4.2+29.2*s))
positions.append((*route[-1],33.4))
def road(name,pts,width,matr):
 v=[];f=[]
 for i,p in enumerate(pts):
  a=Vector(pts[max(0,i-1)][:2]);b=Vector(pts[min(len(pts)-1,i+1)][:2])
  d=b-a;d.normalize();side=Vector((-d.y,d.x))
  for s in (-1,1):v.append((p[0]+side.x*s*width*.5,p[1]+side.y*s*width*.5,p[2]))
  if i:f.append((2*i-2,2*i-1,2*i+1,2*i))
 return obj(name,v,f,matr)
road("RIGHT CARVED SWITCHBACK PATH TO LIGHTHOUSE",positions,5.8,trail)
# Rear rim route visibly joins the settlement plateau and right switchback entry.
bridge=[(-105,-76,4),(-80,-87,3),(-40,-94,2.5),(0,-94,2.3),(38,-94,2.9),(64,-86,3.4),(82,-74,4.2)]
segments=[]
for a,b in zip(bridge,bridge[1:]):
 for k in range(12):
  t=k/12;segments.append(tuple(a[n]*(1-t)+b[n]*t for n in range(3)))
segments.append(bridge[-1])
road("VILLAGE to LIGHTHOUSE CONTINUOUS LINK",segments,6.3,trail)
# Islands, grounded rounded mass protruding from lagoon
def island(n,cx,cy,rx,ry,h):
 nring=13;N=60;v=[];f=[]
 for j in range(nring+1):
  t=j/nring
  for i in range(N):
   a=2*pi*i/N;scale=1+.07*sin(7*a+n)+.05*sin(3*a-n)
   v.append((cx+rx*t*cos(a)*scale,cy+ry*t*sin(a)*scale,-2.05+h*(1-t*t)**1.4))
 for j in range(nring):
  for i in range(N):
   a=j*N+i;b=j*N+(i+1)%N;f.append((a,b,b+N,a+N))
 return obj("COVE ISLAND "+str(n),v,f,rock)
for n,x,y,rx,ry,h in [(1,-10,-14,9,6,9),(2,17,16,6,8,14),(3,-23,41,4,6,8)]:island(n,x,y,rx,ry,h)
# A simple sea plane is a measuring surface only.
bpy.ops.mesh.primitive_plane_add(size=2,location=(0,0,-2.20))
o=bpy.context.object;o.name="SEA guide";o.scale=(180,180,1);o.data.materials.append(ocean)
bpy.ops.object.empty_add(type='PLAIN_AXES',location=(97,76,34))
bpy.context.object.name="LIGHTHOUSE future placement point";bpy.context.object.empty_display_size=7
bpy.ops.object.camera_add(location=(142,-192,124))
cam=bpy.context.object;cam.rotation_euler=(Vector((0,-11,11))-cam.location).to_track_quat('-Z','Y').to_euler()
cam.data.type='ORTHO';cam.data.ortho_scale=250;bpy.context.scene.camera=cam
bpy.ops.object.light_add(type='AREA',location=(-70,-60,160))
bpy.context.object.data.energy=3300;bpy.context.object.data.size=105
scene=bpy.context.scene;scene.render.engine='BLENDER_EEVEE_NEXT'
scene.render.resolution_x=1400;scene.render.resolution_y=900;scene.render.resolution_percentage=100
scene.render.filepath=str(O/"VAELORIA_MARBLE_TERRAIN_V4.png")
bpy.ops.wm.save_as_mainfile(filepath=str(O/"VAELORIA_MARBLE_TERRAIN_V4.blend"))
bpy.ops.render.render(write_still=True)
print("Vaeloria Marble V4 saved",O)
