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


bl_info = {
    "name": "SunTools",
    "description": "Define in- and outpoints of your material in the file browser",
    "author": "Björn Sonnenschein",
    "version": (1, 3),
    "blender": (2, 71, 0),
    "location": "File Browser > Tools",
    "warning": "Experimental",
    "wiki_url": "None Yet"
                "None Yet",
    "tracker_url": "None"
                   "func=detail&aid=<number>",
    "category": "Sequencer"}

import bpy, os
from os import listdir
from os.path import isfile, join

##TODO
# instead of setting area type for non-vse to file browser in edit range operator, save the current area type in a variable and switch back to it.
################################

scnType = bpy.types.Scene

###### Common Functions #######
def act_strip(context):
    try:
        return context.scene.sequence_editor.active_strip
    except AttributeError:
        return None


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

####### Scene Properties ########

### IOP Section 
BoolProperty = bpy.props.BoolProperty                              
scnType.custom_screen = BoolProperty( name="Custom Screen", 
                                     description = "Use a custom screen layout for range editing? ", 
                                     default=False )  
                                     
scnType.meta = BoolProperty( name="Metastrip", 
                                     description = "Combine audio and video into metastrip?? ", 
                                     default=False ) 
                                     
scnType.zoom = BoolProperty( name="Zoom", 
                                     description = "Zoom to the entire Clip after entering Edit Range? ", 
                                     default=False )  
                                     
scnType.show_options = BoolProperty( name="Show Options", 
                                     description = "", 
                                     default=False )  
                                     
scnType.p25 = BoolProperty( name="25%", 
                                     description = "Proxy sizes to be created", 
                                     default=False )  
                                     
scnType.p50 = BoolProperty( name="50%", 
                                     description = "Proxy sizes to be created", 
                                     default=False )
                                     
scnType.p75 = BoolProperty( name="75%", 
                                     description = "Proxy sizes to be created", 
                                     default=False )  
                                     
scnType.p100 = BoolProperty( name="100%", 
                                     description = "Proxy sizes to be created", 
                                     default=False )                                                                              
                                     
#Is it the timeline scene?                          
scnType.timeline = BoolProperty( name="Timeline", 
                                     description = "Is this your actual timeline?", 
                                     default=False)           

#Declare usefulness                                     
scnType.good_clip = BoolProperty( name="Good", 
                                     description = "Is this an useful Clip? ", 
                                     default=False )                              
                                     
#Define Screen to change to for editing range
StringProperty = bpy.props.StringProperty
editingrangestring = StringProperty(name="Editing Range Screen", description="The name of the screen layout you use for editing range", default="Video Editing" )
scnType.editing_range_screen = editingrangestring

#Define Screen to change to for editing
editingstring = StringProperty(name="Editing Screen", description="The name of the screen layout you use for editing", default="Video Editing" )
scnType.editing_screen = editingstring                                     

#Channel selector
IntProperty = bpy.props.IntProperty
intprop = IntProperty( name="Channel", description="Define into which channel the new strip will be inserted ", default=1, min=1, max=30, step=1)
scnType.channel = intprop

#Define the Path of the File the Scene belongs to.
sourcepath = StringProperty(name="Source Path", description="The Path of the File the Scene belongs to.", default="none" )
scnType.source_path = sourcepath


### TrimTools Section
                           
scnType.select_audio = BoolProperty( name="Select Audio", 
                                     description = "Select appropriate audio strips, too? ", 
                                     default=True )  

####### Panels #####

