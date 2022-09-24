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

