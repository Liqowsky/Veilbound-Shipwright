import bpy, math, os, random
from mathutils import Vector
from math import sin, cos, pi
random.seed(23)
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
s=bpy.context.scene
s.render.engine='BLENDER_EEVEE'
s.eevee.taa_render_samples=64
s.eevee.use_gtao=True
s.eevee.use_bloom=True
s.render.resolution_x=1280;s.render.resolution_y=720
s.render.resolution_percentage=int(os.getenv('VB_PERCENT','75'))
s.render.fps=24;s.frame_start=1;s.frame_end=int(os.getenv('VB_FRAMES','216'))
s.render.image_settings.file_format='PNG';s.render.filepath='//renders/frame_'
s.view_settings.view_transform='Standard';s.view_settings.look='Medium High Contrast'
def mat(name,color,metal=0,rough=.35,emission=0):
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True
 p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1)
 p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough
 if emission:
  key='Emission Color' if 'Emission Color' in p.inputs else 'Emission'
  p.inputs[key].default_value=(*color,1)
  if 'Emission Strength' in p.inputs:p.inputs['Emission Strength'].default_value=emission
 return m
gold=mat('Aged engraved gold',(0.61,.41,.13),.85,.22)
edgegold=mat('Bright gold edges',(.86,.66,.29),.88,.18)
stone=mat('Pale stone inset',(.54,.58,.48),.12,.64)
silver=mat('Dull ancient silver',(.34,.44,.44),.8)
dark=mat('Black patina',(.022,.045,.042),.6)
emerald=mat('Pulsating emerald',(.015,.95,.38),.17,.15,6)
chainmat=mat('Gilded chain links',(.53,.33,.12),.83)
cloudmat=mat('Distant cloud silver',(.17,.27,.42),0,.98)
def k(obj,frame,pos=None,scale=None,rot=None):
 if pos is not None:obj.location=pos;obj.keyframe_insert('location',frame=frame)
 if scale is not None:obj.scale=scale;obj.keyframe_insert('scale',frame=frame)
 if rot is not None:obj.rotation_euler=rot;obj.keyframe_insert('rotation_euler',frame=frame)
def bevel(obj,width=.04):
 b=obj.modifiers.new('Polished edges','BEVEL');b.width=width;b.segments=3
 obj.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
def cylinder(name,r,depth,material,parent=None):
 bpy.ops.mesh.primitive_cylinder_add(vertices=64,radius=r,depth=depth)
 o=bpy.context.object;o.name=name;o.rotation_euler.x=pi/2;o.data.materials.append(material)
 if parent:o.parent=parent
 bevel(o);return o
def torus(name,r,thick,material,parent=None):
 bpy.ops.mesh.primitive_torus_add(major_segments=32,minor_segments=12,major_radius=r,minor_radius=thick)
 o=bpy.context.object;o.name=name;o.rotation_euler.x=pi/2;o.data.materials.append(material)
 if parent:o.parent=parent
 for p in o.data.polygons:p.use_smooth=True
 return o
pendant=bpy.data.objects.new('Medallion animated root',None);s.collection.objects.link(pendant)
back=cylinder('Eight-point spiked medallion',.46,.15,silver,pendant)
for j in range(3):
 detail=torus('Forged concentric filigree %d'%j,.295+j*.062,.014,edgegold,pendant)
 detail.location.y=-.125-j*.003
rim=torus('Carved antique golden rim',.46,.065,gold,pendant);rim.location.y=-.12
inside=cylinder('Inset dark recess',.36,.018,dark,pendant);inside.location.y=-.095
core=bpy.data.objects.new('Emerald pulse root',None);s.collection.objects.link(core);core.parent=pendant
gem=cylinder('Large emerald luminous gemstone',.265,.065,emerald,core);gem.location.y=-.14
for i in range(8):
 a=2*pi*i/8
 bpy.ops.mesh.primitive_cone_add(vertices=5,radius1=.16,radius2=0,depth=.40)
 o=bpy.context.object;o.name='Ancient medallion spike %d'%i;o.parent=pendant
 o.location=(.52*cos(a),-.05,.52*sin(a));o.rotation_euler=(0,-pi/2+a,pi/2)
 o.data.materials.append(edgegold);bevel(o,.015)
for j in range(16):
 a=2*pi*j/16
 bpy.ops.mesh.primitive_uv_sphere_add(segments=12,ring_count=8,radius=.024,location=(.405*cos(a),-.18,.405*sin(a)))
 nail=bpy.context.object;nail.name='Riveted bronze detail %02d'%j;nail.parent=pendant;nail.data.materials.append(edgegold)
# Early flight approaches camera and locks in final title medallion position.
for f,pos,sc,rotation in [
 (1,(1.95,8.0,2.25),(.12,)*3,(.3,-.9,.8)),
 (32,(.75,.25,1.25),(.75,)*3,(0,-.25,.25)),
 (68,(.12,-.06,-1.25),(1,)*3,(0,0,0)),
 (216,(.12,-.06,-1.25),(1,)*3,(0,0,0))]:
 k(pendant,f,pos,sc,rotation)