class MovieManagerPanel(bpy.types.Panel):    
    bl_space_type = "SEQUENCE_EDITOR"
    bl_region_type = "UI"
    bl_label = "Movie Manager"

    def draw(self, context):
        scn = bpy.context.scene
        layout = self.layout
        
        
        row = layout.row()
        col = row.column() 
        col.operator( "moviemanager.edit_range" ) 
       
        if (bpy.context.scene.timeline == False):
            row.operator( "moviemanager.switch_back_to_timeline" )
            
            if (bpy.context.scene.source_path != "none"):
                row = layout.row()
                col = row.column() 
                col.operator( "moviemanager.hide" )
                row.prop(scn, "good_clip" )
            
        
        row = layout.row()
        col = row.column() 
        if (bpy.context.scene.timeline == True):
            col.operator( "moviemanager.insert_strip" )  
        
        if (bpy.context.scene.timeline == False):
            col.operator( "moviemanager.insert_strip_masterscene" )

        if (bpy.context.scene.timeline == True):
            row = layout.row()
            col = row.column() 
            col.operator( "moviemanager.proxy")
            
            row = layout.row()
            col = row.column() 
            col.operator( "moviemanager.unmeta" )
            row.operator( "moviemanager.meta" )
            
            
            if (bpy.context.scene.timeline == False):
                row = layout.row()
                row.operator( "moviemanager.set_timeline" )  
            
        row = layout.row() 
        
        if (bpy.context.scene.timeline == True):
            row.prop( scn, "show_options" )   
        
            if (bpy.context.scene.show_options == True):
            
                row = layout.row()
                col = row.column()  
                col.prop( scn, "channel" )        
            
                row = layout.row()
                col = row.column() 
        
                col.prop( scn, "editing_screen" ) 
                col.prop( scn, "editing_range_screen" ) 
            
                row = layout.row()
                col = row.column() 
                row.prop( scn, "custom_screen" )   
                col.prop( scn, "zoom" )  
        
                row = layout.row()
                row.prop( scn, "meta" )   
                
                row = layout.row()
                col = row.column() 
                col.prop( scn, "p100" )  
                row.prop( scn, "p75" )   
                row.prop( scn, "p50" )   
                row.prop( scn, "p25" )   
        else:
            row = layout.row()
            col = row.column()  
            col.operator( "moviemanager.set_timeline" )  

class TrimToolsPanel(bpy.types.Panel):    
    bl_space_type = "SEQUENCE_EDITOR"
    bl_region_type = "UI"
    bl_label = "Trim Tools"

    def draw(self, context):
        scn = bpy.context.scene
        layout = self.layout
        
        row = layout.row()
        col = row.column()
        
        col.operator( "ht.select_current" ) 
        row.prop( scn, "select_audio" )
        
        row = layout.row()
        col = row.column()
        
        col.operator( "ht.cut_current" )  
        row.operator( "ht.snap_end" )
        
        row = layout.row()
        col = row.column()
        col.operator( "ht.trim_left" )
        row.operator( "ht.trim_right" )  
                
##### MovieManager Operators ####

class Set_Timeline (bpy.types.Operator):
    bl_idname = "moviemanager.set_timeline"
    bl_label = "Set as Timeline"
    bl_description = "Set this scene as Timeline"    
    
    def invoke (self, context, event):
        for i in bpy.data.scenes:
            i.timeline = False 
            
        bpy.context.scene.timeline = True
        
        return {'FINISHED'}         
    
class Hide_Operator (bpy.types.Operator):
    bl_idname = "moviemanager.hide"
    bl_label = "Hide"
    bl_description = "Hide clips that are not useful"
    
    def invoke (self, context, event):
        for i in bpy.data.scenes:
            path = i.source_path 
            #print(i.name)
            if (path != "none"):
                split = path.split("/")
                length = len(split)
                dir = ""
                
                for m in range (0, length - 1):
                    dir = dir + split[m] + "/"
                    
                file = split[(length - 1)]
                    
                changed = False
                #print(dir)
                #print(path)
                #print(file)
                if (file[0] == "." and i.good_clip == True):
                    newname = file[1:]
                    changed = True

                if (file[0] != "." and i.good_clip == False):
                    newname = "." + file
                    changed = True
                    
                if (changed == True):
                    os.chdir(dir)
                    os.rename(file, newname)
                    #print(file)
                    #print(newname)
                    #print("once")
                    for j in bpy.data.scenes:
                        
                        if (j.source_path == path):
                            j.source_path = dir + newname
                        
                        try:
                            for k in j.sequence_editor.sequences_all:
                                if (k.filepath == bpy.path.relpath(path)):
                                    k.filepath = bpy.path.relpath(dir + newname)
                                         
                        except:
                            print("hadn't a sequencer. poor little scene!")
                    
                
        return {'FINISHED'}  
        
    
