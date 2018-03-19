import bpy
import math
from . import exporter_common
from .. import common
from .. import utility

# export blender information
def export_blender(scene, force_debug=False):
    node = export_scene(scene)
    export_pbrt_file(scene,node)

# export pbrt file
def export_pbrt_file(scene, node):
    # Get the path to save pbrt scene
    pbrt_file_path = bpy.context.user_preferences.addons[common.preference_bl_name].preferences.pbrt_export_path
    pbrt_file_name = exporter_common.getEditedFileName()
    pbrt_file_fullpath = pbrt_file_path + pbrt_file_name + ".pbrt"

    print( 'Exporting PBRT Scene :' , pbrt_file_fullpath )

    # generating the film header
    xres = scene.render.resolution_x * scene.render.resolution_percentage / 100
    yres = scene.render.resolution_y * scene.render.resolution_percentage / 100
    pbrt_film = "Film \"image\"\n"
    pbrt_film += "\t\"integer xresolution\" [" + '%d'%xres + "]\n"
    pbrt_film += "\t\"integer yresolution\" [" + '%d'%yres + "]\n"
    pbrt_film += "\t\"string filename\" [ \"" + pbrt_file_name + ".exr\" ]\n\n"

    # generating camera information
    fov = math.degrees( bpy.data.cameras[0].angle )
    camera = exporter_common.getCamera(scene)
    pos, target, up = exporter_common.lookAtPbrt(camera)
    pbrt_camera = "Scale -1 1 1 \n"
    pbrt_camera += "LookAt \t" + utility.vec3tostr( pos ) + "\n"
    pbrt_camera += "       \t" + utility.vec3tostr( target ) + "\n"
    pbrt_camera += "       \t" + utility.vec3tostr( up ) + "\n"
    pbrt_camera += "Camera \t\"perspective\"\n"
    pbrt_camera += "       \t\"float fov\" [" + '%f'%fov + "]\n\n"

    # sampler information
    sample_count = scene.sampler_count_prop
    pbrt_sampler = "Sampler \"random\" \"integer pixelsamples\" " + '%d'%sample_count + "\n"

    # integrator
    pbrt_integrator = "Integrator \"path\"" + " \"integer maxdepth\" " + '%d'%scene.inte_max_recur_depth + "\n\n"

    file = open(pbrt_file_fullpath,'w')
    file.write( pbrt_film )
    file.write( pbrt_camera )
    file.write( pbrt_sampler )
    file.write( pbrt_integrator )
    file.write( "WorldBegin\n" )
    file.write( "Include \"tmp.pbrt\"\n")
    for n in node:
        file.write( "Include \"" + n + ".pbrt\"\n" )
    file.write( "WorldEnd\n" )
    file.close()

# export scene
def export_scene(scene):
    ret = []
    all_nodes = exporter_common.renderable_objects(scene)
    for node in all_nodes:
        if node.type == 'MESH':
            export_mesh(node)
            ret.append(node.name)
    return ret;

def export_mesh(node):
    pbrt_file_path = bpy.context.user_preferences.addons[common.preference_bl_name].preferences.pbrt_export_path
    pbrt_geometry_file_name = pbrt_file_path + node.name + ".pbrt"

    print( "Exporting pbrt file for geometry: " , pbrt_geometry_file_name )
    file = open( pbrt_geometry_file_name , 'w' )

    mesh = node.data

    # begin attribute
    file.write( "AttributeBegin\n" )

    # transform
    #file.write( "Scale -1 1 1\n" )
    file.write( "Transform [" + utility.matrixtostr( node.matrix_world.transposed() ) + "]\n" )

    # output triangle mesh
    file.write( "Shape \"trianglemesh\"\n")

    # output vertex buffer
    file.write( '\"point P\" [' )
    for v in mesh.vertices:
        file.write( utility.vec3tostr( v.co ) + " " )
    file.write( "]\n" )

    # output index buffer
    file.write( "\"integer indices\" [" )
    for p in mesh.polygons:
        if len(p.vertices) == 3:
            file.write( "%d %d %d " %( p.vertices[0] , p.vertices[1] , p.vertices[2] ) )
        elif len(p.vertices) == 4:
            file.write( "%d %d %d %d %d %d " % (p.vertices[0],p.vertices[1],p.vertices[2],p.vertices[0],p.vertices[2],p.vertices[3]))
        #for i in p.vertices:
        #    file.write("%d " % i)
    file.write( "]\n" )

    # end attribute
    file.write( "AttributeEnd\n" )

    file.close()