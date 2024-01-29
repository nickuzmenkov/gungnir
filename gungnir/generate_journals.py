from pathlib import Path

root_path = Path("C:/", "Users", "frenc", "Desktop", "gungnir", "simulation")
fluent_path = root_path / "fluent"
mesh_path = root_path / "mesh"

export_properties = [
    "pressure",
    "total-pressure",
    "x-velocity",
    "y-velocity",
    "velocity-magnitude",
    "cell-wall-distance",
]

case_path = fluent_path / "main.cas.h5"
journal = [f'/file/read-case "{case_path}" yes']

mesh_paths = list(mesh_path.glob("*.msh"))
calculated_cases = list(fluent_path.glob("*.csv"))
not_calculated_cases = set([x.stem for x in mesh_paths]).difference([x.stem for x in calculated_cases])

mesh_paths = [x for x in mesh_paths if x.stem in not_calculated_cases]

for mesh_path in mesh_paths:
    output_solution_path = Path(fluent_path, mesh_path.stem + ".dat")
    output_data_path = Path(fluent_path, mesh_path.stem + ".csv")

    journal += [
        f'/file/replace-mesh "{mesh_path}" yes',
        "/solve/initialize/hyb-initialization yes",
        "/solve/iterate 500",
        f'/file/write-data/ "{output_solution_path}"',
        f'/file/export ascii "{output_data_path}" () no {" ".join(export_properties)} () no yes',
        "",
    ]

with open("journal.jou", "w") as file:
    file.write("\n".join(x for x in journal))