class Proxy_Operator(bpy.types.Operator): 
     
    bl_idname = "moviemanager.proxy"
    bl_label = "Create Proxies"
            
    def invoke(self, context, event ):  
        
        masterscene = 0
        masterscene_is_set = False
        
        for i in bpy.data.scenes:
            if (i.timeline == True):
                masterscene = i
                masterscene_is_set = True
                break
        
        if (masterscene_is_set == False):
            self.report({'ERROR_INVALID_INPUT'},'Please set a Timeline first.')
            return {'CANCELLED'}
            
        if (masterscene.p50 == False and masterscene.p25 == False and masterscene.p75 == False  and masterscene.p100 == False ):
            self.report({'ERROR_INVALID_INPUT'},'No Proxies to create!.')
            return {'CANCELLED'}
        
        #get directory
        for a in context.window.screen.areas:
            if a.type == 'FILE_BROWSER':
                dir = a.spaces[0].params.directory
                break
            
        try:
            dir
            
        except:
            self.report({'ERROR_INVALID_INPUT'}, 'No visible File Browser')
            return {'CANCELLED'}

        #Change the current area to VSE so that we can also call the operator from any other area type.
        bool_IsVSE = True
        if (bpy.context.area.type != 'SEQUENCE_EDITOR'):
            bpy.context.area.type = 'SEQUENCE_EDITOR'
            bool_IsVSE = False
        
        #Check if scene exists, if not -> new 
        scene_exists = False
        scene_name = "qID"
        for i in bpy.data.scenes:
            if i.name == scene_name:
                scene_exists = True
                
        if (scene_exists == True):                                         
            bpy.context.screen.scene = bpy.data.scenes[scene_name]   
            
        else:
            new_scene = bpy.data.scenes.new(scene_name)                    
                                                
        scene = bpy.data.scenes[scene_name]
        bpy.context.screen.scene = scene     
        
        ## Get files in directory
        
        files = [ f for f in listdir(dir) if isfile(join(dir,f)) ]
        
        for k in files:
            path =  dir + k
            strip_type = detect_strip_type(k)

            if (strip_type == 'MOVIE'):                     
                bpy.ops.sequencer.movie_strip_add(filepath=path) 
                    
                for j in bpy.context.scene.sequence_editor.sequences:
                    if (j.type == 'MOVIE'):
                        j.use_proxy = True
                        if (masterscene.p25 == True):
                            j.proxy.build_25 = True
                            
                        if (masterscene.p50 == True):
                            j.proxy.build_50 = True
                            
                        if (masterscene.p75 == True):
                            j.proxy.build_75 = True
                            
                        if (masterscene.p100 == True):
                            j.proxy.build_100 = True
                            
                bpy.ops.sequencer.select_all(action='SELECT')
                bpy.ops.sequencer.rebuild_proxy()
                bpy.ops.sequencer.delete()

            if (bool_IsVSE == False):       
                bpy.context.area.type = 'FILE_BROWSER'

        Switch_back_to_Timeline_Operator.invoke(self, context, event)
       
        return {'FINISHED'} 
 
