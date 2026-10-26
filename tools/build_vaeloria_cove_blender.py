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
  if 'Emission Color' in p.inputs: p.inputs['Emission Color'].default_value=(*c,1)
  elif 'Emission' in p.inputs: p.inputs['Emission'].default_value=(*c,1)
  if 'Emission Strength' in p.inputs: p.inputs['Emission Strength'].default_value=emit
 return m
sand=mat('Warm ochre sand',(.79,.38,.14)); rock=mat('Red layered sandstone',(.52,.19,.09)); rocklight=mat('Sunlit cliff edges',(.91,.43,.18))
stucco=mat('Sunbleached handpainted plaster',(.91,.75,.52)); wood=mat('Dark timber',(.21,.105,.065)); roof=mat('Rust cloth awning',(.52,.115,.08))
water=mat('Deep teal bay',(.017,.28,.37),.28);foam=mat('Shallow turquoise foam',(.64,.93,.79))
green=mat('Emerald magical crystals',(.04,.96,.51),.2,3.2); beacon=mat('Warm beacon', (1,.7,.19),.2,5)
grass=mat('Dried grasses',(.55,.39,.12));dark=mat('Deep window recess',(.08,.07,.055))
# PROCEDURAL PAINTED TEXTURE PASS — these shaders render on actual mesh surfaces.
# Object-space coordinates avoid needing UVs for preliminary terrain/architecture art.
def painted_shader(material, dark_color, light_color, scale=4.0, bump=0.10):
 nodes=material.node_tree.nodes; links=material.node_tree.links
 bsdf=nodes.get('Principled BSDF')
 coord=nodes.new('ShaderNodeTexCoord')
 noise=nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=scale
 noise.inputs['Detail'].default_value=3.3;noise.inputs['Roughness'].default_value=.68
 ramp=nodes.new('ShaderNodeValToRGB')
 ramp.color_ramp.elements[0].position=.21
 ramp.color_ramp.elements[0].color=(*dark_color,1)
 ramp.color_ramp.elements[1].position=.79
 ramp.color_ramp.elements[1].color=(*light_color,1)
 links.new(coord.outputs['Generated'],noise.inputs['Vector'])
 links.new(noise.outputs['Fac'],ramp.inputs['Fac'])
 links.new(ramp.outputs['Color'],bsdf.inputs['Base Color'])
 if bump:
  b=nodes.new('ShaderNodeBump');b.inputs['Strength'].default_value=bump
  b.inputs['Distance'].default_value=.08
  links.new(noise.outputs['Fac'],b.inputs['Height'])
  links.new(b.outputs['Normal'],bsdf.inputs['Normal'])
painted_shader(sand,(.48,.205,.085),(.95,.62,.30),6,.12)
painted_shader(rock,(.29,.09,.045),(.76,.30,.135),5,.21)
painted_shader(rocklight,(.49,.19,.085),(1,.59,.27),5,.17)
painted_shader(stucco,(.66,.46,.30),(1,.90,.68),15,.065)
painted_shader(wood,(.12,.057,.03),(.47,.22,.10),11,.11)
painted_shader(roof,(.30,.055,.045),(.78,.22,.11),12,.055)
painted_shader(grass,(.28,.19,.055),(.83,.66,.27),8,.02)
painted_shader(water,(.009,.11,.18),(.035,.59,.61),9,.045)
# Lighting/render fidelity: lower render noise without using a pre-generated picture.
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
# Swept coast meshes replace the old four giant cuboids.
# Center inlet remains open, with irregular terraces and stratified cliff bands.
def coast_terrace(name,side,front,back,outer,inner,base_z,height,material):
 # Closed coastline with vertex-based terraces, NOT flat slab and exposed undersides.
 count=64;verts=[];faces=[]
 for i in range(count):
  t=i/(count-1);y=front+(back-front)*t
  shore=inner+side*(4*math.sin(t*7)+2*math.sin(t*17))
  far=outer+side*(7*math.sin(t*5.2)+3*math.sin(t*13))
  top=base_z+height*(.83+.13*math.sin(t*6)+.04*math.sin(t*21))
  # Shore edge starts near sea level; peaks inland. High cliff face occurs
  # where ground rises over the first 15 percent of terrain depth.
  for j in range(9):
   u=j/8
   x=shore+(far-shore)*u
   raise_curve=(u**.42) if side==1 else (u**.8)
   z=-1.6+(top+1.6)*raise_curve+1.1*math.sin(i*.71+j*1.9)*u*(1-u)
   verts.append((x,y,z))
  if i:
   for j in range(8):
    a=(i-1)*9+j;b=i*9+j
    faces.append((a,b,a+1));faces.append((a+1,b,b+1))
 mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces);mesh.update()
 o=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(o);o.data.materials.append(material)
 return o
