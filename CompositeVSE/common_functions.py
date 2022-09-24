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
import os

DEFAULT = '__default__'
SETTINGS_STRIP_COPY_TO_META = [
        # TODO: Update this for all relevant current attributes
        # TODO: Also include keyframes etc.!
        #   Is there a convenient way to copy all animation, transform, modifiers etc. between strips (or even better, link them)?
        'blend_type',
        'blend_alpha',
        'use_flip_x',
        'use_flip_y',
        # 'use_translation',
        # 'use_crop',
        'strobe',
        # 'playback_direction',
        'color_saturation',
        'color_multiply',
        'use_float',
        ['crop', 'min_x'],
        ['crop', 'max_x'],
        ['crop', 'min_y'],
        ['crop', 'max_y'],
        ['transform', 'offset_x'],
        ['transform', 'offset_y'],
    ]

SETTINGS_RESET_SOURCE_STRIP = {
        # TODO: Some properties must be set to custom values (e.g. blend_alpha, which will be reset to 0 otherwise)
        'blend_type': 'ALPHA_OVER',
        'blend_alpha': 1.,
        'use_flip_x': DEFAULT,
        'use_flip_y': DEFAULT,
        # 'use_translation',
        # 'use_crop',
        'strobe': DEFAULT,
        # 'playback_direction',
        'color_saturation': DEFAULT,
        'color_multiply': DEFAULT,
        'use_float': DEFAULT,
        ('crop', 'min_x'): DEFAULT,
    ('crop', 'max_x'): DEFAULT,
    ('crop', 'min_y'): DEFAULT,
    ('crop', 'max_y'): DEFAULT,
    ('transform', 'offset_x'): DEFAULT,
    ('transform', 'offset_y'): DEFAULT,
}
SETTINGS_STRIP_COPY_TO_COMP_STRIP = [

]

def switch_screen(context, eswc_screen):
    bpy.context.window.workspace = bpy.data.workspaces[eswc_screen]

def select_only_strip(strip):
    # deselect all strips and select only the composite strip
    # todo: more elegant way to do this?
    bpy.ops.sequencer.select_all(action='SELECT')
    for i in bpy.context.selected_editable_sequences:
        if i.name != strip.name:
            i.select = False
    bpy.context.scene.sequence_editor.active_strip = strip
    # bpy.context.scene.update()

# function to toggle showing the compositions
def toggle_composition_visibility(self, context):
    # store strips first because direct iteration doesn't work when modifying strips
    strips = [strip for strip in bpy.context.scene.sequence_editor.sequences_all if strip.type == 'META' and strip.is_composite]

    for strip in strips:
        # if show compositions, replace the movie and image strips with their compositions
        for sequence in strip.sequences:
            if sequence.type == 'SCENE':
                sequence.mute = not bpy.context.scene.eswc_info.bool_show_compositions
            else:
                sequence.mute = bpy.context.scene.eswc_info.bool_show_compositions


        # set proxy settings
        # todo: might be better to store proxy settings for original strip and composition separately.


def apply_proxy_settings_to_strip(strip, dict_settings):
    if dict_settings is not None:
        strip.use_proxy = True
        for setting, value in dict_settings.items():
            setattr(strip.proxy, setting, value)
    else:
        strip.use_proxy = False

def store_proxy_settings(strip):
    
    if strip.proxy is None:
        return None
    
    settings = [
        'build_100',
        'build_50',
        'build_25',
        'build_75',
        'build_free_run',
        'build_free_run_rec_date',
        'build_record_run',
        'directory',
        'filepath',
        'quality',
        'timecode',
        'use_overwrite',
        'use_proxy_custom_directory',
        'use_proxy_custom_file'
    ]
    
    result = {}
    for setting in settings:
        result[setting] = getattr(strip.proxy, setting)

    return result

