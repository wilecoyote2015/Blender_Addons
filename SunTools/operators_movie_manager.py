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
from common_functions import get_masterscene, detect_strip_type

class OperatorSetTimeline (bpy.types.Operator):
    bl_idname = "sequencer.moviemanager_set_timeline"
    bl_label = "Set as Timeline"
    bl_description = "Set this scene as Timeline"

    def invoke (self, context, event):
        for i in bpy.data.scenes:
            i.timeline = False

        bpy.context.scene.timeline = True

        return {'FINISHED'}

class OperatorHideSequences (bpy.types.Operator):
    bl_idname = "sequencer.moviemanager_hide"
    bl_label = "Hide"
    bl_description = "Hide clips that are not useful"

    def invoke (self, context, event):
        for scene_clip in bpy.data.scenes:
            source_path = scene_clip.source_path
            if (source_path != "none"):
                self.hide_file(source_path, scene_clip)

        return {'FINISHED'}

    def hide_file(self, filepath, scene_clip):
        path_directory, filename = os.path.split(filepath)

        changed = False
        if (filename[0] == "." and scene_clip.good_clip == True):
            filename_new = filename[1:]
            changed = True
        elif (filename[0] != "." and scene_clip.good_clip == False):
            filename_new = "." + filename
            changed = True
        if (changed == True):
            filepath_new = path_directory + filename_new
            os.rename(filepath, filepath_new)

            for sequence_scene in bpy.data.scenes:
                if (sequence_scene.source_path == filepath):
                    sequence_scene.source_path = filepath_new
                try:
                    for sequence in sequence_scene.sequence_editor.sequences_all:
                        if (sequence.filepath == bpy.path.relpath(filepath)):
                            sequence.filepath = bpy.path.relpath(filepath_new)
                except:
                    print("hadn't a sequencer. poor little scene!")


class OperatorCreateProxies(bpy.types.Operator):
    """ Automatically create proxies with given settings for all strips in the directory
    """
    bl_idname = "file.moviemanager_proxy"
    bl_label = "Create Proxies"

    def invoke(self, context, event ):
        name_scene_current = bpy.context.scene.name
        
        masterscene = get_masterscene()
        if (masterscene is None):
            self.report({'ERROR_INVALID_INPUT'},'Please set a Timeline first.')
            return {'CANCELLED'}

        if (masterscene.p50 == False and masterscene.p25 == False and masterscene.p75 == False and masterscene.p100 == False ):
            self.report({'ERROR_INVALID_INPUT'},'No Proxies to create!.')
            return {'CANCELLED'}

        #get directory
        for a in context.window.screen.areas:
            if a.type == 'FILE_BROWSER':
                directory = a.spaces[0].params.directory
                break
        try:
            directory
        except:
            self.report({'ERROR_INVALID_INPUT'}, 'No visible File Browser')
            return {'CANCELLED'}

        #Change the current area to VSE so that we can also call the operator from any other area type.
        bool_IsVSE = True
        native_area_type = 'SEQUENCE_EDITOR'
        if (bpy.context.area.type != 'SEQUENCE_EDITOR'):
            native_area_type = bpy.context.area.type
            bpy.context.area.type = 'SEQUENCE_EDITOR'
            bool_IsVSE = False

        # store whether to search files recursively from current scene, as qID will have it
        # set to False
        proxy_recursive = bpy.context.scene.proxy_recursive

        #Check if scene exists, if not -> new
        self.switch_to_scene(scene_name='qID')

        ## Get files in directory
        if proxy_recursive:
            filepaths = []
            for root, dirs, files in os.walk(directory):
                # only add files if they are not in a proxy directory
                if 'BL_proxy' not in root:
                    filepaths.extend([os.path.join(root, f) for f in files])
        else:
            filepaths = [ os.path.join(directory, f) for f in os.listdir(directory) if os.isfile(os.path.join(directory,f)) ]

        strips_created = self.create_strips_and_set_proxy_settings(masterscene, filepaths)

        if strips_created:
            self.report({'INFO'}, 'Generating Proxies. Blender freezes until job is finished.')
            bpy.ops.sequencer.select_all(action='SELECT')
            bpy.ops.sequencer.rebuild_proxy()
            bpy.ops.sequencer.delete()
        else:
            self.report({'INFO'},'No video files found.')

        if (bool_IsVSE == False):
            bpy.context.area.type = native_area_type

        #OperatorToTimeline.invoke(self, context, event
        # switch back to initial scene
        self.switch_to_scene(scene_name=name_scene_current)

        self.report({'INFO'}, 'Finished proxy generation.')

        return {'FINISHED'}

    def switch_to_scene(self, scene_name):
        """ If a scene of given name does not exist, create it. Then switch context to the scene
        
        :param scene_name: Name of the scene
        :return: 
        """
        scene_exists = False
        for i in bpy.data.scenes:
            if i.name == scene_name:
                scene_exists = True

        if (scene_exists == True):
            bpy.context.screen.scene = bpy.data.scenes[scene_name]
        else:
            new_scene = bpy.data.scenes.new(scene_name)

        scene = bpy.data.scenes[scene_name]
        bpy.context.screen.scene = scene

    def create_strips_and_set_proxy_settings(self, masterscene, filepaths):
        strips_created = False
        for path in filepaths:
            filename = os.path.basename(path)
            strip_type = detect_strip_type(filename)

            if (strip_type == 'MOVIE'):
                print('creating proxy for {}'.format(path))
                strips_created = True
                bpy.ops.sequencer.movie_strip_add(filepath=path)
                for sequence in bpy.context.scene.sequence_editor.sequences:
                    if (sequence.type == 'MOVIE'):
                        sequence.use_proxy = True
                        if (masterscene.p25 == True):
                            sequence.proxy.build_25 = True
                        if (masterscene.p50 == True):
                            sequence.proxy.build_50 = True
                        if (masterscene.p75 == True):
                            sequence.proxy.build_75 = True
                        if (masterscene.p100 == True):
                            sequence.proxy.build_100 = True

        return strips_created

class OperatorUnmeta(bpy.types.Operator):
    bl_idname = "sequencer.moviemanager_unmeta"
    bl_label = "Unmeta"
    bl_description = "Unmeta and trim all containing strip so meta strip"

    def invoke(self, context, event):
        for meta_strip in bpy.context.selected_sequences:
            if (meta_strip.type == 'META'):
                channel = meta_strip.channel
                self.separate_meta_strip(meta_strip)
                self.apply_meta_strip_channel(channel)
        return {'FINISHED'}

    def separate_meta_strip(self, meta_strip):
        frame_final_start = meta_strip.frame_final_start
        frame_final_end = meta_strip.frame_final_end
        bpy.ops.sequencer.select_all(action='DESELECT')
        meta_strip.select = True
        bpy.context.scene.sequence_editor.active_strip = meta_strip
        bpy.ops.sequencer.meta_separate()
        for sequence_from_meta in bpy.context.selected_sequences:
            sequence_from_meta.frame_final_start = frame_final_start
            sequence_from_meta.frame_final_end = frame_final_end

    def apply_meta_strip_channel(self, channel):
        for sequence_from_meta in reversed(bpy.context.selected_sequences):
            if (sequence_from_meta.type == 'MOVIE'):
                sequence_from_meta.channel = channel
            else:
                sequence_from_meta.channel = channel + 1