class Edit_Range_Operator(bpy.types.Operator):  
    
    bl_idname = "moviemanager.edit_range"
    bl_label = "Edit Range"
    bl_description = "Edit the Range of the selected clip in the File Browser. Use the new scene's Start and end Frame"
    
    def invoke (self, context, event):        
        
        masterscene = 0
        masterscene_is_set = False
        
        for i in bpy.data.scenes:
            if (i.timeline == True):
                masterscene = i
                masterscene_is_set = True
                break
        
        if (masterscene_is_set == False):
            self.report({'ERROR_INVALID_INPUT'},'Please set a Timeline first.')
            return {'CANCELLED'}
            
        #get scene
        for a in context.window.screen.areas:
            if a.type == 'FILE_BROWSER':
                params = a.spaces[0].params
                break
           
        try:
            params
            
        except:
            self.report({'ERROR_INVALID_INPUT'}, 'No visible File Browser')
            return {'CANCELLED'}

        if params.filename == '':
            self.report({'ERROR_INVALID_INPUT'}, 'No file selected')
            return {'CANCELLED'}
        
        #Change the current area to VSE so that we can also call the operator from any other area type.
        bool_IsVSE = True
        if (bpy.context.area.type != 'SEQUENCE_EDITOR'):
            bpy.context.area.type = 'SEQUENCE_EDITOR'
            bool_IsVSE = False
        
        path = params.directory + params.filename
        strip_type = detect_strip_type(params.filename)
        scene_exists = False
        scene_name = params.filename + "_Range"

        if (strip_type == 'MOVIE' or 'SOUND'):
            
            for i in bpy.data.scenes:
                if i.source_path == path:
                    scene_exists = True
                    scene_name = i.name  
            
            if (scene_exists == True):                                         
                bpy.context.screen.scene = bpy.data.scenes[scene_name]      
                bpy.context.scene.sync_mode = masterscene.sync_mode              
            
            else:
                new_scene = bpy.data.scenes.new(scene_name)                
                scene_name = new_scene.name                
                bpy.data.scenes[scene_name].source_path = path 
              
                new_scene.render.resolution_x = masterscene.render.resolution_x
                new_scene.render.resolution_y = masterscene.render.resolution_y
                new_scene.render.resolution_percentage = masterscene.render.resolution_percentage
                new_scene.render.fps  = masterscene.render.fps
                new_scene.frame_start = 0   
                            
                scene = bpy.data.scenes[scene_name]
                
                        
                bpy.context.screen.scene = scene     
                
                bpy.context.scene.sync_mode = masterscene.sync_mode
                   
                #bpy.ops.sequencer.movie_strip_add(frame_start=0, filepath=path)
                
                if (strip_type == 'MOVIE'):
                    bpy.ops.sequencer.movie_strip_add(frame_start=0, filepath=path) 
                
                elif (strip_type == 'SOUND'):
                    bpy.ops.sequencer.sound_strip_add(frame_start=0, filepath=path)     
                
                bpy.context.scene.frame_end = bpy.context.scene.sequence_editor.active_strip.frame_final_duration 
                
                
        else:
            self.report({'ERROR_INVALID_INPUT'}, 'Invalid file format')
            return {'CANCELLED'}
	  
        if (masterscene.zoom == True and bool_IsVSE == True):
            bpy.ops.sequencer.view_selected()
            
        if (bool_IsVSE == False):       
            bpy.context.area.type = 'FILE_BROWSER'
            
        #Change to custom layout if wanted.      
        if (masterscene.custom_screen == True):                
            for i in bpy.data.screens:
                bpy.ops.screen.screen_set(delta=1)
                        
                if (bpy.context.screen.name == masterscene.editing_range_screen):
                    break
           
            bpy.context.screen.scene = bpy.data.scenes[scene_name]   
        
        return {'FINISHED'}

class Switch_back_to_Timeline_Operator(bpy.types.Operator): 
     
    bl_idname = "moviemanager.switch_back_to_timeline"
    bl_label = "Get Back"
            
    def invoke(self, context, event ):  
        
        masterscene = 0
        masterscene_is_set = False
        
        for i in bpy.data.scenes:
            if (i.timeline == True):
                masterscene = i
                masterscene_is_set = True
                break
        
        if (masterscene_is_set == False):
            self.report({'ERROR_INVALID_INPUT'},'Please set a Timeline first.')
            return {'CANCELLED'} 
                     
        if (masterscene.custom_screen == True):         
            for i in bpy.data.screens:
                bpy.ops.screen.screen_set(delta=1)
                        
                if (bpy.context.screen.name == masterscene.editing_screen):
                    break
           
            bpy.context.screen.scene = masterscene
                        
        else:
            bpy.context.screen.scene = masterscene   
           
        return {'FINISHED'}    
    
