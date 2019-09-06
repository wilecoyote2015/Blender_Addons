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

from common_functions import get_masterscene, detect_strip_type
import bpy
import os

class OperatorEditRange(bpy.types.Operator):
    bl_idname = "file.moviemanager_edit_range"
    bl_label = "Edit Range"
    bl_description = "Edit the Range of the selected clip in the File Browser. Use the new scene's Start and end Frame"

    def invoke (self, context, event):

        masterscene = get_masterscene()
        if (masterscene is None):
            self.report({'ERROR_INVALID_INPUT'},'Please set a Timeline first.')
            return {'CANCELLED'}

        #get scene parameters
        for a in context.window.screen.areas:
            if a.type == 'FILE_BROWSER':
                scene_parameters = a.spaces[0].params
                break
        try:
            filename = scene_parameters.filename
        except:
            self.report({'ERROR_INVALID_INPUT'}, 'No visible File Browser')
            return {'CANCELLED'}

        if scene_parameters.filename == '':
            self.report({'ERROR_INVALID_INPUT'}, 'No file selected')
            return {'CANCELLED'}

        #Change the current area to VSE so that we can also call the operator from any other area type.
        bool_IsVSE = True
        if (bpy.context.area.type != 'SEQUENCE_EDITOR'):
            bpy.context.area.type = 'SEQUENCE_EDITOR'
            bool_IsVSE = False

        source_path = os.path.join(scene_parameters.directory, filename)
        strip_type = detect_strip_type(filename)
        scene_name = filename + "_Range"

        if (strip_type == 'MOVIE' or 'SOUND'):
            self.create_new_scene_with_strip_and_switch_to_scene(masterscene, source_path, strip_type, scene_name)
        else:
            self.report({'ERROR_INVALID_INPUT'}, 'Invalid file format')
            return {'CANCELLED'}

        if (masterscene.zoom == True and bool_IsVSE == True):
            bpy.ops.sequencer.view_selected()
        if (bool_IsVSE == False):
            bpy.context.area.type = 'FILE_BROWSER'

        #Change to custom layout if wanted.
        if (masterscene.custom_screen == True):
            for screen in bpy.data.screens:
                bpy.ops.screen.screen_set(delta=1)
                if (bpy.context.screen.name == masterscene.editing_range_screen):
                    break
            bpy.context.screen.scene = bpy.data.scenes[scene_name]

        return {'FINISHED'}

    def create_new_scene_with_strip_and_switch_to_scene(self, masterscene, source_path, strip_type, scene_name):
        # get the according scene
        scene_exists = False
        for scene in bpy.data.scenes:
            if scene.source_path == source_path:
                scene_exists = True
                scene_name = scene.name

        if (scene_exists == True):
            bpy.context.screen.scene = bpy.data.scenes[scene_name]
            bpy.context.scene.sync_mode = masterscene.sync_mode
        else:
            scene = self.create_new_scene_with_settings_from_masterscene(masterscene, scene_name, source_path)
            bpy.context.screen.scene = scene
            bpy.context.scene.sync_mode = masterscene.sync_mode

            if (strip_type == 'MOVIE'):
                bpy.ops.sequencer.movie_strip_add(frame_start=0, filepath=source_path)
            elif (strip_type == 'SOUND'):
                bpy.ops.sequencer.sound_strip_add(frame_start=0, filepath=source_path)

            bpy.context.scene.frame_end = bpy.context.scene.sequence_editor.active_strip.frame_final_duration

    def create_new_scene_with_settings_from_masterscene(self, masterscene, scene_name, source_path):
        new_scene = bpy.data.scenes.new(scene_name)
        scene_name = new_scene.name
        bpy.data.scenes[scene_name].source_path = source_path

        new_scene.render.resolution_x = masterscene.render.resolution_x
        new_scene.render.resolution_y = masterscene.render.resolution_y
        new_scene.render.resolution_percentage = masterscene.render.resolution_percentage
        new_scene.render.fps = masterscene.render.fps
        new_scene.frame_start = 0

        return new_scene