coast_terrace('LEFT layered coast',-1,-85,150,-130,-54,9,12,sand)
coast_terrace('RIGHT tall lighthouse cliffs',1,-38,150,133,56,19,28,rock)
# A separate landing shelf supports the protagonist home and village buildings.
cube('Home terrace foundation',(-88,-5,10),(34,27,7),rocklight,.6)
# Thin beach at the cave base: keep turquoise bay unobstructed.
cube('Cave golden beach',(77,-23,-.35),(24,30,1.3),sand)
for side in (-1,1):
 for i in range(44):
  x=random.uniform(-119,-59) if side==-1 else random.uniform(61,116)
  y=random.uniform(-24,118)
  z=random.uniform(8,23) if side==-1 else random.uniform(15,38)
  sz=random.uniform(1.6,5)
  rockform(('LEFT' if side==-1 else 'RIGHT')+' cliff rock '+str(i),(x,y,z),(random.uniform(3,9),random.uniform(3,9),sz), rocklight if i%5==0 else rock)
# Painterly sandstone strata at right cliff foot, actual mesh bands.
for i in range(24):
 y=-25+i*6.6
 x=61+3*math.sin(i*.71)
 rockform('Bay coast vertical strata %02d'%i,(x,y,8+5*math.sin(i*.43)),(3.5,5.2,11+3*math.sin(i)),rocklight if i%4==0 else rock)
# Color-separated windswept rock shelves on the opposite cape
for i in range(22):
 y=-47+i*8
 x=-57-4*math.cos(i*.43)
 rockform('Home coast sandstone shelf %02d'%i,(x,y,6+math.cos(i*.6)),(4,5,2.5),rocklight)
# Landmark house dominates left third.
house('PROTAGONIST FAMILY HOME',-88,-5,13,28,20,14)
for i,(x,y,w) in enumerate([(-65,33,14),(-74,65,13),(-47,58,11),(-57,83,12)]):
 house('VILLAGE '+str(i),x,y,13,w,w*.8,7)
# Lighthouse stands high right, below silhouetted peak: no floating lighthouse.
L=(83,57);base=43
cone('TALL LIGHTHOUSE STONE TOWER',(L[0],L[1],base+20),7.6,40,stucco,14)
cone('Lighthouse masonry ring',(L[0],L[1],base+39),8.5,3,rocklight,16)
cone('Lighthouse dark lantern',(L[0],L[1],base+43),6.4,8,dark,12)
for n in range(12):
 a=n*math.tau/12
 tube('Lantern railing '+str(n),(L[0]+7*math.cos(a),L[1]+7*math.sin(a),base+39),(L[0]+7*math.cos(a),L[1]+7*math.sin(a),base+45),.16,wood)
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
for i in range(12):
 x=random.uniform(-48,48);y=random.uniform(0,105)
 rockform('Sea stack '+str(i),(x,y,random.uniform(-1,4)),(random.uniform(1,4),random.uniform(1,6),random.uniform(1,4)),rock)
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
cam=bpy.context.object;cam.name='MENU — reference composition';point(cam,(0,35,21));cam.data.type='PERSP';cam.data.lens=39
bpy.context.scene.camera=cam
bpy.ops.object.light_add(type='SUN',location=(-50,110,100))
sun=bpy.context.object;sun.name='Sundown orange';sun.data.energy=2.7;sun.data.color=(1,.58,.31);point(sun,(0,0,0))
bpy.ops.object.light_add(type='AREA',location=(-55,-80,85))
fill=bpy.context.object;fill.name='Cool sky fill';fill.data.energy=1100;fill.data.shape='DISK';fill.data.size=100;fill.data.color=(.43,.7,1);point(fill,(0,0,10))
for n,pos,power,color,size in [('Emerald cave point',(58,-7,11),1800,(.08,1,.54),14),('Beacon local light',(83,57,87),2600,(1,.64,.2),14)]:
 bpy.ops.object.light_add(type='POINT',location=pos);o=bpy.context.object;o.name=n;o.data.energy=power;o.data.color=color;o.data.shadow_soft_size=size
world=bpy.data.worlds.new('Twilight warm sky') if not bpy.data.worlds else bpy.data.worlds[0];world.use_nodes=True
world.node_tree.nodes['Background'].inputs['Color'].default_value=(.74,.35,.21,1);world.node_tree.nodes['Background'].inputs['Strength'].default_value=.8
bpy.context.scene.world=world
sc=bpy.context.scene;sc.render.engine='CYCLES';sc.cycles.samples=32
# Ubuntu apt Blender builds can omit OpenImageDenoise entirely.
# Disable both render and viewport denoisers before invoking Cycles.
sc.cycles.use_denoising=False
for layer in sc.view_layers:
 if hasattr(layer,'cycles'):
  layer.cycles.use_denoising=False

sc.render.resolution_x=1600;sc.render.resolution_y=900;sc.render.resolution_percentage=100
sc.view_settings.view_transform='AgX'
bpy.ops.wm.save_as_mainfile(filepath=str(out/'VAELORIA_COVE_REFERENCE.blend'))
sc.render.filepath=str(out/'VAELORIA_COVE_REFERENCE_RENDER.png')
bpy.ops.render.render(write_still=True)
print('FINISHED 3D SCENE',len(bpy.data.objects),out)
