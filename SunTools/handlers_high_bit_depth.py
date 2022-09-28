##### Handlers for High Bit Depth Fix

LABEL_ID = 'HighBitDepth_'

import shutil
from os import path, makedirs
import bpy
import subprocess
from bpy.app.handlers import persistent
import os
from SunTools.common_functions import render_current_frame_strip_to_image, check_sequence_current_darktable
from tempfile import TemporaryDirectory
from shutil import copyfile

# todo: delete frames post render

def apply_darktable_sequence(sequence, scene):
    sequence.source_darktable = sequence.filepath
    sequence.frame_final_start_darktable = sequence.frame_final_start
    sequence.frame_final_end_darktable = sequence.frame_final_end
    sequence.frame_offset_start_darktable = sequence.frame_offset_start

    sequence.frame_final_start_darktable_set = True
    sequence.frame_final_end_darktable_set = True
    sequence.frame_offset_start_darktable_set = True
    with TemporaryDirectory() as path_tempdir:
        filename_image_raw = f'{sequence.name}.tif'
        filename_output_darktable = f'img_dt.tif'
        filename_output_darktable_video = f'{sequence.name}_dt.mov'
        path_image_raw = str(os.path.join(path_tempdir, filename_image_raw))
        path_image_darktable = str(os.path.join(path_tempdir, filename_output_darktable))

        render_current_frame_strip_to_image(sequence, bpy.context.scene, path_image_raw)
        path_xmp = os.path.join(path_tempdir, filename_image_raw + '.xmp')

        if sequence.xmp_darktable != '':
            with open(path_xmp, 'w') as f:
                f.write(sequence.xmp_darktable)

        # TODO: use wide-gamut color space that is also supported in blender out of the box...
        cmd = [
            'darktable-cli',
            path_image_raw,
            path_xmp,
            path_image_darktable,
            # '--icc-type',
            # 'ADOBERGB'
        ]
        print(f'Processing image {path_image_raw} with darktable. Output: {path_image_darktable}')
        subprocess.run(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE)

        subprocess.run(['ls', path_tempdir])
        # TODO: convert via FFMPEG to Video

        path_video_darktable_persistent = os.path.join(bpy.app.tempdir, filename_output_darktable_video)
        print(f'Converting image {path_image_darktable} to video {path_video_darktable_persistent}')
        cmd = [
            'ffmpeg',
            '-i',
            path_image_darktable,
            '-c:v',
            'libx264',
            '-crf',
            '0',
            '-preset',
            'ultrafast',
            # '-pix_fmt',
            # 'yuv422p10le',
            '-y',
            # '-update',
            # '-vframes',
            # '1',
            path_video_darktable_persistent
        ]
        subprocess.run(cmd)
    sequence.filepath = path_video_darktable_persistent
    sequence.frame_final_start = sequence.frame_final_start_darktable
    sequence.frame_final_end = sequence.frame_final_end_darktable
    sequence.frame_offset_start = sequence.frame_offset_start_darktable

@persistent
def render_pre_sequencer(scene):
    if scene.eswc_info.bool_use_high_bit_depth_fix:
        apply_function_compositing_scene(scene, render_pre)

    # TODO: darktable
    # TODO: Handle color spaces with darktable: in darktable-cli, use Adobe RGB output color space and
    #   set the corresponding input color space for the strip in blender.
    #   REMEMBER to reset the color space to previous value in post_sequencer!

    # TODO: refactor into separate file
    if scene.suntools_info.render_darktable:
        for sequence in scene.sequence_editor.sequences_all:
            if check_sequence_current_darktable(sequence, scene):
                apply_darktable_sequence(sequence, scene)



