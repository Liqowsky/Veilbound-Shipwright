"""Veilbound: circular cove terrain-only v3. No generated image, no houses.
Run with Blender 4.2: blender -b -P blender/vaeloria_circular_cove_v3.py
"""
import bpy, math, random, os
from mathutils import Vector
from pathlib import Path
from math import sin,cos,pi,exp,sqrt
random.seed(1207)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
OUT=Path(os.environ.get('VAELORIA_OUT','/tmp/vaeloria_circular'));OUT.mkdir(parents=True,exist_ok=True)
def material(n,color):
 m=bpy.data.materials.new(n);m.diffuse_color=(*color,1);m.use_nodes=True;m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(*color,1);return m
sand=material('sand warm buff',(.79,.45,.22));cliff=material('red sandstone cliffs',(.57,.27,.17))
trail=material('WALKABLE path - light tan',(.95,.70,.39));sea=material('SEA sea level',(.045,.38,.51))
islandmat=material('rocky natural islands',(.54,.34,.22))
def surf(n,NX,NY,fn,mt):
 vs=[];faces=[]
 for j in range(NY+1):
  for i in range(NX+1):vs.append(fn(i/NX,j/NY))
 for j in range(NY):
  for i in range(NX):
   a=j*(NX+1)+i;faces.append((a,a+1,a+NX+2,a+NX+1))
 me=bpy.data.meshes.new(n);me.from_pydata(vs,[],faces);me.update()
 ob=bpy.data.objects.new(n,me);bpy.context.collection.objects.link(ob);me.materials.append(mt)
 for f in me.polygons:f.use_smooth=True
 return ob
# Circular inner cove with opening at the far/top, wide connected rear walkable shore.
# Both sides of the cove remain ONE continuous land mass, never detached rectangular slabs.
def height(x,y):
 rr=sqrt((x/1.02)**2+((y+5)/.90)**2)
 # round lagoon center and opening to open ocean at +y
 edge=57+3.8*sin(math.atan2(y+5,x)*5)+1.7*sin(math.atan2(y+5,x)*11)
 outside=(rr-edge)
 t=max(0,min(1,(outside+3)/12))
 t=t*t*(3-2*t)
 rear=exp(-((y+64)/31)**2)
 plateau=(5.7 if x<0 else 8.2)
 escarpment=17*max(0,min(1,(x-44)/48))**1.3 if x>35 else 0
 z=-2.4+t*(plateau+escarpment)
 # rear sandy beach is shallower, left building terrace / right ascent
 z-=t*4.2*rear
 z+=t*(.75*sin(x*.085+y*.034)+.42*sin(y*.18))*min(1,max(.05,outside/15))
 # deep channel reconnecting lagoon and sea towards horizon
 if y>38 and abs(x)<33:
  fade=max(0,min(1,(y-38)/27))
  z=z*(1-fade)+(-2.4)*fade
 return z
def terrain(u,v):
 x=-110+220*u;y=-96+226*v
 return (x,y,height(x,y))
surf('MAIN CONNECTED CRESCENT COAST - no artificial cuts',190,180,terrain,cliff)
# Water is below shore, with exposed opening to distant ocean.
bpy.ops.mesh.primitive_plane_add(size=2,location=(0,25,-2.36))
ob=bpy.context.object;ob.name='SEA below coast';ob.scale=(155,160,1);ob.data.materials.append(sea)
# Four substantial islands in irregular clustered crescent, not random scattered spikes.
def island(n,cx,cy,rx,ry,h):
 rows=12;segments=60;v=[];f=[]
 for r in range(rows+1):
  t=r/rows
  for i in range(segments):
   a=2*pi*i/segments
   m=1+.10*sin(a*5+n)+.055*sin(a*9+n)
   x=cx+t*rx*cos(a)*m;y=cy+t*ry*sin(a)*m
   z=-2.33+h*(1-t*t)**1.9+.10*t*sin(a*7)
   v.append((x,y,z))
 for r in range(rows):
  for i in range(segments):
   a=r*segments+i;b=r*segments+(i+1)%segments
   f.append((a,b,b+segments,a+segments))
 me=bpy.data.meshes.new('island');me.from_pydata(v,[],f);me.update()
 o=bpy.data.objects.new('ROCK ISLAND '+str(n),me);bpy.context.collection.objects.link(o);me.materials.append(islandmat)
for spec in [(1,-18,7,8,7,6),(2,19,13,6,9,9),(3,3,36,7,5,6),(4,-26,40,4,5,5)]:island(*spec)
# The continuous path deliberately links village (-left) to summit on (+right).
# A natural back-beach promenade runs across the south shore then switchbacks east uphill.
# Keep path on the surface with a slight clearance, not floating in a straight chord.
anchors=[(-83,-46),(-67,-65),(-42,-78),(-16,-83),(13,-82),(39,-76),(60,-68),
         (76,-60),(91,-49),(97,-35),(78,-26),(75,-12),(93,1),(101,16),(88,28),(91,42)]
pts=[]
for a,b in zip(anchors,anchors[1:]):
 for j in range(12):
  t=j/12;x=a[0]*(1-t)+b[0]*t;y=a[1]*(1-t)+b[1]*t
  pts.append((x,y,height(x,y)+.27))
x,y=anchors[-1];pts.append((x,y,height(x,y)+.27))
vs=[];fs=[];width=3.6
for i,(x,y,z) in enumerate(pts):
 prev=Vector(pts[max(0,i-1)][:2]);nxt=Vector(pts[min(i+1,len(pts)-1)][:2])
 d=nxt-prev
 if d.length<1e-5:d=Vector((1,0))
 d.normalize();right=Vector((-d.y,d.x))
 for m in [-.5,.5]:vs.append((x+right.x*width*m,y+right.y*width*m,z))
 if i:fs.append((2*i-2,2*i-1,2*i+1,2*i))
me=bpy.data.meshes.new('connected route');me.from_pydata(vs,[],fs);me.update()
o=bpy.data.objects.new('CONTINUOUS VILLAGE TO LIGHTHOUSE TRAIL',me);bpy.context.collection.objects.link(o);me.materials.append(trail)
# Untextured marker geometry only, showing where future lighthouse WILL go
bpy.ops.object.empty_add(type='PLAIN_AXES',location=(91,42,height(91,42)+1))
bpy.context.object.name='LIGHTHOUSE SITE (EMPTY)';bpy.context.object.empty_display_size=6
# Bird's-eye review camera catches the full round lagoon and both ends of walkable route
bpy.ops.object.camera_add(location=(116,-154,136));cam=bpy.context.object
cam.rotation_euler=(Vector((0,-2,2))-cam.location).to_track_quat('-Z','Y').to_euler()
cam.data.type='ORTHO';cam.data.ortho_scale=222;bpy.context.scene.camera=cam
bpy.ops.object.light_add(type='AREA',location=(-60,-80,160))
bpy.context.object.data.energy=2800;bpy.context.object.data.size=130
scene=bpy.context.scene;scene.render.engine='BLENDER_EEVEE'
scene.render.resolution_x=1440;scene.render.resolution_y=900;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'
scene.render.filepath=str(OUT/'TERRAIN_ONLY_CIRCULAR_COVE_V3.png')
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'TERRAIN_ONLY_CIRCULAR_COVE_V3.blend'))
bpy.ops.render.render(write_still=True)
print('VAELORIA CIRCULAR TERRAIN V3 COMPLETE')
