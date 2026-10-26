"""VEILBOUND — import real CC0 Kenney Retro Medieval 3D assets into Blender scene.
The asset archive is downloaded by GitHub Actions, not generated.
Source: https://opengameart.org/content/retro-medieval-kit
License: CC0, author Kenney.nl.
"""
import bpy, os, math, random
from pathlib import Path
from mathutils import Vector
assets=Path(os.environ.get('VAELORIA_ASSETS','/tmp/veilbound-assets'))
candidate_files=list(assets.rglob('*.glb'))+list(assets.rglob('*.gltf'))
print('KENNEY_ASSETS_FOUND',len(candidate_files))
if not candidate_files:
 print('WARNING: No external GLB assets. Keeping original scene geometry.')
else:
 grouped={}
 for f in sorted(candidate_files):
  n=f.stem.lower().replace('-','_')
  for tag in ('house','tower','rock','barrel','crate','fence','wall','gate','arch','bridge','market','well','lantern','dock','boat'):
   if tag in n:
    grouped.setdefault(tag,[]).append(f)
 def asset(tag,at,target_width,rot=0):
  candidates=grouped.get(tag,[])
  if not candidates:return False
  src=candidates[0];before=set(bpy.context.scene.objects)
  try:
   if src.suffix=='.glb':bpy.ops.import_scene.gltf(filepath=str(src))
   else:bpy.ops.import_scene.gltf(filepath=str(src))
  except Exception as e:
   print('Asset import failed',src,str(e));return False
  added=[o for o in bpy.context.scene.objects if o not in before]
  meshes=[o for o in added if o.type=='MESH']
  if not meshes:return False
  # A single Empty controls all components, preserving meshes/UVs/materials.
  bpy.ops.object.empty_add(location=(0,0,0));root=bpy.context.object;root.name='KENNEY CC0 '+tag+' '+src.stem
  for o in added:
   if o!=root and o.parent is None:
    world=o.matrix_world.copy();o.parent=root;o.matrix_world=world
  deps=bpy.context.evaluated_depsgraph_get()
  coords=[]
  for o in meshes:
   for v in o.bound_box:coords.append(o.matrix_world @ Vector(v))
  lo=Vector([min(v[k] for v in coords) for k in range(3)])
  hi=Vector([max(v[k] for v in coords) for k in range(3)])
  center=(hi+lo)*.5
  width=max(hi.x-lo.x,hi.y-lo.y,.01)
  factor=target_width/width
  root.scale=(factor,)*3
  root.rotation_euler[2]=rot
  root.location=Vector(at)-Vector((center.x,center.y,lo.z))*factor
  print('IMPORTED_CC0',tag,src.name)
  return True
 random.seed(28)
 # Replace false silhouette placeholders only when actual imported mesh exists.
 if asset('house',(-88,-5,13),29):
  for o in list(bpy.data.objects):
   if o.name.startswith('PROTAGONIST FAMILY HOME'):bpy.data.objects.remove(o,do_unlink=True)
 for i,pos in enumerate([(-65,33,13),(-74,65,13),(-47,58,13),(-57,83,13)]):
  if asset('house',pos,12,rot=[0,.6,-.35,.25][i]):
   for o in list(bpy.data.objects):
    if o.name.startswith('VILLAGE '+str(i)+' '):bpy.data.objects.remove(o,do_unlink=True)
 for tag,poses,size in (
  ('barrel',[(-99,-25,13),(-79,-29,13),(-67,4,13)],3),
  ('crate',[(-93,-26,13),(-81,-28,13),(-59,18,13)],3),
  ('fence',[(-120,-35,10),(-103,-36,10),(-67,18,13)],8),
  ('rock',[(74,-33,0),(-53,-42,1),(61,-10,3)],7),
  ('well',[(-64,21,13)],7),
  ('lantern',[(-101,-22,13),(-72,-13,13)],4),
  ('boat',[(-28,-19,-1)],12)):
  for p in poses:asset(tag,p,size)
print('VEILBOUND_KITBASH_DONE')