@persistent
def render_post_sequencer(scene):
    # TODO: darktable: reset sources of strips
    if scene.suntools_info.render_darktable:
        for sequence in scene.sequence_editor.sequences_all:
            if check_sequence_current_darktable(sequence, scene):
                sequence.filepath = sequence.source_darktable
                if sequence.frame_final_start_darktable_set and sequence.frame_final_end_darktable_set:
                    sequence.frame_final_start = sequence.frame_final_start_darktable
                    sequence.frame_final_end = sequence.frame_final_end_darktable
                    sequence.frame_offset_start = sequence.frame_offset_start_darktable
                    sequence.frame_final_start_darktable_set = False
                    sequence.frame_final_end_darktable_set = False
                    sequence.frame_offset_start_darktable_set = False

@persistent
def render_post_compositor(scene):
    if scene.use_nodes:
        #name_master_scene = scene.eswc_info.master_scene
        #if name_master_scene:
            #if bpy.data.scenes[name_master_scene].eswc_info.bool_use_high_bit_depth_fix:
                #insert_inputs_for_framegrabs(scene)

        insert_inputs_for_framegrabs(scene)

        # delete the temp folder with framegrabs
        path_temp_dir = get_dir_output()
        if path.exists(path_temp_dir):
            shutil.rmtree(path_temp_dir)

def render_pre(scene):
    if scene.use_nodes:
        insert_framegrabs_for_inputs(scene)

def insert_inputs_for_framegrabs(scene):
    tree = scene.node_tree

    # for all nodes
    for node in tree.nodes:
        # if the node is animation or image sequence and has image output connected, render framegrab and reconnect
        if node.bl_static_type == 'IMAGE' and node.label.startswith(LABEL_ID):
            insert_input_for_framegrab(scene, node)

def insert_input_for_framegrab(scene, node_framegrab):
    name_node_input = node_framegrab.label[len(LABEL_ID):]
    node_input = scene.node_tree.nodes[name_node_input]

    transfer_image_links_between_nodes(node_framegrab, node_input, scene)

    bpy.data.images.remove(node_framegrab.image)
    scene.node_tree.nodes.remove(node_framegrab)

def apply_function_compositing_scene(scene, function):
    if scene.sequence_editor:
        for sequence in scene.sequence_editor.sequences_all:
            if (sequence.type == 'SCENE'
                    and sequence.frame_final_start <= scene.frame_current
                    and sequence.frame_final_end > scene.frame_current
                    and sequence.scene.use_nodes):
                
                # it is pre render, so that the frame in the sequence's scene is not the correct frame.
                # hence, calculate the correct frame in the scene
                frame_in_sequence = scene.frame_current - sequence.frame_start + 1  # +1 because frames start at 1
                sequence.scene.frame_current = int(frame_in_sequence)
                function(sequence.scene)

def insert_framegrabs_for_inputs(scene):
    tree = scene.node_tree

    # for all nodes
    for node in tree.nodes:
        # if the node is animation or image sequence and has image output connected, render framegrab and reconnect
        if check_node_has_movie(node) and node.outputs['Image'].links:
            insert_framegrab_for_input(scene, node)

def check_node_has_movie(node):
    if node.bl_static_type == 'MOVIECLIP':
        return True
    if node.bl_static_type == 'IMAGE' and node.image.source == 'MOVIE':
        return True
    return False

def insert_framegrab_for_input(scene, node):
    # todo: mute the node? No, because outputs other than image might be needed.

    # render current frame of video file as 16 bit tiff
    filepath = get_filepath_movie(node)
    frame = get_frame_movie(node, scene)
    path_framegrab = render_framegrab(filepath, frame, node.name)

    # create image datablock with appropriate colorspace
    image_source = bpy.data.images.load(path_framegrab)
    image_source.source = 'FILE'
    ## set appropriate input options from the video input (e.g. Colorspace)
    colorspace_settings = get_colorspace(node)
    image_source.colorspace_settings.name = colorspace_settings.name
    image_source.colorspace_settings.is_data = colorspace_settings.is_data

    # create image input node with the tiff
    node_framegrab = scene.node_tree.nodes.new('CompositorNodeImage')
    node_framegrab.image = image_source

    # set property of image input node indicating that is was created for rendering, storing the ID of the original
    # node
    node_framegrab.label = '{}{}'.format(LABEL_ID, node.name)
    transfer_image_links_between_nodes(node, node_framegrab, scene)