def get_default(holder, prop_name):
    prop = holder.bl_rna.properties[prop_name]
    default_array = getattr(prop, 'default_array', None)
    # default_flag = getattr(prop, 'default_flag', None)
    print(prop_name)
    # if default_array is not None:
    #     default = [v for v in default_array]
        # return
    # if default_flag is not None:
    #     return default_flag
    # else:
    default = prop.default



    return default

def reset_settings_strip(strip, settings):
    for setting, value in settings.items():
        if isinstance(setting, (list, tuple)):
            attr = getattr(strip, setting[0])
            if attr is not None:
                setattr(attr, setting[1], get_default(attr, setting[1]) if value == DEFAULT else value)

        else:
            if getattr(strip, setting):
                setattr(strip, setting, get_default(strip, setting) if value == DEFAULT else value)

def copy_settings_to_strip(strip_a, strip_b, settings):
    '''
    Copy all listed settings for scene strip A scene_a
    to match original scene strip B
    '''
    # todo: if setting is list, get until last one
    for setting in settings:
        if isinstance(setting, (list, tuple)):
            attr_scene_b = getattr(strip_b, setting[0])
            attr_scene_a = getattr(strip_a, setting[0])
            if attr_scene_a is not None:
                setattr(attr_scene_b, setting[1], getattr(attr_scene_a, setting[1]))
        else:
            if getattr(strip_a, setting):
                setattr(strip_b, setting, getattr(strip_a, setting))

    
def insert_scene_timeline(new_scene, original_strip, context):

    # deselect all other strips
    bpy.ops.sequencer.select_all(action='DESELECT')
    context.scene.sequence_editor.active_strip = None

    # Add newly created scene to the timeline
    # if view comps mode, replace the movie strip with the scene strip.
    # else, assign the composition name to the movie strip
    # todo: add directly to sequencer instead of using operator
    bpy.ops.sequencer.scene_strip_add(
        frame_start=int(original_strip.frame_start),
        replace_sel=True, scene=new_scene.name)

    # make composite strip  active
    # todo: is this really the correct way to get the newly created strip?
    composite_strip = context.scene.sequence_editor.active_strip

    transfer_trip_properties_movie_to_composition(original_strip, composite_strip, context)
    
    return composite_strip
    
def transfer_trip_properties_movie_to_composition(strip_to_replace, strip_replacement, context):
    """
    Replace a strip by another strip
    """
    # TODO: update: only copy settings to the comp scene strip that
    #   are NOT transferred to the parent meta strip
    eswc_info = context.scene.eswc_info

    # name_strip = strip_to_replace.name

    # Update scene
    # context.scene.update()

    # # Camera override
    # todo: this in insert_scene_timeline?
    # strip_replacement.scene_camera = editing_scene.camera

    # context.scene.update()

    # Copy Settings
    # if eswc_info.settings == "All":
    #     copy_all_settings(strip_replacement, strip_to_replace)

    copy_settings_to_strip(strip_replacement, strip_to_replace, SETTINGS_STRIP_COPY_TO_COMP_STRIP)
    # copy proxy settings
    dict_proxy_settings = store_proxy_settings(strip_to_replace)
    apply_proxy_settings_to_strip(strip_replacement, dict_proxy_settings)

    channel = strip_to_replace.channel
    frame_start = strip_to_replace.frame_start
    offset_start = strip_to_replace.frame_offset_start
    offset_end = strip_to_replace.frame_offset_end

    # # delete the strip
    # select_only_strip(strip_to_replace)
    # bpy.ops.sequencer.delete()

    # set the correct channel and name
    # strip_replacement.name = name_strip

    strip_replacement.frame_offset_start = offset_start
    strip_replacement.frame_offset_end = offset_end
    strip_replacement.frame_start = frame_start

    strip_replacement.channel = channel

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

def avail_screens():
    items = []
    for i, elem in enumerate(bpy.data.workspaces):
        items.append((elem.name, elem.name, elem.name))
    return items