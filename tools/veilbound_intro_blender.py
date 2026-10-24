import bpy, math, os
from math import sin, cos, pi
from mathutils import Vector
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
sc=bpy.context.scene
sc.render.engine='BLENDER_EEVEE_NEXT' if bpy.app.version >= (4,2,0) else 'BLENDER_EEVEE'
sc.render.resolution_x=1280
sc.render.resolution_y=720
sc.render.resolution_percentage=int(os.getenv('VEILBOUND_PERCENT','60'))
sc.render.fps=24
sc.frame_start=1
sc.frame_end=int(os.getenv('VEILBOUND_END_FRAME','216'))
sc.world.color=(.03,.05,.09)
def material(name,c,metal=0,emit=0):
 m=bpy.data.materials.new(name)
 m.diffuse_color=(*c,1);m.use_nodes=True
 p=m.node_tree.nodes.get('Principled BSDF')
 p.inputs['Base Color'].default_value=(*c,1)
 p.inputs['Metallic'].default_value=metal
 p.inputs['Roughness'].default_value=.34
 if emit:
  p.inputs['Emission Color'].default_value=(*c,1)
  p.inputs['Emission Strength'].default_value=emit
 return m
silver=material('Ancient silver',(.48,.56,.53),.8)
bronze=material('Bronze chain',(.49,.34,.16),.85)
stone=material('Weathered stone',(.72,.73,.60))
green=material('Emerald gemstone',(.05,.9,.3),.3,4.0)
cloud=material('Clouds',(.5,.63,.77))
def link(name,location,r=.1):
 bpy.ops.mesh.primitive_torus_add(major_segments=24,minor_segments=8,major_radius=r,minor_radius=.023,location=location)
 o=bpy.context.object;o.name=name;o.data.materials.append(bronze)
 for f in o.data.polygons:f.use_smooth=True
 return o
def key(obj,fr,pos=None,scale=None,rot=None):
 if pos is not None:obj.location=pos;obj.keyframe_insert(data_path='location',frame=fr)
 if scale is not None:obj.scale=scale;obj.keyframe_insert(data_path='scale',frame=fr)
 if rot is not None:obj.rotation_euler=rot;obj.keyframe_insert(data_path='rotation_euler',frame=fr)
rig=bpy.data.objects.new('Pendant rig',None);sc.collection.objects.link(rig)
bpy.ops.mesh.primitive_cylinder_add(vertices=64,radius=.52,depth=.13)
body=bpy.context.object;body.name='Medallion body';body.data.materials.append(silver)
body.rotation_euler[0]=pi/2;body.parent=rig
mod=body.modifiers.new('Rounded rim','BEVEL');mod.width=.04;mod.segments=3
rim=link('Pendant bronze rim',(0,-.12,0),.48);rim.rotation_euler[0]=pi/2;rim.parent=rig
bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=3,radius=.23,location=(0,-.19,0))
gem=bpy.context.object;gem.name='Glowing emerald';gem.data.materials.append(green);gem.scale=(1,.3,1);gem.parent=rig
for fr,pos,scale in [(1,(1.7,7,2.3),(.12,)*3),(45,(.8,-.2,1),(.95,)*3),(67,(.8,-.2,1),(1,)*3),(216,(.8,-.2,1),(1,)*3)]:
 key(rig,fr,pos,scale)
for fr,s in [(1,1),(51,1),(56,1.35),(61,1),(69,1),(74,1.42),(79,1),(216,1)]:
 key(gem,fr,scale=(s,.3*s,s))
for i in range(20):
 o=link('Free moving chain link %02d'%i,(0,0,0))
 for fr in [1,25,48,75,105,140,170,216]:
  t=max(0,min(1,(fr-45)/125));t=t*t*(3-2*t)
  x=(.8+.17*sin(i*.7+fr*.1))*(1-t)+(-2.5+.18*i+.27*sin(i*.6))*t
  z=(1.7+.17*i+.20*sin(i*.45+fr*.12))*(1-t)+(-.64+.26*sin(i*.48))*t
  key(o,fr,(x,-.23,z),rot=(pi/2 if i%2 else 0,.2*sin(i+fr*.05),.2*sin(i*.6+fr*.04)))
font=bpy.data.curves.new('VEILBOUND 3D text','FONT')
font.body='VEILBOUND';font.align_x='CENTER';font.align_y='CENTER'
font.extrude=.07;font.bevel_depth=.014;font.bevel_resolution=3
word=bpy.data.objects.new('VEILBOUND wordmark',font);sc.collection.objects.link(word)
word.data.materials.append(stone);word.location=(0,.10,-.80)
for fr,s in [(1,.001),(89,.001),(115,.24),(155,.69),(216,.69)]:
 key(word,fr,scale=(s,s,s))
wave=link('Energy shockwave',(.8,-.3,1),.45);wave.data.materials.clear();wave.data.materials.append(green)
for fr,s in [(1,.001),(78,.001),(85,.1),(110,7),(126,.001),(216,.001)]:
 key(wave,fr,scale=(s,s,s))
import random
random.seed(7)
for i in range(45):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=12,ring_count=8,location=(random.uniform(-11,11),random.uniform(6,17),random.uniform(-7,4)))
 o=bpy.context.object;o.name='Sky cloud %02d'%i;o.scale=(random.uniform(1,4),random.uniform(.3,.8),random.uniform(.3,.8))
 o.data.materials.append(cloud)
 p=o.location.copy()
 key(o,1,p)
 key(o,216,(p.x+random.uniform(-1,1),p.y,p.z))
bpy.ops.object.camera_add(location=(0,-13,.8))
camera=bpy.context.object;sc.camera=camera
camera.rotation_euler=(Vector((0,0,0))-camera.location).to_track_quat('-Z','Y').to_euler()
camera.data.type='ORTHO';camera.data.ortho_scale=8.8
def area(name,pos,color,power):
 bpy.ops.object.light_add(type='AREA',location=pos)
 o=bpy.context.object;o.name=name;o.data.energy=power;o.data.color=color;o.data.size=10
 o.rotation_euler=(Vector((0,0,0))-o.location).to_track_quat('-Z','Y').to_euler()
 return o
day=area('Daylight',(3,-5,7),(1,.85,.63),650)
night=area('Moonlight',(-4,-5,4),(.4,.55,1),180)
area('Gem bounce',(1,-3,0),(.15,1,.5),260)
for fr,a,b in [(1,650,180),(100,360,410),(216,50,800)]:
 day.data.energy=a;day.data.keyframe_insert(data_path='energy',frame=fr)
 night.data.energy=b;night.data.keyframe_insert(data_path='energy',frame=fr)
sc.render.image_settings.file_format='PNG'
sc.render.filepath='//renders/frame_'
bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath('veilbound_intro.blend'))
if os.getenv('VEILBOUND_RENDER','1')=='1':bpy.ops.render.render(animation=True)
