import os
import json
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import colormaps
from scipy.cluster.hierarchy import linkage, dendrogram
from scipy.spatial.distance import squareform
import argparse


def load_json_steps(file_path):
    with open(file_path) as f:
        return json.load(f)


def create_output_directory(base_path):
    os.makedirs(base_path, exist_ok=True)


def build_initial_distance_matrix(steps):
    labels = [c[0] for c in steps[0]["clusters"]]
    n = len(labels)
    matrix = np.full((n, n), np.inf)
    for i in range(n):
        for j in range(n):
            if i != j:
                matrix[i][j] = steps[0]["matriz"][i][j]
    return labels, matrix


def draw_final_dendrogram(distance_matrix, labels, method, output_path):
    np.fill_diagonal(distance_matrix, 0)
    condensed = squareform(distance_matrix)
    Z = linkage(condensed, method=method)

    fig, ax = plt.subplots(figsize=(10, 6))
    ddata = dendrogram(Z, labels=labels, ax=ax)
    ax.set_title(f"Final Dendrogram ({method})")
    ax.set_ylabel("Distance")

    for i, d in zip(ddata['icoord'], ddata['dcoord']):
        x = 0.5 * (i[1] + i[2])
        y = d[1]
        ax.text(x + 1, y + 0.01, f"{y:.2f}", va='bottom', ha='center', fontsize=9)

    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()
    print(f"✅ Final dendrogram saved to {output_path}")


def compute_cluster_distance(D, c1, c2, method):
    values = [D[i][j] for i in c1 for j in c2 if i != j]
    if method == "single":
        return min(values)
    elif method == "complete":
        return max(values)
    else:
        return np.mean(values)


def generate_distance_matrix(D, clusters, method):
    size = len(clusters)
    M = np.zeros((size, size))
    for i in range(size):
        for j in range(size):
            if i != j:
                M[i][j] = compute_cluster_distance(D, clusters[i], clusters[j], method)
    return M


def draw_distance_matrix(ax, matrix, clusters, labels):
    ax.clear()
    ax.imshow(matrix, cmap="viridis", interpolation="nearest")
    names = [''.join(sorted(labels[i] for i in cluster)) for cluster in clusters]
    ax.set_xticks(range(len(clusters)))
    ax.set_yticks(range(len(clusters)))
    ax.set_xticklabels(names, rotation=45, fontsize=10)
    ax.set_yticklabels(names, fontsize=10)
    for i in range(len(matrix)):
        for j in range(len(matrix)):
            if i != j:
                ax.text(j, i, f"{matrix[i, j]:.2f}", ha="center", va="center", color="w", fontsize=8)
    ax.set_title("Distance Matrix")


def process_json(file_path, method, final_only=False):
    steps = load_json_steps(file_path)
    base_name = os.path.splitext(os.path.basename(file_path))[0]
    output_folder = os.path.join("img", base_name)
    create_output_directory(output_folder)

    labels, original_matrix = build_initial_distance_matrix(steps)
    n = len(labels)

    if final_only:
        output_path = os.path.join(output_folder, f"dendrogram_final_{method}.png")
        draw_final_dendrogram(original_matrix, labels, method, output_path)
        return

    clusters = {i: {i} for i in range(n)}
    positions = {i: i for i in range(n)}
    heights = {i: 0 for i in range(n)}
    next_id = n
    merges = []
    colors = colormaps.get_cmap("tab10")

    for step in steps:
        step_id = step["paso"]

        if "fusion" in step and step["fusion"]:
            fusion = step["fusion"]
            names1 = set(fusion["clusters"][0])
            names2 = set(fusion["clusters"][1])

            c1 = next(k for k, v in clusters.items() if v and set(labels[i] for i in v) == names1)
            c2 = next(k for k, v in clusters.items() if v and set(labels[i] for i in v) == names2)

            merges.append({"c1": c1, "c2": c2, "dist": fusion["distancia"]})

            new_cluster = clusters[c1] | clusters[c2]
            clusters[next_id] = new_cluster
            positions[next_id] = (positions[c1] + positions[c2]) / 2
            heights[next_id] = fusion["distancia"]
            clusters[c1] = None
            clusters[c2] = None
            next_id += 1

        fig, (ax_dendo, ax_matrix) = plt.subplots(1, 2, figsize=(12, 6), gridspec_kw={"width_ratios": [3, 2]})
        ax_dendo.set_xlim(-1, n)
        ax_dendo.set_ylim(0, max([float(p["fusion"]["distancia"]) for p in steps if "fusion" in p and p["fusion"]] + [0]) + 1)
        ax_dendo.set_xticks(range(n))
        ax_dendo.set_xticklabels(labels, fontsize=10)
        ax_dendo.set_ylabel("Distance")
        ax_dendo.set_title(f"Dendrogram - Step {step_id} ({method})")

        for idx, merge in enumerate(merges):
            c1, c2, dist = merge["c1"], merge["c2"], merge["dist"]
            x1, x2 = positions[c1], positions[c2]
            y1, y2 = heights[c1], heights[c2]
            new_x = (x1 + x2) / 2
            col = colors(idx % 10)
            ax_dendo.plot([x1, x1], [y1, dist], '-', color=col, lw=2)
            ax_dendo.plot([x2, x2], [y2, dist], '-', color=col, lw=2)
            ax_dendo.plot([x1, x2], [dist, dist], '-', color=col, lw=2)
            ax_dendo.text(new_x + 0.05, dist + 0.02, f"{dist:.2f}", fontsize=9, color=col)

        alive_clusters = [v for v in clusters.values() if v]
        M = generate_distance_matrix(original_matrix, alive_clusters, method)
        draw_distance_matrix(ax_matrix, M, alive_clusters, labels)

        plt.tight_layout()
        filename = os.path.join(output_folder, f"step_{step_id:02d}_partial.png")
        plt.savefig(filename)
        plt.close()

    print(f" Step-by-step dendrograms saved to {output_folder}/")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Visualización de dendrogramas desde archivo JSON")
    parser.add_argument("archivo_json", help="Ruta al archivo JSON generado por el programa C++")
    parser.add_argument("metodo", choices=["single", "complete", "average"], help="Método de enlace: single | complete | average")
    parser.add_argument("--pasos", action="store_true", help="Mostrar paso a paso. Por defecto, solo muestra el dendrograma final")
    args = parser.parse_args()

    process_json(args.archivo_json, args.metodo, final_only=not args.pasos)