class Insert_Strip_Masterscene(bpy.types.Operator):  
    
    bl_idname = "moviemanager.insert_strip_masterscene"
    bl_label = "Insert into editing scene"
    bl_description = "Insert the selected Strip into the Timeline of the Editing Scene"
    
    def invoke(self, context, event):
        
        masterscene = 0
        masterscene_is_set = False
        
        for i in bpy.data.scenes:
            if (i.timeline == True):
                masterscene = i
                masterscene_is_set = True
                break
        
        if (masterscene_is_set == False):
            self.report({'ERROR_INVALID_INPUT'},'Please set a Timeline first.')
            return {'CANCELLED'}
        
        strip = bpy.context.scene.sequence_editor.active_strip

        if (strip.type == 'MOVIE' or 'SOUND'):
            
            cut_end = False
                
            scene = bpy.context.scene
            bpy.context.screen.scene = masterscene
            
            #Get current frame and channel
            
            if (bpy.context.selected_sequences):  
                current_frame = bpy.context.screen.scene.sequence_editor.active_strip.frame_final_end
                channel = bpy.context.screen.scene.sequence_editor.active_strip.channel
                
            else:
                current_frame = bpy.context.scene.frame_current
                channel = scene.channel
                
            frame_final_end = current_frame + strip.frame_final_duration
            frame_start = current_frame - ( strip.frame_final_start - strip.frame_start )
            
            #If there is a selected strip, limit the length of the new one           
            try:
                for j in bpy.context.selected_sequences:
                    if (j.frame_final_start < frame_final_end and j.frame_final_start > current_frame):
                        frame_final_end = j.frame_final_start
                        
            except:
                print("no selected sequences")
            
            if (strip.type == 'MOVIE'):
                bpy.ops.sequencer.movie_strip_add(frame_start=frame_start, channel=channel, overlap=True, filepath=strip.filepath) 
                
            elif (strip.type == 'SOUND'):
                bpy.ops.sequencer.sound_strip_add(frame_start=frame_start, channel=channel, overlap=True, filepath=strip.filepath)             
            
            
            #Apply in and out points
            if (strip.type == 'MOVIE' and masterscene.meta == True):
                bpy.ops.sequencer.meta_make()
                bpy.context.scene.sequence_editor.active_strip.frame_final_start = current_frame
                bpy.context.scene.sequence_editor.active_strip.frame_final_end = frame_final_end
                bpy.context.scene.sequence_editor.active_strip.channel = channel
                
            else:
                for i in bpy.context.selected_sequences:  
                    channel = i.channel 
                    i.frame_final_start = current_frame
                    i.frame_final_end = frame_final_end
                    i.channel = channel
                #i.frame_start = frame_start - scene.frame_start    
                
                   
            bpy.context.screen.scene = scene
            
            return {'FINISHED'}         
 
    
