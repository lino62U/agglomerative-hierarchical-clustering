import numpy as np
import matplotlib.pyplot as plt
from scipy.cluster.hierarchy import linkage
from scipy.spatial.distance import squareform
import matplotlib.cm as cm
import os

# --- Datos base ---
labels = ['A', 'B', 'C', 'D', 'E', 'F', 'G']
dist_lower = [
    [0],
    [2.15, 0],
    [0.7, 1.53, 0],
    [1.07, 1.14, 0.43, 0],
    [0.85, 1.38, 0.21, 0.29, 0],
    [1.16, 1.01, 0.55, 0.22, 0.41, 0],
    [1.56, 2.83, 1.86, 2.04, 2.02, 2.05, 0]
]

# Convertir a matriz completa
n = len(labels)
D = np.zeros((n, n))
for i in range(n):
    for j in range(i + 1):
        D[i][j] = dist_lower[i][j]
        D[j][i] = dist_lower[i][j]
dist_vector = squareform(D)

methods = ['single', 'complete', 'average']

# --- Funciones ---
def calcular_distancia(c1, c2, metodo):
    vals = [D[i][j] for i in c1 for j in c2 if i != j]
    if metodo == 'single':
        return min(vals)
    elif metodo == 'complete':
        return max(vals)
    else:
        return np.mean(vals)

def generar_matriz(clusters, metodo):
    size = len(clusters)
    M = np.zeros((size, size))
    for i in range(size):
        for j in range(size):
            if i != j:
                M[i][j] = calcular_distancia(clusters[i], clusters[j], metodo)
    return M

def dibujar_matriz(ax, M, clusters):
    ax.clear()
    im = ax.imshow(M, cmap='viridis', interpolation='nearest')
    names = [''.join([labels[i] for i in sorted(cluster)]) for cluster in clusters]
    font_size = 10 + (8 - len(clusters)) * 1.5
    font_size = min(font_size, 18)
    ax.set_xticks(range(len(clusters)))
    ax.set_yticks(range(len(clusters)))
    ax.set_xticklabels(names, rotation=45, fontsize=font_size)
    ax.set_yticklabels(names, fontsize=font_size)
    for i in range(len(M)):
        for j in range(len(M)):
            if i != j:
                ax.text(j, i, f"{M[i, j]:.2f}", ha="center", va="center",
                        color="w", fontsize=font_size - 2)
    ax.set_title("Matriz de distancias", fontsize=font_size + 2)

# --- Ejecutar animación paso a paso y guardar ---
def ejecutar_animacion(method):
    Z = linkage(dist_vector, method=method)
    carpeta = f"imagenes_{method}"
    os.makedirs(carpeta, exist_ok=True)

    fig, (ax_dendo, ax_mat) = plt.subplots(1, 2, figsize=(16, 8), gridspec_kw={'width_ratios': [3, 2]})
    colors = cm.get_cmap('tab10', len(Z))

    for frame in range(len(Z) + 1):
        ax_dendo.clear()
        ax_mat.clear()

        ax_dendo.set_xlim(-1, n)
        ax_dendo.set_ylim(0, max(Z[:, 2]) + 1)
        ax_dendo.set_xticks(range(n))
        ax_dendo.set_xticklabels(labels, fontsize=12)
        ax_dendo.set_ylabel("Distancia")
        ax_dendo.set_title(f"Dendrograma - Paso {frame} ({method})")

        clusters = [{i} for i in range(n)]
        positions = {i: i for i in range(n)}
        heights = {i: 0 for i in range(n)}
        next_id = n

        for step in range(frame):
            a, b, dist, _ = Z[step]
            a, b = int(a), int(b)
            new_cluster = clusters[a] | clusters[b]
            clusters.append(new_cluster)
            clusters[a] = None
            clusters[b] = None

            x1, x2 = positions[a], positions[b]
            y1, y2 = heights[a], heights[b]
            new_x = (x1 + x2) / 2
            new_y = dist

            positions[next_id] = new_x
            heights[next_id] = new_y

            c = colors(step % 10)
            ax_dendo.plot([x1, x1], [y1, new_y], '-', color=c, lw=2)
            ax_dendo.plot([x2, x2], [y2, new_y], '-', color=c, lw=2)
            ax_dendo.plot([x1, x2], [new_y, new_y], '-', color=c, lw=2)
            ax_dendo.text(new_x + 0.05, new_y, f"{dist:.2f}", fontsize=8, color=c)

            next_id += 1

        cl_actuales = [c for c in clusters if c is not None]
        M = generar_matriz(cl_actuales, method)
        dibujar_matriz(ax_mat, M, cl_actuales)

        plt.tight_layout(pad=3)
        plt.savefig(f"{carpeta}/paso_{frame:02d}.jpg", dpi=150)

    plt.close()

# --- Ejecutar ---
for method in methods:
    ejecutar_animacion(method)
