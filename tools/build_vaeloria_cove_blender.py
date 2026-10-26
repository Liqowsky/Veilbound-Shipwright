"""VEILBOUND — camera-matched 3D coastal cove. Run: blender -b -t 4 --python tools/build_vaeloria_cove_blender.py
All geometry/materials/lights are genuinely made in Blender; no AI generated pixels.
"""
import bpy, math, random, os
from mathutils import Vector
from pathlib import Path
random.seed(1229)
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
out=Path(os.environ.get("VAELORIA_OUT","/tmp/vaeloria_render"))
out.mkdir(parents=True,exist_ok=True)
def mat(name,c,rough=1,emit=0):
 m=bpy.data.materials.new(name);m.diffuse_color=(*c,1);m.use_nodes=True
 p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*c,1);p.inputs['Roughness'].default_value=rough
 if emit:
  p.inputs['Emission Color'].default_value=(*c,1);p.inputs['Emission Strength'].default_value=emit
 return m
sand=mat('Warm ochre sand',(.79,.38,.14)); rock=mat('Red layered sandstone',(.52,.19,.09)); rocklight=mat('Sunlit cliff edges',(.91,.43,.18))
stucco=mat('Sunbleached handpainted plaster',(.91,.75,.52)); wood=mat('Dark timber',(.21,.105,.065)); roof=mat('Rust cloth awning',(.52,.115,.08))
water=mat('Deep teal bay',(.017,.28,.37),.28);foam=mat('Shallow turquoise foam',(.64,.93,.79))
green=mat('Emerald magical crystals',(.04,.96,.51),.2,3.2); beacon=mat('Warm beacon', (1,.7,.19),.2,5)
grass=mat('Dried grasses',(.55,.39,.12));dark=mat('Deep window recess',(.08,.07,.055))
def cube(name,at,scale,material,bevel=0):
 bpy.ops.mesh.primitive_cube_add(size=1,location=at);o=bpy.context.object;o.name=name;o.dimensions=scale;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 o.data.materials.append(material)
 if bevel: mod=o.modifiers.new('Soft silhouette bevel','BEVEL');mod.width=bevel;mod.segments=1;o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
 return o
def cone(name,at,rad,depth,material,verts=9):
 bpy.ops.mesh.primitive_cone_add(vertices=verts,radius1=rad,radius2=rad*.62,depth=depth,location=at)
 o=bpy.context.object;o.name=name;o.data.materials.append(material);return o
def tube(name,a,b,r,material,verts=7):
 a=Vector(a);b=Vector(b);d=b-a
 bpy.ops.mesh.primitive_cylinder_add(vertices=verts,radius=r,depth=d.length,location=(a+b)/2)
 o=bpy.context.object;o.name=name;o.rotation_euler=d.to_track_quat('Z','Y').to_euler();o.data.materials.append(material);return o
def rockform(name,at,sc,material):
 bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=1,location=at);o=bpy.context.object;o.name=name
 o.scale=sc;o.rotation_euler=(random.random()*.25,random.random()*.5,random.random()*6.28);o.data.materials.append(material);return o
def roofpiece(name,x,y,z,w,d,h):
 v=[(x-w/2,y-d/2,z),(x+w/2,y-d/2,z),(x+w/2,y+d/2,z),(x-w/2,y+d/2,z),(x,y-d/2,z+h),(x,y+d/2,z+h)]
 fs=[(0,1,4),(3,5,2),(0,4,5,3),(1,2,5,4)]
 mesh=bpy.data.meshes.new(name);mesh.from_pydata(v,[],fs);mesh.update();ob=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(ob);ob.data.materials.append(roof)
def house(name,x,y,z,w=17,d=13,h=10):
 cube(name+' plaster walls',(x,y,z+h/2),(w,d,h),stucco,.35)
 roofpiece(name+' tiled roof',x,y,z+h,w+3,d+3,4)
 cube(name+' dark doorway',(x,y-d/2-.06,z+3),(3,.24,5),dark)
 for dx in (-w*.3,w*.3):cube(name+' window', (x+dx,y-d/2-.16,z+6.3),(1.7,.20,2.6),dark)
 cube(name+' veranda canopy',(x,y-d/2-3,z+8.1),(w*.88,6,.33),roof)
 for dx in (-w*.35,w*.35):tube(name+' timber post',(x+dx,y-d/2-5,z),(x+dx,y-d/2-5,z+8),.28,wood)
# Two facing headlands leave a very deep open bay: sea is the CENTER.
cube('Ocean surface under open bay',(0,40,-2),(275,285,.4),water)
# Modelled left and right terraced land: geometry follows photo silhouettes, not the old flat strip.
cube('LEFT coastal home terrace',(-84,34,6),(68,135,13),sand)
cube('LEFT near foreground terraces',(-93,-45,4),(90,60,9),sand)
cube('RIGHT lighthouse high mesa',(83,62,21),(54,106,41),rock)
cube('RIGHT cave beach',(70,-18,0),(76,42,3),sand)
for side in (-1,1):
 for i in range(95):
  x=random.uniform(-119,-59) if side==-1 else random.uniform(61,116)
  y=random.uniform(-24,118)
  z=random.uniform(8,23) if side==-1 else random.uniform(15,38)
  sz=random.uniform(2,11)
  rockform(('LEFT' if side==-1 else 'RIGHT')+' cliff rock '+str(i),(x,y,z),(random.uniform(2,6),random.uniform(2,7),sz), rocklight if i%5==0 else rock)
