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


    enum_edit_screen: EnumProperty(items=avail_screens,
                                    name="Editing Workspace")

    enum_range_screen: EnumProperty(items=avail_screens,
                                    name="Range Editing Workspace")



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
