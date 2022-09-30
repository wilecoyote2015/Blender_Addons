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
from .constants import *
from subprocess import run

# TODO: cleanup Suntools Comp VSE Merge

def set_scene_fps_to_clip_fps(scene, strip):
    if strip.type in ('MOVIE', 'MOVIECLIP'):
        scene.render.fps_base = int(round(strip.fps)) / strip.fps
        scene.render.fps = int(round(strip.fps))

def check_sequence_current_darktable(strip, scene):
    # TODO: correct boundaries?
    has_playhead =  scene.frame_current >= strip.frame_final_start and scene.frame_current <= strip.frame_final_end
    return getattr(strip, 'xmp_darktable', None) and strip.use_darktable and has_playhead and not strip.mute

def switch_screen(context, eswc_screen):
    bpy.context.window.workspace = bpy.data.workspaces[eswc_screen]

def render_current_frame_strip_to_image(strip, scene, path_output):
    frame_current = get_frame_current_strip(strip, scene)
    seconds_current = frame_current / strip.fps

    # Workaround for inaccurate input frame seeking with ffmpeg at some frames:
    #   use rough input frame seeking and then perform finer seeking for output.
    #   this way, decoding the whole video is still avoided.
    #   TODO: verify that this works properly
    position_start_miliseconds = int(round(seconds_current * 1e3))
    n_seconds_input, position_seek_output_miliseconds = divmod(position_start_miliseconds, 1000)

    cmd = [
        'ffmpeg',
        '-ss',
        str(n_seconds_input),
        # f'{int(round(seconds_current*1e3))}ms',
        '-i',
        bpy.path.abspath(strip.filepath),
        '-ss',
        f'{position_seek_output_miliseconds}ms',
        '-vframes',
        '1',
          '-y',
        path_output
    ]
    print(cmd)
    run(cmd)

def get_frame_current_strip(strip, scene):
    """0-indexed!"""
    return int(max(min(scene.frame_current - strip.frame_start, strip.frame_duration-1), 0))

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
    strips = [strip for strip in bpy.context.scene.sequence_editor.sequences_all if
              strip.type == 'META' and strip.is_composite]

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

def act_strip(context):
    try:
        return context.scene.sequence_editor.active_strip
    except AttributeError:
        return None

def get_masterscene():
    masterscene = None

    for i in bpy.data.scenes:
        if (i.suntools_info.timeline == True):
            masterscene = i
            break

    return masterscene

def detect_strip_type(filepath):
    imb_ext_image = [
    # IMG
    ".png",
    ".tga",
    ".bmp",
    ".jpg", ".jpeg",
    ".sgi", ".rgb", ".rgba",
    ".tif", ".tiff", ".tx",
    ".jp2",
    ".hdr",
    ".dds",
    ".dpx",
    ".cin",
    ".exr",
    # IMG QT
    ".gif",
    ".psd",
    ".pct", ".pict",
    ".pntg",
    ".qtif",
    ]

    imb_ext_movie = [
    ".avi",
    ".flc",
    ".mov",
    ".movie",
    ".mp4",
    ".m4v",
    ".m2v",
    ".m2t",
    ".m2ts",
    ".mts",
    ".mv",
    ".avs",
    ".wmv",
    ".ogv",
    ".dv",
    ".mpeg",
    ".mpg",
    ".mpg2",
    ".vob",
    ".mkv",
    ".flv",
    ".divx",
    ".xvid",
    ".mxf",
    ]

    imb_ext_audio = [
    ".wav",
    ".ogg",
    ".oga",
    ".mp3",
    ".mp2",
    ".ac3",
    ".aac",
    ".flac",
    ".wma",
    ".eac3",
    ".aif",
    ".aiff",
    ".m4a",
    ]

    extension = os.path.splitext(filepath)[1]
    extension = extension.lower()
    if extension in imb_ext_image:
        type = 'IMAGE'
    elif extension in imb_ext_movie:
        type = 'MOVIE'
    elif extension in imb_ext_audio:
        type = 'SOUND'
    else:
        type = None

    return type

# def switch_workspace(name_workspace):
#     bpy.context.window.workspace = bpy.data.workspaces[name_workspace]

def switch_workspace(screen_selection):

    bpy.context.window.workspace = bpy.data.workspaces[screen_selection]

def avail_screens():
    items = []
    for i, elem in enumerate(bpy.data.workspaces):
        items.append((elem.name, elem.name, elem.name))
    return items

def insert_clip(scene, path_source, strip_type, name, frame_start, channel,
                p_25, p_50, p_75, p_100):
    frame_start = int(frame_start)
    path_source_abs = bpy.path.abspath(path_source)
    strips_new = []
    if (strip_type == 'MOVIE'):
        strips_new.append(
            scene.sequence_editor.sequences.new_movie(
                name,
                frame_start=frame_start,
                filepath=path_source_abs,
                channel=channel
            )
        )
        try:
            strips_new.append(
                scene.sequence_editor.sequences.new_sound(
                    name,
                    frame_start=frame_start,
                    filepath=path_source_abs,
                    channel=channel+1
                )
            )
        except:
            pass

        strips_new[0].use_proxy = True
        strips_new[0].proxy.build_25 = p_25
        strips_new[0].proxy.build_50 = p_50
        strips_new[0].proxy.build_75 = p_75
        strips_new[0].proxy.build_100 = p_100


    elif (strip_type == 'SOUND'):
        strips_new.append(
            scene.sequence_editor.sequences.new_sound(
                name,
                frame_start=frame_start,
                filepath=path_source_abs,
                channel=channel
            )
        )
    else:
        return None

    
    return strips_new

def get_filepath_strip(strip):
    if strip.type == 'IMAGE':
        return strip.directory

    elif strip.type == 'MOVIE':
        # Get source of strip and add strip path
        return strip.filepath

