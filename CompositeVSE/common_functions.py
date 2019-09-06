# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

import bpy
import common_functions

def switch_screen(context, eswc_screen):
    # get the name of the desired composite screen
    for index, screen in enumerate(bpy.data.screens):
        if index == int(eswc_screen):
            screen_name = screen.name
            break

    # change current screen to the composite screen
    for screen in bpy.data.screens:
        bpy.ops.screen.screen_set(delta=1)
        if context.screen.name == screen_name:
            break


def select_only_strip(strip):
    # deselect all strips and select only the composite strip
    # todo: more elegant way to do this?
    bpy.ops.sequencer.select_all(action='SELECT')
    for i in bpy.context.selected_editable_sequences:
        if i.name != strip.name:
            i.select = False
    bpy.context.scene.sequence_editor.active_strip = strip
    bpy.context.scene.update()


def create_strip_for_composition(strip_composition):
    eswc_info_composite = strip_composition.scene.eswc_info
    path_input = eswc_info_composite.path_input

    # deselect all other strips
    bpy.ops.sequencer.select_all(action='DESELECT')

    new_strip = None
    if eswc_info_composite.type_original_strip == 'MOVIE':
        bpy.ops.sequencer.movie_strip_add(filepath=path_input, replace_sel=True, sound=False)
        bpy.context.scene.update()
        new_strip = bpy.context.scene.sequence_editor.active_strip
    elif eswc_info_composite.type_original_strip == 'IMAGE':
        # todo: respect files. For this, a new string prop collection holding all files
        # of the source image strip must be added to composition scene.
        # also, the check if a scene already corresponds to an image strip then also has to compare
        # this list of files because if other files are used, it is not the same source albeit
        # it referes to the same directory.
        bpy.ops.sequencer.image_strip_add(directory=path_input, replace_sel=True)
        bpy.context.scene.update()
        new_strip = bpy.context.scene.sequence_editor.active_strip

    if new_strip is not None:
        new_strip.composite_scene = strip_composition.scene.name
        common_functions.replace_strip(strip_composition, new_strip, bpy.context)
    else:
        print({'ERROR_INVALID_INPUT'}, 'The following composite strip refers to an invalid strip type:'
                                       ' {}'.format(strip_composition.name))

    return new_strip


# function to toggle showing the compositions
def toggle_composition_visibility(self, context):
    # store strips first because direct iteration doesn't work when modifying strips
    strips = [strip for strip in bpy.context.scene.sequence_editor.sequences_all]

    for strip in strips:
        # if show compositions, replace the movie and image strips with their compositions
        if bpy.context.scene.eswc_info.bool_show_compositions:
            if strip.type in ['MOVIE', 'IMAGE']:
                if strip.composite_scene != "":
                    composite_scene = bpy.data.scenes[strip.composite_scene]
                    common_functions.insert_scene_timeline(composite_scene, strip, bpy.context)
        # if not show compositions, the compositions are to be replaced by the movie strips
        elif strip.type == 'SCENE' and strip.scene.eswc_info.path_input != "":
            new_strip = create_strip_for_composition(strip)

def copy_all_settings(scene_a, scene_b):
    '''
    Copy all listed settings for scene strip A scene_a.node_tree.use_opencl
    to match original scene strip B
    '''
    # scene_a.use_translation =  scene_b.use_translation
    scene_a.use_reverse_frames = scene_b.use_reverse_frames
    scene_a.use_float = scene_b.use_float
    scene_a.use_flip_y = scene_b.use_flip_y
    scene_a.use_deinterlace = scene_b.use_deinterlace
    scene_a.use_default_fade = scene_b.use_default_fade
    scene_a.strobe = scene_b.strobe
    scene_a.speed_factor = scene_b.speed_factor
    scene_a.mute = scene_b.mute
    scene_a.lock = scene_b.lock
    scene_a.effect_fader = scene_b.effect_fader
    scene_a.color_saturation = scene_b.color_saturation
    scene_a.color_multiply = scene_b.color_multiply
    scene_a.blend_type = scene_b.blend_type
    scene_a.blend_alpha = scene_b.blend_alpha
    scene_a.use_flip_x = scene_b.use_flip_x
    
