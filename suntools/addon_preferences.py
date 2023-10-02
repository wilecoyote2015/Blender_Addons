import bpy
from bpy.types import Operator, AddonPreferences
from bpy.props import StringProperty, IntProperty, BoolProperty

class SuntoolsAddonPreferences(AddonPreferences):
    # this must match the add-on name, use '__package__'
    # when defining this in a submodule of a python package.
    bl_idname = __package__

    command_darktable: StringProperty(
        name="Command: Darktable",
        default='darktable'
    )
    command_darktable_cli: StringProperty(
        name="Command: Darktable CLI",
        default='darktable-cli',
    )
    darktable_disable_opencl_render: BoolProperty(
        name="Darktable Render: Disable Opencl",
        default=False,
    )

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "command_darktable")
        layout.prop(self, "command_darktable_cli")
        layout.prop(self, "darktable_disable_opencl_render")