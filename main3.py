import numpy as np
import matplotlib.pyplot as plt
from scipy.cluster.hierarchy import linkage
from scipy.spatial.distance import squareform
from matplotlib.animation import FuncAnimation
import matplotlib.cm as cm

# --- Leer matriz y etiquetas desde archivo ---
def leer_matriz_y_labels(path):
    dist_lower = []
    with open(path, 'r') as f:
        for idx, linea in enumerate(f):
            partes = linea.strip().split()
            fila = list(map(float, partes[1:]))
            while len(fila) < idx + 1:
                fila.append(0.0)
            dist_lower.append(fila)

    n = len(dist_lower)
    D = np.zeros((n, n))
    for i in range(n):
        for j in range(i + 1):
            D[i][j] = dist_lower[i][j]
            D[j][i] = dist_lower[i][j]

    labels = [chr(ord('A') + i) for i in range(n)]
    return D, labels

# --- Función de distancia entre clusters ---
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

# --- Dibujar matriz de distancias ---
def dibujar_matriz(ax, M, clusters, labels):
    ax.clear()
    im = ax.imshow(M, cmap='viridis', interpolation='nearest')
    names = [''.join([labels[i] for i in sorted(cluster)]) for cluster in clusters]
    font_size = 12 + (8 - len(clusters)) * 2
    font_size = min(font_size, 30)
    ax.set_xticks(range(len(clusters)))
    ax.set_yticks(range(len(clusters)))
    ax.set_xticklabels(names, rotation=45, fontsize=font_size)
    ax.set_yticklabels(names, fontsize=font_size)
    for i in range(len(M)):
        for j in range(len(M)):
            if i != j:
                ax.text(j, i, f"{M[i, j]:.2f}", ha="center", va="center",
                        color="w", fontsize=font_size - 4)
    ax.set_title("Matriz de distancias actual", fontsize=font_size + 2)

# --- Animación por método ---
def ejecutar_animacion(method):
    Z = linkage(dist_vector, method=method)
    fig, (ax_dendo, ax_mat) = plt.subplots(2, 1, figsize=(10, 10), gridspec_kw={'height_ratios': [2, 3]})
    cmap = cm.get_cmap('tab20', len(Z)*2)
    lines, texts = [], []

    def update(frame):
        for l in lines:
            l.remove()
        lines.clear()
        for t in texts:
            t.remove()
        texts.clear()

        ax_dendo.clear()
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
            while a >= len(clusters) or clusters[a] is None:
                a -= 1
            while b >= len(clusters) or clusters[b] is None:
                b -= 1

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

            c = cmap(step)
            lines.extend([
                ax_dendo.plot([x1, x1], [y1, new_y], '-', color=c, lw=2)[0],
                ax_dendo.plot([x2, x2], [y2, new_y], '-', color=c, lw=2)[0],
                ax_dendo.plot([x1, x2], [new_y, new_y], '-', color=c, lw=2)[0]
            ])
            texts.append(ax_dendo.text(new_x + 0.05, new_y, f"{dist:.2f}", fontsize=8, color=c))

            next_id += 1

        cl_actuales = [c for c in clusters if c is not None]
        M = generar_matriz(cl_actuales, method)
        dibujar_matriz(ax_mat, M, cl_actuales, labels)

    ani = FuncAnimation(fig, update, frames=len(Z) + 1, interval=500, repeat=False)
    plt.tight_layout(pad=3)
    plt.show()

# --- Main ---
if __name__ == "__main__":
    D, labels = leer_matriz_y_labels("distancia.txt")
    n = len(labels)
    dist_vector = squareform(D)
    methods = ['single', 'complete', 'average']
    for method in methods:
        ejecutar_animacion(method)