class Insert_Strip(bpy.types.Operator):  
    
    bl_idname = "moviemanager.insert_strip"
    bl_label = "Insert selected File"
    bl_description = "Insert the selected File into the Timeline"
    
    def invoke(self, context, event):

        masterscene = 0
        masterscene_is_set = False
        
        for i in bpy.data.scenes:
            if (i.timeline == True):
                masterscene = i
                masterscene_is_set = True
                break
        
        if (masterscene_is_set == False):
            self.report({'ERROR_INVALID_INPUT'},'Please set a Timeline first.')
            return {'CANCELLED'}
        
        for a in context.window.screen.areas:
            if a.type == 'FILE_BROWSER':
                params = a.spaces[0].params
                break
           
        try:
            params
            
        except:
            self.report({'ERROR_INVALID_INPUT'}, 'No visible File Browser')
            return {'CANCELLED'}

        if params.filename == '':
            self.report({'ERROR_INVALID_INPUT'}, 'No file selected')
            return {'CANCELLED'}

        path = params.directory + params.filename
        strip_type = detect_strip_type(params.filename)
        scene_exists = False

        if (strip_type == 'MOVIE' or 'SOUND'):
            
            for i in bpy.data.scenes:
                if i.source_path == path:
                    scene_exists = True
                    scene_name = i.name
                    scene = i
                    break       
            
            #Get current frame
            if (bpy.context.selected_sequences):  
                current_frame = bpy.context.screen.scene.sequence_editor.active_strip.frame_final_end
                channel = bpy.context.screen.scene.sequence_editor.active_strip.channel
                
            else:
                current_frame = bpy.context.scene.frame_current
                channel = bpy.context.scene.channel
                     
            if (scene_exists == True):
                
                if (strip_type == 'MOVIE'):
                   bpy.ops.sequencer.movie_strip_add(frame_start=current_frame, channel=channel, filepath=path)
                
                elif (strip_type == 'SOUND'):
                   bpy.ops.sequencer.sound_strip_add(frame_start=current_frame, channel=channel, filepath=path)             

                frame_start = bpy.context.scene.sequence_editor.active_strip.frame_start
                frame_end = bpy.context.scene.sequence_editor.active_strip.frame_final_end
                duration = bpy.context.scene.sequence_editor.active_strip.frame_duration
                end_offset = duration - scene.frame_end
                
                #Apply in and out points
                
                if (strip_type == 'MOVIE' and bpy.context.scene.meta == True):
                    bpy.ops.sequencer.meta_make()
                    bpy.context.scene.sequence_editor.active_strip.frame_start + scene.frame_start
                    bpy.context.scene.sequence_editor.active_strip.frame_final_end = frame_end - end_offset + 1
                    bpy.context.scene.sequence_editor.active_strip.channel = channel
                
                else:
                    for i in bpy.context.selected_sequences:   
                        channel = i.channel
                        i.frame_final_start = frame_start + scene.frame_start
                        i.frame_final_end = frame_end - end_offset + 1
                        i.frame_start = frame_start - scene.frame_start       
                        i.channel = channel
                    
            else:
                if (strip_type == 'MOVIE'):
                   bpy.ops.sequencer.movie_strip_add(frame_start=current_frame, channel=channel, filepath=path)
                
                elif (strip_type == 'SOUND'):
                   bpy.ops.sequencer.sound_strip_add(frame_start=current_frame, channel=channel, filepath=path)      
                
            if (strip_type == 'MOVIE' and masterscene.meta == True):
                bpy.ops.moviemanager.meta()
            return {'FINISHED'}         
        
class Meta(bpy.types.Operator):  
    
    bl_idname = "moviemanager.meta"
    bl_label = "Meta"
    bl_description = "Merge Audio and Video into meta strip"
    
    def invoke(self, context, event):
        
        channel = 100
        for i in bpy.context.selected_sequences:
            if (i.channel < channel):
                channel = i.channel
                
        bpy.ops.sequencer.meta_make()
        frame_final_start = bpy.context.scene.sequence_editor.active_strip.frame_final_start
        frame_final_end = bpy.context.scene.sequence_editor.active_strip.frame_final_end
        
        bpy.ops.sequencer.meta_toggle()
        for i in bpy.context.selected_sequences:
            i.frame_final_start = i.frame_start
            i.frame_final_duration = i.frame_duration
        bpy.ops.sequencer.meta_toggle()
        bpy.context.scene.sequence_editor.active_strip.frame_final_start = frame_final_start
        bpy.context.scene.sequence_editor.active_strip.frame_final_end = frame_final_end
        bpy.context.scene.sequence_editor.active_strip.channel = channel
        return {'FINISHED'} 
 
class Unmeta(bpy.types.Operator):  
    
    bl_idname = "moviemanager.unmeta"
    bl_label = "Unmeta"
    bl_description = "Separate Audio and Video"
    
    def invoke(self, context, event):
        #sequences = []
        #for h in bpy.context.selected_sequences:     
        #    sequences.append(h)
            
        for i in bpy.context.selected_sequences:
            if (i.type == 'META'):
                channel = i.channel
                frame_final_start = i.frame_final_start
                frame_final_end = i.frame_final_end
                bpy.ops.sequencer.select_all(action='DESELECT')
                i.select = True
                bpy.context.scene.sequence_editor.active_strip = i
                bpy.ops.sequencer.meta_separate()
                for j in bpy.context.selected_sequences:
                    j.frame_final_start = frame_final_start
                    j.frame_final_end = frame_final_end
                    if (j.type == 'MOVIE'):
                        j.channel = channel
                    else:
                        j.channel = channel + 1
                        
        return {'FINISHED'} 
 