class OperatorBackToTimeline(bpy.types.Operator):
    bl_idname = "sequencer.moviemanager_switch_back_to_timeline"
    bl_label = "Get Back"

    def invoke(self, context, event ):

        masterscene = get_masterscene()
        if (masterscene is None):
            self.report({'ERROR_INVALID_INPUT'},'Please set a Timeline first.')
            return {'CANCELLED'}

        if (masterscene.custom_screen == True):
            for screen in bpy.data.screens:
                bpy.ops.screen.screen_set(delta=1)
                if (bpy.context.screen.name == masterscene.editing_screen):
                    break
            bpy.context.screen.scene = masterscene
        else:
            bpy.context.screen.scene = masterscene

        return {'FINISHED'}

class OperatorInsertStripIntoMasterscene(bpy.types.Operator):
    bl_idname = "sequencer.moviemanager_insert_strip_masterscene"
    bl_label = "Insert into editing scene"
    bl_description = "Insert the selected Strip into the Timeline of the Editing Scene"

    def invoke(self, context, event):
        """ Called from the range scene. Insert the selected clip into the masterscene,
            performing 2 or 3-point editing if strips are selected in the masterscene.
        """
        masterscene = get_masterscene()
        if (masterscene is None):
            self.report({'ERROR_INVALID_INPUT'}, 'Please set a Timeline first.')
            return {'CANCELLED'}

        strip_to_insert = bpy.context.scene.sequence_editor.active_strip
        if (strip_to_insert.type == 'MOVIE' or 'SOUND'):
            range_scene_name = bpy.context.scene.name
            bpy.context.screen.scene = masterscene

            frame_start, frame_final_start, frame_final_end, channel = self.get_destination_start_end_frames_and_channel(range_scene_name, strip_to_insert)
            if (strip_to_insert.type == 'MOVIE'):
                bpy.ops.sequencer.movie_strip_add(frame_start=frame_start, channel=channel, overlap=True, filepath=strip_to_insert.filepath)
            elif (strip_to_insert.type == 'SOUND'):
                bpy.ops.sequencer.sound_strip_add(frame_start=frame_start, channel=channel, overlap=True, filepath=strip_to_insert.sound.filepath)
            self.apply_in_and_out_points(masterscene, strip_to_insert, frame_final_start, frame_final_end, channel)

            # change visible scene back
            bpy.context.screen.scene = bpy.data.scenes[range_scene_name]

            return {'FINISHED'}
        else:
            self.report({'ERROR_INVALID_INPUT'}, 'Please select a sound or movie strip.')
            return {'CANCELLED'}

    def get_destination_start_end_frames_and_channel(self, range_scene_name, strip_to_insert):
        # Get current frame and channel.
        # If sequences are selected in the master scene, set it to the active strip for 2-point editing
        if (bpy.context.selected_sequences):
            frame_final_start = bpy.context.screen.scene.sequence_editor.active_strip.frame_final_end
            channel = bpy.context.screen.scene.sequence_editor.active_strip.channel
        else:
            frame_final_start = bpy.contex__init__.py__init__.pyt.scene.frame_current
            channel = bpy.data.scenes[range_scene_name].channel

        frame_final_end = frame_final_start + strip_to_insert.frame_final_duration
        frame_start = frame_final_start - (strip_to_insert.frame_final_start - strip_to_insert.frame_start)

        # If there is a selected strip, limit the length of the new one
        try:
            for selected_sequence in bpy.context.selected_sequences:
                if (selected_sequence.frame_final_start < frame_final_end and selected_sequence.frame_final_start > frame_final_start):
                    frame_final_end = selected_sequence.frame_final_start
        except:
            print("no selected sequences")

        return frame_start, frame_final_start, frame_final_end, channel

    def apply_in_and_out_points(self, masterscene, strip_to_insert, frame_final_start, frame_final_end, channel):
        # Apply in and out points
        if (strip_to_insert.type == 'MOVIE' and masterscene.meta == True):
            bpy.ops.sequencer.meta_make()
        for selected_sequence in bpy.context.selected_sequences:
            channel = selected_sequence.channel
            selected_sequence.frame_final_start = frame_final_start
            selected_sequence.frame_final_end = frame_final_end
            selected_sequence.channel = channel