for f,v in [(1,1),(75,1),(80,1.24),(85,1),(96,1),(101,1.33),(107,1),(216,1)]:
 k(core,f,scale=(v,v,v))
# 3D wordmark — appears from enchantment, remains behind suspended medallion.
curve=bpy.data.curves.new('3D Wordmark','FONT')
curve.body='VEILBOUND';curve.align_x='CENTER';curve.align_y='CENTER'
curve.size=1.45;curve.extrude=.11;curve.bevel_depth=.021;curve.bevel_resolution=2
word=bpy.data.objects.new('VEILBOUND real extruded 3D letters',curve);s.collection.objects.link(word)
curve.materials.append(gold);word.rotation_euler.x=pi/2;word.location=(0,.25,.30)
# Fine carved metallic underlay adds visual weight to the logo.
under=word.copy();under.data=word.data.copy();s.collection.objects.link(under)
under.name='Dimensional stone underlay';under.data.materials.clear();under.data.materials.append(stone)
under.location.y=.39;under.scale=(1.035,1.035,1.035)
for f,sc in [(1,.001),(104,.001),(128,.68),(149,1),(216,1)]:
 k(under,f,scale=(sc*1.035,sc*1.035,sc*1.035))
for f,sc in [(1,.001),(104,.001),(128,.68),(149,1),(216,1)]:
 k(word,f,scale=(sc,sc,sc))
# chain links are actual torus meshes, each independently animated; S-shaped arc interlaces title.
for i in range(28):
 u=i/27
 x=-3.6+7.2*u
 z=.84+.42*sin(3*pi*u)+.18*sin(9*pi*u)
 chain=torus('Articulated golden link %02d'%i,.13,.039,chainmat)
 for fr in [1,22,46,68,96,130,162,216]:
  t=min(1,max(0,(fr-46)/116));t=t*t*(3-2*t)
  p0=Vector((2.3+.11*i,-.6+.025*i,2.4-.17*i))
  p1=Vector((x,-.48,z))
  wob=Vector((.24*sin(i*.9+fr*.11),0,.30*sin(i*.55+fr*.12)))*(1-t)
  final=p0.lerp(p1,t)+wob
  r=(pi/2 + .35*sin(fr*.08+i*.8)*(1-t), .05*sin(i), pi*u*.35)
  k(chain,fr,final,rot=r)
# thin pulse shockwaves
for n in range(2):
 ring=torus('Emerald shockwave %d'%n,.35,.021,emerald)
 for f,sc in [(1,.001),(79+n*21,.001),(89+n*21,2.4),(103+n*21,.001),(216,.001)]:
  k(ring,f,pos=(.12,-.28,-1.25),scale=(sc,sc,sc))
# distant cloud banks, small and pushed behind subjects
for i in range(30):
 x=random.uniform(-7,7);z=random.uniform(-3.8,-2.3)
 bpy.ops.mesh.primitive_uv_sphere_add(segments=16,ring_count=8,location=(x,6+random.random()*4,z))
 cloud=bpy.context.object;cloud.name='Far sky cloud %02d'%i
 cloud.scale=(random.uniform(.5,1.8),random.uniform(.12,.24),random.uniform(.08,.24))
 cloud.data.materials.append(cloudmat)
 k(cloud,1,pos=cloud.location)
 k(cloud,216,pos=cloud.location+Vector((.6,0,0)))
bpy.ops.object.camera_add(location=(0,-13,.12))
cam=bpy.context.object;s.camera=cam
cam.rotation_euler=(Vector((0,0,0))-cam.location).to_track_quat('-Z','Y').to_euler()
cam.data.type='ORTHO';cam.data.ortho_scale=9.3
for f,v in [(1,9.8),(78,8.6),(150,9.2),(216,9.2)]:
 cam.data.ortho_scale=v;cam.data.keyframe_insert('ortho_scale',frame=f)
world=s.world;world.use_nodes=True
world.node_tree.nodes['Background'].inputs['Color'].default_value=(.07,.17,.30,1)
bg=world.node_tree.nodes['Background']
for f,color in [(1,(.16,.32,.57,1)),(110,(.07,.16,.34,1)),(216,(.006,.016,.06,1))]:
 bg.inputs['Color'].default_value=color;bg.inputs['Color'].keyframe_insert('default_value',frame=f)
def light(name,loc,color,power):
 bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.name=name
 o.data.energy=power;o.data.color=color;o.data.size=7
 o.rotation_euler=(Vector((0,0,0))-o.location).to_track_quat('-Z','Y').to_euler()
 return o
sun=light('Warm daylight',(3,-4,7),(1,.84,.59),820)
moon=light('Cool night light',(-4,-4,4),(.33,.63,1),230)
light('Emerald bounce',(0,-4,-1),(.13,1,.45),350)
for f,a,b in [(1,820,200),(115,430,470),(216,90,850)]:
 sun.data.energy=a;sun.data.keyframe_insert('energy',frame=f)
 moon.data.energy=b;moon.data.keyframe_insert('energy',frame=f)
os.makedirs('renders',exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath('veilbound_3d_v3.blend'))
bpy.ops.render.render(animation=True)
