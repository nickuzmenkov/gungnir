import os
import uuid
import random


class GeometryIncorrectError(Exception):
    pass


def draw_spline_figure(points):
    points = List[Point2D]([Point2D.Create(x[0], x[1]) for x in points])
    SketchNurbs.CreateFrom2DPoints(True, points)


def draw_rectangle(point1, point2, point3):
    SketchRectangle.Create(
        Point2D.Create(point1[0], point1[1]),
        Point2D.Create(point2[0], point2[1]),
        Point2D.Create(point3[0], point3[1]),
    )


def select(item):
    return Selection.Create(item)


def create_named_selection(name, items):
    NamedSelection.Create(select(items), Selection.Empty())
    NamedSelection.Rename("Группа1", name)


def delete(items):
    for item in items:
        if item:
            Delete.Execute(select(item))


def purge():
    root = GetRootPart()
    delete(
        [
            root.Bodies,
            root.Components,
            root.DatumPlanes,
            root.DatumLines,
            root.DatumPoints,
            root.Curves,
        ]
    )


def get_mid_point(edge):
    mid_point = edge.EvalMid().Point
    return mid_point.X, mid_point.Y


def close(point1, point2, tolerance=6):
    return round(point1[0], tolerance) == round(point2[0], tolerance) and round(
        point1[1], tolerance
    ) == round(point2[1], tolerance)


def inside(point, x_range, y_range):
    return x_range[0] <= point[0] <= x_range[1] and y_range[0] <= point[1] <= y_range[1]


def select_edge(edges, condition):
    selected = [x for x in edges if condition(x)]

    if not selected:
        raise GeometryIncorrectError(
            "Edge selection failed: no edges found for the given condition."
        )
    if len(selected) > 1:
        raise GeometryIncorrectError(
            "Edge selection failed: multiple edges found for the given condition."
        )

    return selected[0]


def save(path):
    DocumentSave.Execute(path, ExportOptions.Create())


def random_point_inside(x_range, y_range):
    return random.uniform(x_range[0], x_range[1]), random.uniform(
        y_range[0], y_range[1]
    )


def split_tiles(x_range, y_range):
    tile_width = (x_range[1] - x_range[0]) / 3
    tile_height = (y_range[1] - y_range[0]) / 3
    tiles = []

    for i in range(3):
        for j in range(3):
            x_min = x_range[0] + i * tile_width
            x_max = x_min + tile_width
            y_min = y_range[0] + j * tile_height
            y_max = y_min + tile_height
            tiles.append([[x_min, x_max], [y_min, y_max]])

    return [tiles[x] for x in (0, 3, 6, 7, 8, 5, 2, 1)]


def select_random_tiles(tiles, n_min, n_max):
    index = []
    n = random.randint(n_min, n_max)

    while len(index) < n:
        i = random.choice(range(len(tiles)))

        if i not in index:
            index.append(i)

    return [tiles[x] for x in sorted(index)]


"""================= START ================="""


def build(
    domain_left,
    domain_right,
    domain_up,
    domain_down,
    obstacle_left,
    obstacle_right,
    obstacle_up,
    obstacle_down,
    output_path,
):
    purge()

    ViewHelper.SetSketchPlane(Plane.PlaneXY)
    ViewHelper.SetViewMode(InteractionMode.Sketch)

    tiles = split_tiles(
        x_range=[obstacle_left, obstacle_right], y_range=[obstacle_down, obstacle_up]
    )
    tiles = select_random_tiles(tiles=tiles, n_min=3, n_max=8)
    points = [random_point_inside(x[0], x[1]) for x in tiles]

    draw_spline_figure(points=points)
    draw_rectangle(
        point1=(domain_left, domain_down),
        point2=(domain_left, domain_up),
        point3=(domain_right, domain_up),
    )

    ViewHelper.SetViewMode(InteractionMode.Solid)

    fluid = GetRootPart().Bodies[0]
    create_named_selection("fluid_body", fluid)

    fluid_face = fluid.Faces[0]
    create_named_selection("fluid", fluid_face)

    edges = fluid_face.Edges

    if len(edges) != 5:
        raise GeometryIncorrectError(
            "There must be exactly 5 edges: inlet, outlet, symmetry-up, symmetry-down and wall."
        )

    domain_x_center = (domain_left + domain_right) / 2
    domain_y_center = (domain_up + domain_down) / 2

    inlet = select_edge(
        edges=edges,
        condition=lambda x: close(get_mid_point(x), (domain_left, domain_y_center)),
    )
    outlet = select_edge(
        edges=edges,
        condition=lambda x: close(get_mid_point(x), (domain_right, domain_y_center)),
    )
    symmetry_up = select_edge(
        edges=edges,
        condition=lambda x: close(get_mid_point(x), (domain_x_center, domain_up)),
    )
    symmetry_down = select_edge(
        edges=edges,
        condition=lambda x: close(get_mid_point(x), (domain_x_center, domain_down)),
    )
    wall = select_edge(
        edges=edges,
        condition=lambda x: inside(
            get_mid_point(x),
            x_range=(obstacle_left, obstacle_right),
            y_range=(obstacle_down, obstacle_up),
        ),
    )

    create_named_selection("inlet", inlet)
    create_named_selection("outlet", outlet)
    create_named_selection("symmetry_up", symmetry_up)
    create_named_selection("symmetry_down", symmetry_down)
    create_named_selection("wall", wall)

    save(os.path.join(output_path, "{}.scdoc".format(str(uuid.uuid4())[:8])))


shapes = 2000

domain_left = -0.1
domain_right = 0.1
domain_up = 0.1
domain_down = -0.1

obstacle_left = -0.01
obstacle_right = 0.01
obstacle_up = 0.01
obstacle_down = -0.01

output_path = "C:/Users/frenc/Desktop/gungnir/simulation/geometry"

# Workaround for bug in SpaceClaim Scripting:
# Prevent script being infinitely executed top to bottom
if len(os.listdir(output_path)) >= shapes:
    raise Exception("Done")

i = 0

while i < shapes:
    try:
        build(
            domain_left=domain_left,
            domain_right=domain_right,
            domain_up=domain_up,
            domain_down=domain_down,
            obstacle_left=obstacle_left,
            obstacle_right=obstacle_right,
            obstacle_up=obstacle_up,
            obstacle_down=obstacle_down,
            output_path=output_path,
        )
        i += 1
    except GeometryIncorrectError:
        print("Generated geometry is incorrect, rebuilding...")
