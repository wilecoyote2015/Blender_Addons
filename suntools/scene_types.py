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

# todo: use collection


from bpy.props import (IntProperty,
                       FloatProperty,
                       BoolProperty,
                       StringProperty,
                    EnumProperty
                       )
import bpy
from .common_functions import toggle_composition_visibility


class ESWC_Info(bpy.types.PropertyGroup):
    bool_show_options: BoolProperty(
        name="Show options",
        description="Show options",
        default=False)

    bool_add_scale: BoolProperty(
        name="Add Scale node",
        description="Add Scale node",
        default=False)

    # todo: implement update function
    bool_show_compositions: BoolProperty(
        name="Show composite strips",
        description="If activated, the composite are shown in the timeline. Otherwise, the source videos are visible.",
        default=True,
        update=toggle_composition_visibility)

    bool_reuse_compositions: BoolProperty(
        name="Reuse compositions",
        description="When creating compositions for strips, reuse existing compositions that use the same source",
        default=True)

    bool_add_viewer: BoolProperty(
        name="Add Viewer",
        description="You can add a viewer node to the new compositions \
        automatically",
        default=True)

    bool_use_high_bit_depth_fix: BoolProperty(
        name="Render Use High Bitdepth Fix",
        description="Workaround for 10 Bit videos in compositor while rendering. Support for 10 bit videos is still"
                    " missing in Blender, which makes working with all kind of modern log-footage infeasible. This "
                    "option enables a hacky fix to utilize the additional information of 10 bit footage "
                    "during rendering of compositions.",
        default=True)

    bool_add_group: BoolProperty(
        name="Add Nodegroup",
        description="You can add a custom node group to the new compositions \
        automatically",
        default=False)

    # the input path of the movie file the composition was created from
    # if it is empty, the operators infer that the current scene
    # is not a composition.
    path_input: StringProperty(
        name="Movie strip input",
        default="",
        description="the input path of the movie file the composition was \
            created from")

    # store original strip type so that a strip can be created from the composition
    type_original_strip: StringProperty(
        name="Original strip type",
        default="",
        description="Type of the strip associated with this composition")

    selections = [("All", "All", "Copy all settings"),
                  # ( "Select", "Select", "Copy selected settings" ),
                  ("None", "None", "Copy none of the settings")]
    settings: EnumProperty(
        name="Settings Type",
        items=selections,
        default="All",
        description="Choose which settings to copy from the source clip to the created composition")

    master_scene: StringProperty(
        name="Master Scene",
        description="This is the name of the Scene's Master Scene",
        default="Scene")

    scene_init_comp: BoolProperty(name="",
                                   description="",
                                   default=False)

    def avail_nodegroups(self, context):
        items = []
        for i, node_group in enumerate(bpy.data.node_groups):
            items.append((str(i), node_group.name, node_group.name))
        return items

    enum_node_groups: EnumProperty(items=avail_nodegroups,
                                    name="Node Group")

    edit_screen: StringProperty(
        name='Editing Workspace',
        default=''
    )
    comp_screen: StringProperty(
        name='Compositing Workspace',
        default=''
    )

class SunToolsInfo(bpy.types.PropertyGroup):
    ### IOP Section
    # custom_screen = BoolProperty( name="Custom Workspace",
    #                                      description = "Use a custom workspace layout for range editing ",
    #                                      default=False )

    meta: BoolProperty( name="Metastrip",
                                         description = "Combine audio and video into metastrip on insertion into Masterscene",
                                         default=False )
    #
    # zoom = BoolProperty( name="Zoom",
    #                                      description = "Zoom to the entire Clip after entering Edit Range",
    #                                      default=False )

    show_options: BoolProperty( name="Show Options",
                                         description = "",
                                         default=False )

    p25: BoolProperty( name="25%",
                                         description = "Proxy sizes to be created",
                                         default=False )

    p50: BoolProperty( name="50%",
                                         description = "Proxy sizes to be created",
                                         default=False )

    p75: BoolProperty( name="75%",
                                         description = "Proxy sizes to be created",
                                         default=False )

    p100: BoolProperty( name="100%",
                                         description = "Proxy sizes to be created",
                                         default=False )
    p25_edit_range: BoolProperty( name="25%",
                                         description = "Proxy sizes to activate for edit range and inserted strips",
                                         default=False )

    p50_edit_range: BoolProperty( name="50%",
                                         description = "Proxy sizes to activate for edit range and inserted strips",
                                         default=False )

    p75_edit_range: BoolProperty( name="75%",
                                         description = "Proxy sizes to activate for edit range and inserted strips",
                                         default=False )

    p100_edit_range: BoolProperty( name="100%",
                                         description = "Proxy sizes to activate for edit range and inserted strips",
                                         default=False )
    proxy_recursive: BoolProperty(name="Proxy: include subfoders",
                                         description = 'Generate proxies also for files in subfolders',
                                         default=False )

    #Is it the timeline scene?
    timeline: BoolProperty(name="Timeline",
                                         description = "Is this your actual timeline?",
                                         default=False)
    #
    # #Declare usefulness
    # good_clip = BoolProperty( name="Good",
    #                                      description = "Is this an useful Clip? ",
    #                                      default=False )

    def avail_screens(self, context):
        items = []
        for i, elem in enumerate(bpy.data.workspaces):
            items.append((elem.name, elem.name, elem.name))
        return items


    # enum_edit_screen: EnumProperty(items=avail_screens,
    #                                 name="Editing Workspace")
    #
    # enum_range_screen: EnumProperty(items=avail_screens,
    #                                 name="Range Editing Workspace")

    edit_screen: StringProperty(
        name='Editing Workspace',
        default=''
    )
    range_screen: StringProperty(
        name='Range Editing Workspace',
        default=''
    )



    #Channel selector
    channel: IntProperty(
        name="Channel",
        description="Define into which channel the new strip will be inserted ",
        default=1,
        min=1,
        max=30,
        step=1
    )

    #Define the Path of the File the Scene belongs to.
    source_path: StringProperty(name="Source Path", description="The Path of the File the Scene belongs to.", default="none" )

    # define strip type of a range scene so that only ranges of relevant strips are obtained
    type_strip_range: StringProperty(name="Range Strip Type", description="Type of a range scene's strip.", default="none" )

    ### TrimTools Section
    select_audio: BoolProperty( name="Select Audio",
                                         description = "Select appropriate audio strips, too? ",
                                         default=True )
    render_darktable: BoolProperty(
        name='Render with Darktable',
        description='Whether to render Strips edited with darktable with darktable. darktable-cli and ffmpeg must be in your PATH.',
        default=False
    )