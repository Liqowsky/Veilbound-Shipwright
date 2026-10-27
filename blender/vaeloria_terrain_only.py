# Vaeloria — terrain-only blockout for Blender 4.x
# Run: blender -b -P vaeloria_terrain_only.py
import bpy, math, random
from mathutils import Vector
from math import sin, cos, exp
random.seed(41)
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

def material(name,color,rough=1):
 m=bpy.data.materials.new(name); m.diffuse_color=(*color,1)
 m.use_nodes=True; n=m.node_tree.nodes.get('Principled BSDF')
 n.inputs['Base Color'].default_value=(*color,1);n.inputs['Roughness'].default_value=rough
 return m
sand=material('01 sandstone sand - terrain',(0.55,.30,.16))
rock=material('02 cliff rock',(0.38,.20,.13))
pathmat=material('03 navigable switchback path',(0.75,.54,.31))
islandmat=material('04 island sandstone',(.62,.39,.23))
watermat=material('05 water reference plane',(.055,.32,.36),.27)

def mesh_grid(name,nx,ny,fn,mat):
 vs=[];faces=[]
 for j in range(ny+1):
  for i in range(nx+1):
   x,y,z=fn(i/nx,j/ny);vs.append((x,y,z))
 for j in range(ny):
  for i in range(nx):
   a=j*(nx+1)+i;faces.append((a,a+1,a+nx+2,a+nx+1))
 me=bpy.data.meshes.new(name);me.from_pydata(vs,[],faces);me.update()
 ob=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(ob);ob.data.materials.append(mat)
 for poly in me.polygons:poly.use_smooth=True
 return ob
def left_coast(y):
 return 36+5*sin(y*.065)+1.7*sin(y*.18)+3*exp(-((y-18)/12)**2)
def right_coast(y):
 return 65+6*sin(y*.047+1.1)+1.6*sin(y*.15)
def left(u,v):
 y=85*v;x=-12+u*(left_coast(y)+12)
 shore=left_coast(y);inland=max(0,(shore-x)/44)
 z=-.6+4.2*inland**1.7+1.5*exp(-((x-11)/16)**2-((y-65)/21)**2)
 z+=.3*sin(x*.24)*sin(y*.18)*inland
 return x,y,z
mesh_grid('LEFT LAND — one continuous sculpted shoreline',110,150,left,sand)
# Broad right peninsula, no vertical tabletop cut. High bluff set back from coast.
def right_height(x,y):
 coast=right_coast(y)
 d=max(0,x-coast)
 z=-.6+17*(1-exp(-(d/18)**2))
 z+=3.4*exp(-((x-91)/15)**2-((y-64)/21)**2)
 z+=1.1*sin(x*.18+y*.08)*min(1,d/17)
 return z
def right(u,v):
 y=85*v;shore=right_coast(y);x=shore+u*(114-shore)
 return x,y,right_height(x,y)
mesh_grid('RIGHT PENINSULA — continuous climb to lighthouse summit',125,160,right,rock)
# Outlying islands are actual raised land meshes with irregular contours, not stacked cubes.
def island(cx,cy,rx,ry,h,idx):
 N=64;R=9;v=[];f=[]
 for ring in range(R+1):
  t=ring/R
  for i in range(N):
   a=2*math.pi*i/N
   jitter=1+.075*sin(3*a+idx)+.05*sin(7*a+idx*.7)
   x=cx+rx*t*jitter*cos(a);y=cy+ry*t*jitter*sin(a)
   z=-.48+h*(1-t**2)**1.25+.15*sin(a*5+idx)*t
   v.append((x,y,z))
 for k in range(R):
  for i in range(N):
   a=k*N+i;b=k*N+(i+1)%N
   f.append((a,b,b+N,a+N))
 me=bpy.data.meshes.new('Island mesh');me.from_pydata(v,[],f);me.update()
 ob=bpy.data.objects.new('ISLAND %02d — organic landform'%idx,me);bpy.context.collection.objects.link(ob)
 ob.data.materials.append(islandmat)
 for p in me.polygons:p.use_smooth=True
for idx,(cx,cy,rx,ry,h) in enumerate([(47,33,4.5,5,3.5),(53,49,7,4.5,5.3),(60,66,5,7,4.4),(46,70,3,4,2.3)],1):
 island(cx,cy,rx,ry,h,idx)
# Switchback rises from water-level foot to summit, constructed as walkable ribbon.
# Four switchbacks across the broad right peninsula. z samples real underlying bluff.
route=[(right_coast(10)+3,10),(82,13),(98,19),(101,28),(85,34),
       (81,43),(101,48),(104,57),(90,65),(96,72)]
points=[]
for a,b in zip(route,route[1:]):
 A=Vector(a);B=Vector(b)
 for k in range(16):
  t=k/16;xy=A.lerp(B,t)
  points.append((xy.x,xy.y,right_height(xy.x,xy.y)+.45))
points.append((*route[-1],right_height(*route[-1])+.45))
# smooth height variation incl. safe ramp sections
for i in range(1,len(points)-1):
 x,y,z=points[i];points[i]=(x,y,(points[i-1][2]+2*z+points[i+1][2])/4)
verts=[];faces=[]
for i,p in enumerate(points):
 prev=Vector(points[max(0,i-1)][:2]);nxt=Vector(points[min(i+1,len(points)-1)][:2])
 vec=(nxt-prev).normalized();side=Vector((-vec.y,vec.x))
 width=2.8
 for s in [-1,1]:verts.append((p[0]+side.x*s*width/2,p[1]+side.y*s*width/2,p[2]+.06))
 if i:faces.append((2*i-2,2*i-1,2*i+1,2*i))
me=bpy.data.meshes.new('switchback_path');me.from_pydata(verts,[],faces);me.update()
ob=bpy.data.objects.new('WINDING TRAIL — switchbacks up right cliff',me);bpy.context.collection.objects.link(ob);me.materials.append(pathmat)
# Sea plane reference only; no buildings/lighthouse geometry until terrain approved.
bpy.ops.mesh.primitive_plane_add(size=2,location=(50,42,-.65))
ob=bpy.context.object;ob.name='SEA — flat level guide';ob.scale=(80,68,1);ob.data.materials.append(watermat)
# Camera previews the island chain and cliff path together.
def aim(ob,at):ob.rotation_euler=(Vector(at)-ob.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(48,-91,82))
cam=bpy.context.object;aim(cam,(51,40,6));cam.data.type='ORTHO';cam.data.ortho_scale=152
bpy.context.scene.camera=cam
world=bpy.context.scene.world;world.color=(.35,.35,.35)
bpy.ops.object.light_add(type='AREA',location=(45,-20,92));bpy.context.object.data.energy=2600;bpy.context.object.data.shape='DISK';bpy.context.object.data.size=65
sc=bpy.context.scene;sc.render.engine='CYCLES';sc.cycles.samples=24
sc.render.resolution_x=1440;sc.render.resolution_y=900;sc.render.resolution_percentage=100
sc.render.image_settings.file_format='PNG'
sc.render.filepath='/tmp/vaeloria_terrain_only.png'
bpy.ops.wm.save_as_mainfile(filepath='/tmp/vaeloria_terrain_only.blend')
bpy.ops.render.render(write_still=True)
