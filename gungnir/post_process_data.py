import warnings
from typing import Tuple
from pathlib import Path

import meshio
import pandas as pd
import matplotlib.pyplot as plt
from scipy.spatial import cKDTree
from tqdm.auto import tqdm

warnings.filterwarnings("ignore", message="Zone specification not supported yet .*")

root_path = Path("C:/", "Users", "frenc", "Desktop", "gungnir", "simulation")
mesh_path = root_path / "mesh"
fluent_path = root_path / "fluent"
dataset_path = root_path / "dataset"

edge_index_path = dataset_path / "edge_index"
node_features_path = dataset_path / "node_features"

for path in (edge_index_path, node_features_path):
    path.mkdir(parents=True, exist_ok=True)


def get_edge_index_and_node_features(stem: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
    mesh = meshio.read(Path(mesh_path, stem + ".msh"))
    edge_index = pd.DataFrame(
        data=mesh.cells_dict["line"], columns=["node-1", "node-2"]
    )

    node_features = pd.read_csv(
        Path(fluent_path, stem + ".csv"), delim_whitespace=True, index_col="nodenumber"
    )
    node_features.columns = [x.strip() for x in node_features.columns]

    tree = cKDTree(node_features[["x-coordinate", "y-coordinate"]].values)
    indices = tree.query(mesh.points)[1]

    node_features = node_features.iloc[indices].reset_index(drop=True)
    node_features.index.name = "nodenumber"

    return edge_index, node_features


def plot_mesh(
    node_features: pd.DataFrame, edge_index: pd.DataFrame, output_path: Path
) -> None:
    figure, axes = plt.subplots(nrows=1, ncols=1, figsize=(10, 10), dpi=300)

    for i in range(len(edge_index)):
        edge = edge_index.iloc[i]
        axes.plot(
            [
                node_features.loc[edge["node-1"], "x-coordinate"],
                node_features.loc[edge["node-2"], "x-coordinate"],
            ],
            [
                node_features.loc[edge["node-1"], "y-coordinate"],
                node_features.loc[edge["node-2"], "y-coordinate"],
            ],
            linewidth=0.5,
            color="black",
        )

    axes.scatter(
        node_features["x-coordinate"],
        node_features["y-coordinate"],
        c=node_features["velocity-magnitude"],
        cmap="plasma",
    )

    axes.axis("off")
    figure.savefig(output_path, bbox_inches="tight")
    plt.close(figure)


if __name__ == "__main__":
    stems = [x.stem for x in fluent_path.glob("*.csv")]

    for stem in tqdm(stems, total=len(stems)):
        edge_index, node_features = get_edge_index_and_node_features(stem=stem)

        edge_index.to_csv(Path(edge_index_path, stem + ".csv"), index=False)
        node_features.to_csv(Path(node_features_path, stem + ".csv"))
