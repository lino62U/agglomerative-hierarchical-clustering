import os
import json
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import colormaps

# === Cargar archivo ===
with open("salida_single.json") as f:
    pasos = json.load(f)

# Crear carpeta de salida
os.makedirs("imagenes", exist_ok=True)

# === Datos base ===
labels = [c[0] for c in pasos[0]["clusters"]]
n = len(labels)
label_to_idx = {name: i for i, name in enumerate(labels)}

# === Construir matriz original ===
D = np.full((n, n), np.inf)
for i in range(n):
    for j in range(n):
        if i != j:
            D[i][j] = pasos[0]["matriz"][i][j]

# === Funciones auxiliares ===
def calcular_distancia(D, c1, c2, metodo="single"):
    vals = [D[i][j] for i in c1 for j in c2 if i != j]
    if metodo == "single":
        return min(vals)
    elif metodo == "complete":
        return max(vals)
    else:
        return np.mean(vals)

def generar_matriz(D, clusters, metodo="single"):
    size = len(clusters)
    M = np.zeros((size, size))
    for i in range(size):
        for j in range(size):
            if i != j:
                M[i][j] = calcular_distancia(D, clusters[i], clusters[j], metodo)
    return M

def dibujar_matriz(ax, M, clusters):
    ax.clear()
    im = ax.imshow(M, cmap="viridis", interpolation="nearest")
    nombres = [''.join(sorted(labels[i] for i in cluster)) for cluster in clusters]
    ax.set_xticks(range(len(clusters)))
    ax.set_yticks(range(len(clusters)))
    ax.set_xticklabels(nombres, rotation=45, fontsize=10)
    ax.set_yticklabels(nombres, fontsize=10)
    for i in range(len(M)):
        for j in range(len(M)):
            if i != j:
                ax.text(j, i, f"{M[i, j]:.2f}", ha="center", va="center", color="w", fontsize=8)
    ax.set_title("Matriz de distancias")

# === Estructuras ===
cluster_id = 0
clusters = {i: {i} for i in range(n)}         # id → set de índices
positions = {i: i for i in range(n)}          # posición x
heights = {i: 0 for i in range(n)}            # altura
next_id = n

fusiones = []  # fusiones realizadas (para graficar todo en cada paso)
colors = colormaps.get_cmap("tab10")

# === Procesar cada paso ===
for paso in pasos:
    paso_id = paso["paso"]

    # Aplicar fusión nueva SI EXISTE (ANTES de graficar)
    if "fusion" in paso and paso["fusion"]:
        f = paso["fusion"]
        nombres1 = set(f["clusters"][0])
        nombres2 = set(f["clusters"][1])
        c1 = next(k for k, v in clusters.items() if v is not None and set(labels[i] for i in v) == nombres1)
        c2 = next(k for k, v in clusters.items() if v is not None and set(labels[i] for i in v) == nombres2)

        # Guardar fusión para graficar
        fusiones.append({"c1": c1, "c2": c2, "dist": f["distancia"]})

        # Fusionar
        new_cluster = clusters[c1] | clusters[c2]
        clusters[next_id] = new_cluster
        positions[next_id] = (positions[c1] + positions[c2]) / 2
        heights[next_id] = f["distancia"]
        clusters[c1] = None
        clusters[c2] = None
        next_id += 1

    # Crear figura
    fig, (ax_dendo, ax_mat) = plt.subplots(1, 2, figsize=(12, 6), gridspec_kw={"width_ratios": [3, 2]})
    ax_dendo.set_xlim(-1, n)
    ax_dendo.set_ylim(0, max([float(p["fusion"]["distancia"]) for p in pasos if "fusion" in p and p["fusion"]] + [0]) + 1)
    ax_dendo.set_xticks(range(n))
    ax_dendo.set_xticklabels(labels, fontsize=10)
    ax_dendo.set_ylabel("Distancia")
    ax_dendo.set_title(f"Dendrograma - Paso {paso_id}")

    # Dibujar TODAS las fusiones acumuladas
    for idx, fusion in enumerate(fusiones):
        c1 = fusion["c1"]
        c2 = fusion["c2"]
        dist = fusion["dist"]
        x1, x2 = positions[c1], positions[c2]
        y1, y2 = heights[c1], heights[c2]
        new_x = (x1 + x2) / 2
        col = colors(idx % 10)
        ax_dendo.plot([x1, x1], [y1, dist], '-', color=col, lw=2)
        ax_dendo.plot([x2, x2], [y2, dist], '-', color=col, lw=2)
        ax_dendo.plot([x1, x2], [dist, dist], '-', color=col, lw=2)
        ax_dendo.text(new_x + 0.05, dist, f"{dist:.2f}", fontsize=9, color=col)

    # Dibujar matriz parcial
    clusters_vivos = [v for v in clusters.values() if v is not None]
    M = generar_matriz(D, clusters_vivos, metodo="single")
    dibujar_matriz(ax_mat, M, clusters_vivos)

    # Guardar imagen
    plt.tight_layout()
    plt.savefig(f"imagenes/paso_{paso_id:02d}_parcial.png")
    plt.close()

print("✅ Dendrogramas parciales con todas las fusiones previas generados.")
