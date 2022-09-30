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

from .common_functions import get_masterscene, detect_strip_type, switch_workspace, insert_clip, avail_screens
import bpy
import json
import os

# TODO: Handle different source framerates: it should be best to use master scene fps in
#   range scene. but does this handle the frame number correctly? Do the frame start / end etc. values
#   os strips already handle the fps conversion between source and scene?

# FIXME: scene switching via linking copies the eswc_info and vice versa!

# TODO: handle relative / absolute file paths correctly, so that ranges saved in the text files
#   keep the correct reference even when moving the project

NAME_RANGESCENE = 'SunTools_Edit_Range'

class OperatorEditRange(bpy.types.Operator):
    bl_idname = "file.moviemanager_edit_range"
    bl_label = "Edit Range"
    bl_description = "Edit the Range of the selected clip in the File Browser. Use the new scene's Start and end Frame"
    

    NAME_TEXT_RANGES = 'SunTools_Edit_Range_Ranges'

    def invoke (self, context, event):
        masterscene = get_masterscene()
        if (masterscene is None):
            self.report({'ERROR_INVALID_INPUT'},'Please set a Timeline first.')
            return {'CANCELLED'}

        #get scene parameters
        params_selected_file = self.get_params_selected_file(context)
        if not params_selected_file:
            return {'CANCELLED'}
        filename = params_selected_file.filename

        if bpy.context.scene.suntools_info.timeline:
            print('MASTERSCENE')
            masterscene.suntools_info.edit_screen = bpy.context.window.workspace.name

        elif bpy.context.scene.name == NAME_RANGESCENE:
            masterscene.suntools_info.range_screen = bpy.context.window.workspace.name

        if not masterscene.suntools_info.range_screen:
            workspaces = avail_screens()
            workspace = workspaces[0][0]

            for ws in workspaces:
                if 'video editing' in ws[0].lower():
                    workspace = ws[0]

            masterscene.suntools_info.range_screen = workspace



        strip_type = detect_strip_type(filename)
        if (strip_type in ['MOVIE', 'SOUND']):
            path_source = os.path.join(params_selected_file.directory.decode(), filename)
            path_source = bpy.path.relpath(path_source)
            self.enter_edit_range_scene(context, masterscene, path_source, strip_type)
        else:
            self.report({'ERROR_INVALID_INPUT'}, 'Invalid file format')
            return {'CANCELLED'}

        return {'FINISHED'}
    
    def get_screen_areas_of_type(self, context, type):
        result = []
        for a in context.window.screen.areas:
            if a.type == type:
                result.append(a)
                
        return result
    
    def get_params_selected_file(self, context):
        areas_filebrowsers = self.get_screen_areas_of_type(context, 'FILE_BROWSER')
        if areas_filebrowsers:
            scene_parameters = areas_filebrowsers[0].spaces[0].params
        else:
            self.report({'ERROR_INVALID_INPUT'}, 'No visible File Browser')
            return None

        if not scene_parameters.filename:
            self.report({'ERROR_INVALID_INPUT'}, 'No file selected')
            return None
        
        return scene_parameters


    def enter_edit_range_scene(self, context, masterscene, path_source, strip_type):
        # if edit range scene exists, store the range and delete the scene
        if NAME_RANGESCENE in bpy.data.scenes:
            scene_range = bpy.data.scenes[NAME_RANGESCENE]
            self.store_ranges(scene_range)
            bpy.data.scenes.remove(scene_range)

        # create the new scene
        scene_range = self.create_new_scene_with_settings_from_masterscene(masterscene,
                                                                           NAME_RANGESCENE,
                                                                           path_source)

        # check if range for source path exists 
        ranges = self.get_ranges_file(path_source)
        if ranges is not None:
            self.insert_clip_ranges(scene_range, ranges, path_source, strip_type)
        else:
            self.insert_clip(scene_range, path_source, strip_type, 'range')

        # enter the scene
        context.window.scene = scene_range
        
        # if custom layout wanted, switch layout
        switch_workspace(masterscene.suntools_info.range_screen)
        
    def get_text_ranges(self):
        if NAME_RANGESCENE in bpy.data.texts:
            return bpy.data.texts[NAME_RANGESCENE]
        else:
            return bpy.data.texts.new(NAME_RANGESCENE)

    def get_ranges(self):
        text_ranges = self.get_text_ranges()
        if text_ranges.as_string():
            return json.loads(text_ranges.as_string())
        else:
            return {}

    def get_ranges_file(self, path_source):
        dict_ranges = self.get_ranges()
        if dict_ranges is not None:
            return dict_ranges.get(path_source, None)
        else:
            return None
        
    def store_ranges(self, scene_range):
        dict_ranges = self.get_ranges()
        
        path_source = scene_range.suntools_info.source_path

        dict_ranges[path_source] = self.get_ranges_in_scene(scene_range)
        self.dict_to_text_ranges(dict_ranges)
    
    def dict_to_text_ranges(self, dict):
        text_ranges = self.get_text_ranges()
        text_ranges.clear()
        text_ranges.from_string(json.dumps(dict, indent=4))
    
    def get_ranges_in_scene(self, scene):
        ranges = []
        for sequence in scene.sequence_editor.sequences:
            if sequence.type == scene.suntools_info.type_strip_range:
                ranges_sequence = {
                    'name': sequence.name,
                    'frame_final_start': sequence.frame_final_start,
                    'frame_final_end': sequence.frame_final_end
                }
                ranges.append(ranges_sequence)
            
        return ranges

    def insert_clip_ranges(self, scene, ranges, path_source, strip_type):
        for index, range in enumerate(ranges):
            strips_new = self.insert_clip(scene, path_source, strip_type, range['name'])
            
            for strip_new in strips_new:
                channel = strip_new.channel
                strip_new.frame_final_start = range['frame_final_start']
                strip_new.frame_final_end = range['frame_final_end']
                strip_new.channel = channel
        
    def insert_clip(self, scene, path_source, strip_type, name):
        masterscene = get_masterscene()
        strips_new = insert_clip(scene, path_source, strip_type, name, 0, 1,
                                 masterscene.suntools_info.p25_edit_range,
                                 masterscene.suntools_info.p50_edit_range,
                                 masterscene.suntools_info.p75_edit_range,
                                 masterscene.suntools_info.p100_edit_range,
                                 )

        if strips_new is None:
            raise ValueError('Strip type {} not supported'.format(strip_type))

        scene.frame_end = strips_new[0].frame_duration

        return strips_new

    def create_new_scene_with_settings_from_masterscene(self, masterscene, scene_name, source_path):
        bpy.context.window.scene = masterscene
        bpy.ops.scene.new(type='LINK_COPY')
        # bpy.context.scene.name = scene_name
        new_scene = bpy.context.scene
        new_scene.sequence_editor_create()
        new_scene.suntools_info.source_path = source_path
        new_scene.suntools_info.timeline = False

        new_scene.suntools_info.type_strip_range = detect_strip_type(source_path)
        new_scene.name = scene_name

        # new_scene.render.resolution_x = masterscene.render.resolution_x
        # new_scene.render.resolution_y = masterscene.render.resolution_y
        # new_scene.render.resolution_percentage = masterscene.render.resolution_percentage
        # new_scene.render.fps = masterscene.render.fps
        # new_scene.sync_mode = masterscene.sync_mode
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

        if bpy.context.scene.name == NAME_RANGESCENE:
            masterscene.suntools_info.range_screen = bpy.context.window.workspace.name

        # if custom layout wanted, switch layout
        switch_workspace(masterscene.suntools_info.edit_screen)
        bpy.context.window.scene = masterscene

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
        
        if strip_to_insert is None:
            return
        
        if (strip_to_insert.type == 'MOVIE' or 'SOUND'):
            range_scene_name = bpy.context.scene.name
            bpy.context.window.scene = masterscene

            frame_start, frame_final_start, frame_final_end, channel = \
                self.get_destination_start_end_frames_and_channel(range_scene_name, strip_to_insert, masterscene)
            print(frame_start)
            strips_new = insert_clip(
                masterscene,
                strip_to_insert.filepath,
                strip_to_insert.type,
                strip_to_insert.name,
                frame_start,
                channel,
                masterscene.suntools_info.p25_edit_range,
                masterscene.suntools_info.p50_edit_range,
                masterscene.suntools_info.p75_edit_range,
                masterscene.suntools_info.p100_edit_range,
            )
            
            if strips_new is None:
                return

            self.apply_in_and_out_points(masterscene, strip_to_insert, frame_final_start, frame_final_end, strips_new)

            # change visible scene back
            bpy.context.window.scene = bpy.data.scenes[range_scene_name]

            return {'FINISHED'}
        else:
            self.report({'ERROR_INVALID_INPUT'}, 'Please select a sound or movie strip.')
            return {'CANCELLED'}

    def get_destination_start_end_frames_and_channel(self, range_scene_name, strip_to_insert, masterscene):
        # Get current frame and channel.
        # If sequences are selected in the master scene, set it to the active strip for 2-point editing
        if bpy.context.selected_sequences and masterscene.sequence_editor.active_strip:
            frame_final_start = masterscene.sequence_editor.active_strip.frame_final_end
            channel = masterscene.sequence_editor.active_strip.channel
        else:
            frame_final_start = bpy.context.scene.frame_current
            channel = masterscene.suntools_info.channel

        frame_final_end = frame_final_start + strip_to_insert.frame_final_duration
        frame_start = frame_final_start - (strip_to_insert.frame_final_start - strip_to_insert.frame_start)

        # If there is a selected strip, limit the length of the new one
        try:
            for selected_sequence in bpy.context.selected_sequences:
                print(selected_sequence)
                if frame_final_start < selected_sequence.frame_final_start < frame_final_end:
                    frame_final_end = selected_sequence.frame_final_start
                    break
        except:
            print("no selected sequences")

        return frame_start, frame_final_start, frame_final_end, channel

    def apply_in_and_out_points(self, masterscene, strip_to_insert, frame_final_start, frame_final_end, strips):
        # Apply in and out points
        if (strip_to_insert.type == 'MOVIE' and masterscene.suntools_info.meta == True):
            bpy.ops.sequencer.meta_make()
        for strip in strips:
            channel = strip.channel
            strip.frame_final_start = frame_final_start
            strip.frame_final_end = frame_final_end
            strip.channel = channel