def insert_scene_timeline(new_scene, original_strip, context):

    # deselect all other strips
    bpy.ops.sequencer.select_all(action='DESELECT')
    context.scene.sequence_editor.active_strip = None

    # Add newly created scene to the timeline
    # if view comps mode, replace the movie strip with the scene strip.
    # else, assign the composition name to the movie strip
    bpy.ops.sequencer.scene_strip_add(
        frame_start=original_strip.frame_start,
        replace_sel=True, scene=new_scene.name)

    context.scene.update()

    # make composite strip  active
    # todo: is this really the correct way to get the newly created strip?
    composite_strip = context.scene.sequence_editor.active_strip

    replace_strip(original_strip, composite_strip, context)
    
def replace_strip(strip_to_replace, strip_replacement, context):
    """
    Replace a strip by another strip
    """
    eswc_info = context.scene.eswc_info

    name_strip = strip_to_replace.name

    # Update scene
    context.scene.update()

    # # Camera override
    # todo: this in insert_scene_timeline?
    # strip_replacement.scene_camera = editing_scene.camera

    context.scene.update()

    # Copy Settings
    if eswc_info.settings == "All":
        copy_all_settings(strip_replacement, strip_to_replace)

    if eswc_info.bool_auto_proxy:
        a = strip_replacement
        setup_proxy(a, eswc_info, strip_replacement.name)

    # if any strips use the strip to replace as input, set input to new strip
    for sequence in context.scene.sequence_editor.sequences_all:
        if hasattr(sequence, 'input_1') and sequence.input_1 == strip_to_replace:
            sequence.input_1 = strip_replacement
        if hasattr(sequence, 'input_2') and sequence.input_2 == strip_to_replace:
            sequence.input_2 = strip_replacement

    channel = strip_to_replace.channel
    frame_start = strip_to_replace.frame_start
    offset_start = strip_to_replace.frame_offset_start
    offset_end = strip_to_replace.frame_offset_end

    # delete the strip
    select_only_strip(strip_to_replace)
    bpy.ops.sequencer.delete()

    # set the correct channel and name
    strip_replacement.name = name_strip

    strip_replacement.frame_offset_start = offset_start
    strip_replacement.frame_offset_end = offset_end
    strip_replacement.frame_start = frame_start

    strip_replacement.channel = channel
    
def setup_proxy(strip, eswc_info, new_name):
    strip.use_proxy = True
    if (eswc_info.pq == "1"):
        strip.proxy.build_25 = True
    else:
        strip.proxy.build_25 = False
    if (eswc_info.pq == "2"):
        strip.proxy.build_50 = True
    else:
        strip.proxy.build_50 = False
    if (eswc_info.pq == "3"):
        strip.proxy.build_75 = True
    else:
        strip.proxy.build_75 = False
    if (eswc_info.pq == "4"):
        strip.proxy.build_100 = True
    else:
        strip.proxy.build_100 = False
    strip.use_proxy_custom_directory = True
    name = new_name
    proxy_folder = bpy.path.abspath("//.proxy")
    new_folder = os.path.join(proxy_folder, name)
    rel_folder = bpy.path.relpath(new_folder)
    strip.proxy.directory = rel_folder
    strip.proxy.quality = 90
    
def find_matching_compositions(strip):
    result = []
    for scene in bpy.data.scenes:
        if scene.eswc_info.path_input == get_filepath_strip(strip):
            result.append(scene)

    return result

def get_filepath_strip(strip):
    if strip.type == 'IMAGE':
        return strip.directory

    elif strip.type == 'MOVIE':
        # Get source of strip and add strip path
        return strip.filepath