####### TrimTools Operators ########

class select_current (bpy.types.Operator):
    bl_idname = "ht.select_current"
    bl_label = "Select current Strip"
    bl_description = "Select the Strip on the current frame"    
    
    def invoke (self, context, event):
        channel = 0
        current_frame = bpy.context.scene.frame_current
        alreadyaselection = False
        selectedstripchannel = 0
        somethingselected = False
        
        for i in bpy.context.scene.sequence_editor.sequences:
            if (i.type == 'MOVIE' or i.type == 'SCENE' or i.type == 'MOVIECLIP' or i.type == 'IMAGE' or i.type == 'COLOR' or i.type == 'MULTICAM'):
                if (i.frame_final_start <= current_frame and i.frame_final_end >= current_frame):
                    if (i.select == True):
                        firstselectedstrip = i
                        alreadyaselection = True
                        
        for i in bpy.context.scene.sequence_editor.sequences:
            if (i.type == 'MOVIE' or i.type == 'SCENE' or i.type == 'MOVIECLIP' or i.type == 'IMAGE' or i.type == 'COLOR' or i.type == 'MULTICAM'):
                if (i.frame_final_start <= current_frame and i.frame_final_end >= current_frame):
                    if (i.channel > channel and alreadyaselection == False):
                        desel = bpy.ops.sequencer.select_all(action='DESELECT')
                        bpy.context.scene.sequence_editor.active_strip = i
                        i.select = True
                        channel = i.channel
                        selectedstrip = i
                        somethingselected = True
                    elif (i.channel < firstselectedstrip.channel and i.channel > selectedstripchannel and alreadyaselection == True):
                        desel = bpy.ops.sequencer.select_all(action='DESELECT')
                        bpy.context.scene.sequence_editor.active_strip = i
                        i.select = True
                        channel = i.channel
                        selectedstrip = i
                        selectedstripchannel = i.channel
                        somethingselected = True
        
        if (somethingselected == False and alreadyaselection == True):
            desel = bpy.ops.sequencer.select_all(action='DESELECT')
                            
                        
        for i in bpy.context.scene.sequence_editor.sequences:
            if (i.type == 'SOUND' and somethingselected == True and bpy.context.scene.select_audio == True):
                if (i.frame_final_start == selectedstrip.frame_final_start and i.frame_final_end == selectedstrip.frame_final_end):
                        i.select = True

        return {'FINISHED'}     
      
class cut_current (bpy.types.Operator):
    bl_idname = "ht.cut_current"
    bl_label = "Cut current Strip"
    bl_description = "Cut the Strip on the current frame"    
    
    def invoke (self, context, event):
        channel = 0
        current_frame = bpy.context.scene.frame_current
        alreadyaselection = False
        selectedstripchannel = 0
        somethingselected = False
        
        for i in bpy.context.scene.sequence_editor.sequences:
            if (i.type == 'MOVIE' or i.type == 'SCENE' or i.type == 'MOVIECLIP' or i.type == 'IMAGE' or i.type == 'COLOR' or i.type == 'MULTICAM'):
                if (i.frame_final_start <= current_frame and i.frame_final_end >= current_frame):
                    if (i.select == True):
                        firstselectedstrip = i
                        alreadyaselection = True
                        
        for i in bpy.context.scene.sequence_editor.sequences:
            if (i.type == 'MOVIE' or i.type == 'SCENE' or i.type == 'MOVIECLIP' or i.type == 'IMAGE' or i.type == 'COLOR' or i.type == 'MULTICAM'):
                if (i.frame_final_start <= current_frame and i.frame_final_end >= current_frame):
                    if (i.channel > channel and alreadyaselection == False):
                        bpy.ops.sequencer.select_all(action='DESELECT')
                        bpy.context.scene.sequence_editor.active_strip = i
                        i.select = True
                        channel = i.channel
                        selectedstrip = i
                        somethingselected = True
                    elif (i.channel < firstselectedstrip.channel and i.channel > selectedstripchannel and alreadyaselection == True):
                        desel = bpy.ops.sequencer.select_all(action='DESELECT')
                        bpy.context.scene.sequence_editor.active_strip = i
                        i.select = True
                        channel = i.channel
                        selectedstrip = i
                        selectedstripchannel = i.channel
                        somethingselected = True
        
        if (somethingselected == False and alreadyaselection == True):
            desel = bpy.ops.sequencer.select_all(action='DESELECT')
                            
                        
        for i in bpy.context.scene.sequence_editor.sequences:
            if (i.type == 'SOUND' and somethingselected == True and bpy.context.scene.select_audio == True):
                if (i.frame_final_start == selectedstrip.frame_final_start and i.frame_final_end == selectedstrip.frame_final_end):
                        i.select = True
                        
        cut = bpy.ops.sequencer.cut(frame=current_frame)

        return {'FINISHED'}     
    
