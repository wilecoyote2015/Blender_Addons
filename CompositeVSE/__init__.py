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

from handlers_high_bit_depth import render_init 
from operator_composition import OperatorCreateCompositionFromStrip
from operators_navigation import (
    Switch_back_to_Timeline_Operator,
    Switch_to_Composite_Nodepanel_Operator,
    Switch_to_Composite_Operator
)
from ui_panels import CompPanel, NodePanel
from eswc_info import ESWC_Info

bl_info = {
    "name": "Edit Strip With Compositor",
    "description": "Send one or more Sequencer strips to the Compositor, gently",
    "author": "Carlos Padial, TMW, Björn Sonnenschein",
    "version": (0, 15),
    "blender": (2, 80),
    "location": "Sequencer > UI panel, Node Editor > UI panel",
    "wiki_url": "None Yet"
                "None Yet",
    "tracker_url": "None"
                   "func=detail&aid=<number>",
    "category": "Sequencer"
}


bpy.app.handlers.render_init.append(render_init)

classes = (
    ESWC_Info,
    CompPanel,
    NodePanel,
    Switch_to_Composite_Operator,
    Switch_to_Composite_Nodepanel_Operator,
    Switch_back_to_Timeline_Operator,
    OperatorCreateCompositionFromStrip
)

register, unregister = bpy.utils.register_classes_factory(classes)

if __name__ == "__main__":
    register()
