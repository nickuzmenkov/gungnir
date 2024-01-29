import os

SetScriptVersion(Version="22.2.192")
system = GetSystem(Name="SYS")

geometry = system.GetContainer(ComponentName="Geometry")
mesh = system.GetContainer(ComponentName="Mesh")
mesh.Edit()

root_path = "C:/Users/frenc/Desktop/gungnir/simulation"
geometry_path =root_path + "/geometry"
mesh_path = root_path + "/mesh"

for geometry_name in os.listdir(geometry_path):
    geometry.SetFile(FilePath=geometry_path + "/" + geometry_name)
    geometry_stem = geometry_name.split(".")[0]
    output_path = mesh_path + "/" + geometry_stem + ".msh"
    system.Update()
    mesh.SendCommand(
        """var DS = WB.AppletList.Applet("DSApplet").App; SC = DS.Script; SC.doFileExport("{}");""".format(
            output_path
        )
    )
