import bpy

bl_info = {
    "name": "Auto Bone Parenting",
    "blender": (3, 0, 0),
    "category": "Object",
    "author": "Felipe Ceotto",
    "version": (0, 1),
    "location": "View3D > Object > Parent > Auto Bone Parenting",
    "description": "Parents the selected objects closest to each bone for a selected armature",
    "tracker_url": "https://github.com/ceottaki/auto-bone-parenting-blender-add-on"
}


class ObjectAutoBoneParenting(bpy.types.Operator):
    """Parents the objects closest to each bone for a selected armature"""      # Use this as a tooltip for menu items and buttons.
    bl_idname = "object.auto_bone_parenting"        # Unique identifier for buttons and menu items to reference.
    bl_label = "Auto Bone Parenting"         # Display name in the interface.
    bl_options = {'REGISTER', 'UNDO'}  # Enable undo for the operator.

    # execute() is called when running the operator.
    def execute(self, context):
        # The original script
        if len(context.selected_objects) <= 0:
            self.report(
                {'WARNING'}, "Please select at least one armature and the meshes you want to parent")
            return {'CANCELLED'}

        if len(list(filter(lambda a: a.type == "ARMATURE", context.selected_objects))) <= 0:
            self.report(
                {'WARNING'}, "Please select at least one armature and the meshes you want to parent")
            return {'CANCELLED'}

        if len(list(filter(lambda a: a.type == "MESH", context.selected_objects))) <= 0:
            self.report(
                {'WARNING'}, "Please select at least one armature and the meshes you want to parent")
            return {'CANCELLED'}

        for armature in context.selected_objects:
            if armature.type != "ARMATURE":
                continue

            # Get a list of all the bones in the selected armature
            bones = armature.pose.bones

            # Iterate over each bone
            for bone in bones:
                # Get the location of the bone
                bone_loc = (bone.head + bone.tail) / 2

                # Initialize the minimum distance to a large value
                min_dist = float("inf")

                # Initialize a variable to keep track of the closest object
                closest_object = None

                # Iterate over all the selected objects in the scene
                for obj in context.selected_objects:
                    # Skip objects that are not mesh objects
                    if obj.type != "MESH":
                        continue

                    # Calculate the distance between the bone and the object
                    dist = (obj.location - bone_loc).length

                    # Update the minimum distance and closest object if necessary
                    if dist < min_dist:
                        min_dist = dist
                        closest_object = obj

                if closest_object != None and (closest_object.location - bone_loc).length < 0.05:
                    # Parent the closest object to the bone
                    self.report({'INFO'}, "Parenting " +
                                closest_object.name + " to " + bone.name)
                    context.view_layer.objects.active = armature
                    # Enter pose mode if not already there
                    if context.object.mode != 'POSE':
                        bpy.ops.object.posemode_toggle()

                    # Selects the bone in question in pose mode and goes back to object mode
                    bpy.data.armatures[armature.name].bones.active = bpy.data.armatures[armature.name].bones[bone.name]
                    bpy.data.armatures[armature.name].bones[bone.name].select = True
                    bpy.ops.object.posemode_toggle()

                    # Selects the detected closest object to the bone and set the bone as its parent
                    closest_object.select_set(True)
                    closest_object.parent = armature
                    closest_object.parent_bone = bone.name
                    bpy.ops.object.parent_set(type='BONE')

                    # Unselects the object
                    closest_object.select_set(False)

        # Lets Blender know the operator finished successfully.
        return {'FINISHED'}


def menu_func(self, context):
    self.layout.operator(ObjectAutoBoneParenting.bl_idname)


def register():
    bpy.utils.register_class(ObjectAutoBoneParenting)
    # Adds the new operator to an existing menu.
    bpy.types.VIEW3D_MT_object_parent.append(menu_func)


def unregister():
    bpy.utils.unregister_class(ObjectAutoBoneParenting)


# This allows you to run the script directly from Blender's Text editor
# to test the add-on without having to install it.
if __name__ == "__main__":
    register()