class trim_left (bpy.types.Operator):
    bl_idname = "ht.trim_left"
    bl_label = "Trim Left"
    bl_description = "Set the selected clip's starting frame to current frame"    
    
    def invoke (self, context, event):
        for i in bpy.context.selected_sequences:
            i.frame_final_start = bpy.context.scene.frame_current
        return {'FINISHED'}                    
    
class trim_right (bpy.types.Operator):
    bl_idname = "ht.trim_right"
    bl_label = "Trim Right"
    bl_description = "Set the selected clip's ending frame to current frame"    
    
    def invoke (self, context, event):
        for i in bpy.context.selected_sequences:
            i.frame_final_end = bpy.context.scene.frame_current
        return {'FINISHED'}          
    
class snap_end (bpy.types.Operator):
    bl_idname = "ht.snap_end"
    bl_label = "Snap End"
    bl_description = "Snap the Clip to the current frame with it´s end"    
    
    def invoke (self, context, event):
        s = bpy.context.scene.sequence_editor.active_strip
        s.frame_start = bpy.context.scene.frame_current - s.frame_offset_start - s.frame_final_duration
        return {'FINISHED'}  

def register():
    bpy.utils.register_class( Edit_Range_Operator ) 
    bpy.utils.register_class( Proxy_Operator ) 
    bpy.utils.register_class( Set_Timeline )
    bpy.utils.register_class( Insert_Strip_Masterscene )
    bpy.utils.register_class( Switch_back_to_Timeline_Operator )
    bpy.utils.register_class( Insert_Strip )
    bpy.utils.register_class( MovieManagerPanel ) 
    bpy.utils.register_class( Unmeta )
    bpy.utils.register_class( Meta )  
    bpy.utils.register_class( Hide_Operator)
### TrimTools ###
    bpy.utils.register_class( TrimToolsPanel )
    bpy.utils.register_class( select_current ) 
    bpy.utils.register_class( cut_current ) 
    bpy.utils.register_class( trim_left )
    bpy.utils.register_class( trim_right ) 
    bpy.utils.register_class( snap_end ) 

def unregister():
    bpy.utils.unregister_class( Edit_Range_Operator ) 
    bpy.utils.unregister_class( Proxy_Operator ) 
    bpy.utils.unregister_class( Set_Timeline )
    bpy.utils.unregister_class( Switch_back_to_Timeline_Operator)
    bpy.utils.unregister_class( Insert_Strip_Masterscene )
    bpy.utils.unregister_class( Insert_Strip )
    bpy.utils.unregister_class( MovieManagerPanel )
    bpy.utils.unregister_class( Unmeta ) 
    bpy.utils.unregister_class( Meta )
    bpy.utils.unregister_class( Hide_Operator)
### TrimTools ###
    bpy.utils.unregister_class( FilePanel )
    bpy.utils.unregister_class( select_current ) 
    bpy.utils.unregister_class( cut_current )
    bpy.utils.unregister_class( trim_left ) 
    bpy.utils.unregister_class( trim_right )
    bpy.utils.unregister_class( snap_end ) 
if __name__ == "__main__":
    register()
    
    
    
    