def transfer_image_links_between_nodes(node_source, node_target, scene):
    # store all image connections
    links_outputs = node_source.outputs['Image'].links
    sockets_connected_to_source = [link.to_socket for link in links_outputs]

    # connect all connections that were present at the old input node to the new one
    socket_image = node_target.outputs['Image']
    for socket_connected_to_source in sockets_connected_to_source:
        scene.node_tree.links.new(socket_image, socket_connected_to_source)

    # links have changed. Thus, in order to delete the links from source node, the links must be
    # fetched again
    links_outputs = node_source.outputs['Image'].links

    # remove all connections from the output links
    for link in links_outputs:
        scene.node_tree.links.remove(link)

def get_frame_movie(node, scene):
    if node.bl_static_type == 'MOVIECLIP':
        movie = node.clip
    elif node.bl_static_type == 'IMAGE':
        movie = node
    else:
        raise NotImplementedError('Node {} not supported'.format(node.bl_static_type))

    return calc_frame_movie(movie, scene)

def calc_frame_movie(movie, scene):
    current_frame = scene.frame_current
    print(current_frame)

    return current_frame - movie.frame_start + movie.frame_offset

def get_filepath_movie(node):
    if node.bl_static_type == 'MOVIECLIP':
        return bpy.path.abspath(node.clip.filepath)
    elif node.bl_static_type == 'IMAGE':
        return bpy.path.abspath(node.image.filepath)
    else:
        raise NotImplementedError('Node {} not supported'.format(node.bl_static_type))

def get_colorspace(node):
    if node.bl_static_type == 'MOVIECLIP':
        return node.clip.colorspace_settings
    elif node.bl_static_type == 'IMAGE':
        return node.image.colorspace_settings
    else:
        raise NotImplementedError('Node {} not supported'.format(node.bl_static_type))

def render_framegrab(filepath, frame, filename):
    command_framerate = [
        "ffprobe",
        "-v",
        "0",
        "-of",
        "csv=p=0" ,
        "-select_streams",
        "v:0" ,
        "-show_entries",
        "stream=r_frame_rate",
        # f'\"{filepath}\"'
        filepath
    ]
    print(command_framerate)
    framerate = subprocess.run(command_framerate,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout.decode('utf-8').split('/')
    framerate_float = float(framerate[0]) / float(framerate[1])
    seconds = frame / framerate_float
    
    print(seconds)

    filename_with_extension = '{}.tiff'.format(filename)
    path_output = path.join(get_dir_output(), filename_with_extension)

    args = [
        '-ss',
        str(seconds),
        '-i',
        filepath,
        '-y',
        '-pix_fmt',
        'rgb48',
        '-frames:v',
        '1',
        path_output
    ]
    subprocess.call(['ffmpeg'] + args)
    # return r'/home/bjoern/Downloads/darktable_exported/YR0001552.jpg'
    return path_output

# def get_path_dir_output():
#     path_blend = bpy.path.abspath('.')
#     return path.join(path_blend, 'temp_high_bit_depth')


def get_dir_output():
    path_dir_output = os.path.join(bpy.app.tempdir, 'framegrabs_suntools')

    # create directory
    if not path.exists(path_dir_output):
        makedirs(path_dir_output)
    return path_dir_output

def register_handlers():
    bpy.app.handlers.render_pre.append(render_pre_sequencer)
    bpy.app.handlers.render_post.append(render_post_compositor)
    bpy.app.handlers.render_post.append(render_post_sequencer)
    bpy.app.handlers.render_cancel.append(render_post_compositor)
    bpy.app.handlers.render_cancel.append(render_post_sequencer)

def unregister_handlers():
    bpy.app.handlers.render_pre.remove(render_pre_sequencer)
    bpy.app.handlers.render_post.remove(render_post_compositor)
    bpy.app.handlers.render_post.remove(render_post_sequencer)
    bpy.app.handlers.render_cancel.remove(render_post_compositor)
    bpy.app.handlers.render_cancel.remove(render_post_sequencer)

