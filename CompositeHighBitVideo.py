
bl_info = {
    "name": "Composite High Bitdepth Video",
    "description": "Use high bitdepth video in compositor while rendering",
    "author": "Björn Sonnenschein",
    "version": (0, 1),
    "blender": (2, 80),
    "location": "Sequencer > UI panel, Node Editor > UI panel",
    "wiki_url": "None Yet"
                "None Yet",
    "tracker_url": "None"
                   "func=detail&aid=<number>",
    "category": "Compositing"}

import bpy
from bpy.app.handlers import persistent


### Properties for nodes
# bpy.types.CompositorNodeImage.high_bit_depth_source_node = bpy.props.StringProperty(
#     name="High Bit Depth source Node",
#     default=None
# )

label_id = 'HighBitDepth_'

@persistent
def render_post(scene):
    if scene.use_nodes:
        insert_inputs_for_framegrabs(scene)


def insert_inputs_for_framegrabs(scene):
    tree = scene.node_tree

    # for all nodes
    for node in tree.nodes:
        # if the node is animation or image sequence and has image output connected, render framegrab and reconnect
        if node.bl_static_type == 'IMAGE' and node.label.startswith(label_id):
            insert_input_for_framegrab(scene, node)

def insert_input_for_framegrab(scene, node_framegrab):
    name_node_input = node_framegrab.label[len(label_id):]
    node_input = scene.node_tree.nodes[name_node_input]
    
    transfer_image_links_between_nodes(node_framegrab, node_input, scene)

    bpy.data.images.remove(node_framegrab.image)
    scene.node_tree.nodes.remove(node_framegrab)

@persistent
def render_pre(scene):
    print('PRE')
    if scene.use_nodes:
        insert_framegrabs_for_inputs(scene)

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
    path_framegrab = render_framegrab(filepath, frame)

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
    node_framegrab.label = '{}{}'.format(label_id, node.name)
    transfer_image_links_between_nodes(node, node_framegrab, scene)

def transfer_image_links_between_nodes(node_source, node_target, scene):
    # store all image connections
    links_outputs = node_source.outputs['Image'].links
    sockets_linked = [link.to_socket for link in links_outputs]

    # remove all connections from the output links
    for link in links_outputs:
        scene.node_tree.links.remove(link)

    # connect all connections that were present at the old input node to the new one
    socket_image = node_target.outputs['Image']
    for socket_target in sockets_linked:
        link = scene.node_tree.links.new(socket_image, socket_target)

def get_frame_movie(node, scene):
    if node.bl_static_type == 'MOVIECLIP':
        movie = node.clip
    elif node.bl_static_type == 'IMAGE':
        movie = node.image
    else:
        raise NotImplementedError('Node {} not supported'.format(node.bl_static_type))
    
    return calc_frame_movie(movie, scene)

def calc_frame_movie(movie, scene):
    current_frame = scene.frame_current

    return current_frame - movie.frame_start + movie.frame_offset

def get_filepath_movie(node):
    if node.bl_static_type == 'MOVIECLIP':
        return bpy.path.abspath(node.clip.filepath)
    elif node.bl_static_type == 'Image':
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

def render_framegrab(filepath, frame):
    return r'/home/bjoern/Downloads/darktable_exported/YR0001552.jpg'
    # use FFMPEG to extract a framegrab
        

bpy.app.handlers.render_pre.append(render_pre)
bpy.app.handlers.render_post.append(render_post)