# Landmark house dominates left third.
house('PROTAGONIST FAMILY HOME',-88,-5,13,28,20,14)
for i,(x,y,w) in enumerate([(-65,33,14),(-74,65,13),(-47,58,11),(-57,83,12)]):
 house('VILLAGE '+str(i),x,y,13,w,w*.8,7)
# Lighthouse stands high right, below silhouetted peak: no floating lighthouse.
L=(83,57);base=43
cone('TALL LIGHTHOUSE STONE TOWER',(L[0],L[1],base+20),7.6,40,stucco,14)
cube('Lighthouse dark lantern',(L[0],L[1],base+43),(12,12,8),dark)
cone('Lighthouse top roof',(L[0],L[1],base+48),8,5,roof,10)
bpy.ops.mesh.primitive_uv_sphere_add(segments=16,ring_count=8,radius=2.4,location=(L[0],L[1],base+44))
bpy.context.object.name='LIVE LIGHTHOUSE EMITTER';bpy.context.object.data.materials.append(beacon)
# Cave mouth in cliff faces center bay, angular ring, emerald actual crystals.
cube('Cave black opening',(67,-8,8),(1.5,18,16),dark)
for i in range(12):
 theta=i/12*math.tau
 rockform('Cave arch stone'+str(i),(65,-8+10*math.cos(theta),12+10*math.sin(theta)),(3.3,3.2,3.5),rocklight)
for i in range(17):
 x=random.uniform(63,69);y=random.uniform(-17,-1);z=random.uniform(3,15)
 cone('Luminous cave emerald '+str(i),(x,y,z),random.uniform(.35,1.4),random.uniform(1.5,5.6),green,5)
# Open bay details, docks, shallow surf, sunlit stylized formations.
for i in range(26):
 x=random.uniform(-48,48);y=random.uniform(0,105)
 rockform('Sea stack '+str(i),(x,y,random.uniform(-1,4)),(random.uniform(1,4),random.uniform(1,6),random.uniform(2,10)),rock)
for i in range(100):
 x=random.uniform(-56,62);y=random.uniform(-25,110)
 if abs(x)<15: continue
 cube('Foam ripple '+str(i),(x,y,-1.65),(random.uniform(1,6),.10,.06),foam)
for i in range(15):
 x=-45+i*2.0
 cube('Pier timber '+str(i),(x,7,2),(1.5,22,.6),wood)
 if i%3==0:tube('Pier post '+str(i),(x,1,-2),(x,1,5),.35,wood)
# Dry shrubs and flagpoles
for i in range(175):
 x=random.uniform(-112,-53) if i%2 else random.uniform(66,113)
 y=random.uniform(-44,100);z=13 if x<0 else 43
 tube('Dry grass '+str(i),(x,y,z),(x+.3,y+.1,z+random.uniform(.3,1.4)),.045,grass,4)
for i,(x,y,z) in enumerate([(-110,-10,20),(-49,34,21),(96,37,45)]):
 tube('Flag pole '+str(i),(x,y,z),(x,y,z+12),.22,wood)
 cube('Cloth flag '+str(i),(x+3,y,z+9),(6,.15,2.3),roof)
# Two natural exit corridors - unassigned destination names
for i,(x,y,z) in enumerate([(-119,94,12),(116,101,43)]):
 tube('EXIT '+str(i)+' marker A',(x-3,y,z),(x-3,y,z+6),.28,wood)
 tube('EXIT '+str(i)+' marker B',(x+3,y,z),(x+3,y,z+6),.28,wood)
# CAMERA deliberately framed from seaside-facing foreground toward sunlit town and lighthouse
def point(obj,target):
 obj.rotation_euler=(Vector(target)-obj.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(3,-190,64))
cam=bpy.context.object;cam.name='MENU — reference composition';point(cam,(0,35,21));cam.data.type='PERSP';cam.data.lens=31
bpy.context.scene.camera=cam
bpy.ops.object.light_add(type='SUN',location=(-50,110,100))
sun=bpy.context.object;sun.name='Sundown orange';sun.data.energy=2.7;sun.data.color=(1,.58,.31);point(sun,(0,0,0))
bpy.ops.object.light_add(type='AREA',location=(-55,-80,85))
fill=bpy.context.object;fill.name='Cool sky fill';fill.data.energy=1100;fill.data.shape='DISK';fill.data.size=100;fill.data.color=(.43,.7,1);point(fill,(0,0,10))
for n,pos,power,color,size in [('Emerald cave point',(58,-7,11),1800,(.08,1,.54),14),('Beacon local light',(83,57,87),2600,(1,.64,.2),14)]:
 bpy.ops.object.light_add(type='POINT',location=pos);o=bpy.context.object;o.name=n;o.data.energy=power;o.data.color=color;o.data.shadow_soft_size=size
world=bpy.data.worlds.new('Twilight warm sky') if not bpy.data.worlds else bpy.data.worlds[0];world.use_nodes=True
world.node_tree.nodes['Background'].inputs['Color'].default_value=(.33,.48,.70,1);world.node_tree.nodes['Background'].inputs['Strength'].default_value=.8
bpy.context.scene.world=world
sc=bpy.context.scene;sc.render.engine='CYCLES';sc.cycles.samples=24
sc.render.resolution_x=1600;sc.render.resolution_y=900;sc.render.resolution_percentage=100
sc.view_settings.view_transform='AgX'
bpy.ops.wm.save_as_mainfile(filepath=str(out/'VAELORIA_COVE_REFERENCE.blend'))
sc.render.filepath=str(out/'VAELORIA_COVE_REFERENCE_RENDER.png')
bpy.ops.render.render(write_still=True)
print('FINISHED 3D SCENE',len(bpy.data.objects),out)
