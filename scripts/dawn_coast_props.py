# Veilbound Dawn Coast — supplemental model detail pass (Blender 3.6+).
# Run from Blender: blender -b --python scripts/dawn_coast_props.py
# Exports two matching-coordinate GLB files. Original procedural assets only.
import bpy, math, random, os
random.seed(25102026)
OUT=os.path.abspath("exports/veilbound");os.makedirs(OUT,exist_ok=True)
def material(name,rgb):
 m=bpy.data.materials.get(name) or bpy.data.materials.new(name)
 m.diffuse_color=(*rgb,1);return m
PAL={
 "sand":(.70,.50,.31),"rock":(.47,.34,.26),"clay":(.63,.37,.27),
 "grass":(.64,.57,.32),"wood":(.32,.23,.16),"snow":(.79,.86,.91),
 "ruin":(.37,.36,.38),"ice":(.51,.72,.81)}
def box(name,p,scale,key):
 bpy.ops.mesh.primitive_cube_add(size=1,location=p);o=bpy.context.object
 o.name=name;o.dimensions=scale;o.data.materials.append(material(key,PAL[key]))
 return o
def rock(name,p,scale,key):
 bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,location=p);o=bpy.context.object
 o.name=name;o.scale=scale;o.data.materials.append(material(key,PAL[key]))
 return o
def stem(name,p,height,key):
 bpy.ops.mesh.primitive_cone_add(vertices=5,radius1=.025,radius2=.001,depth=height,location=p)
 bpy.context.object.name=name;bpy.context.object.data.materials.append(material(key,PAL[key]))
def populate(future):
 prefix="winter_" if future else "desert_"
 box(prefix+"floor",(0,0,-.28),(110,105,.55),"snow" if future else "sand")
 # Coordinates identical for both timeline variants.
 houses=[(-16,-13),(-7,-15),(-18,2),(-15,13),(-4,16),(15,13)]
 for i,(x,y) in enumerate(houses):
  if not future:
   box("house_%d"%i,(x,y,1.7),(5,4.5,3.4),"clay")
   box("roof_%d"%i,(x,y,3.5),(5.6,5,.38),"rock")
   box("door_%d"%i,(x,y-2.3,.95),(1.2,.15,1.9),"wood")
  else:
   for j in range(5):
    h=(1.2,2.3,1.8,2.7,1.5)[(i+j)%5]
    box("broken_wall_%d_%d"%(i,j),(x-2+j,y+1.8,h/2),(.91,.75,h),"ruin")
   for j in range(12):
    rock("collapsed_brick_%d_%d"%(i,j),(x+random.uniform(-3,3),y+random.uniform(-3,3),.1),(.5,.35,.2),"ruin")
   rock("snowy_rubble_%d"%i,(x,y,.16),(1.5,1.2,.25),"snow")
 for i in range(160):
  x=random.uniform(-49,49);y=random.uniform(-47,47)
  if 4<x<18 and -7<y<7:continue
  rock(prefix+"pebble_%03d"%i,(x,y,.07),(.2,.15,.11),"ruin" if future else "rock")
 for i in range(160):
  x=random.uniform(-48,48);y=random.uniform(-47,47)
  if 4<x<18 and -7<y<7:continue
  if not future:
   for j in range(4):
    a=j*math.tau/4
    stem("grass_%d_%d"%(i,j),(x+math.cos(a)*.06,y+math.sin(a)*.06,.16),.32,"grass")
  elif i%4:
   stem("dead_grass_%d"%i,(x,y,.1),.2,"wood")
   rock("frost_%d"%i,(x,y,.03),(.2,.18,.08),"snow")
 # World anchors: same lighthouse and cave position in both eras.
 for j in range(5 if not future else 3):
  box("lighthouse_%d"%j,(35,30,j*1.65+.82),(3.2,3.2,1.62),"rock" if not future else "ruin")
 for j in range(9):
  a=math.pi*j/8
  rock("cave_arch_%d"%j,(-36+3.1*math.cos(a),31,1.2+2.7*math.sin(a)),(.8,.9,.9),"rock" if not future else "ruin")
 if future:
  for j in range(6):
   stem("icicle_%d"%j,(-38+j*.75,30.5,2.7),.8,"ice")
def export(future):
 bpy.ops.object.select_all(action="SELECT");bpy.ops.object.delete(use_global=False)
 random.seed(20261025);populate(future)
 bpy.ops.export_scene.gltf(filepath=os.path.join(OUT,"dawn_coast_"+("winter_25y" if future else "childhood")+".glb"),export_format="GLB")
export(False);export(True)
print("Veilbound Dawn Coast meshes exported to",OUT)
