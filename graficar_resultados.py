import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np
import os
import re

labels = ["A", "B", "C", "D", "E", "F", "G"]
label_to_index = {l: i for i, l in enumerate(labels)}

def parsear_archivo(ruta):
    pasos = []
    with open(ruta, "r") as f:
        contenido = f.read().strip().split("-----\n")
    for bloque in contenido:
        lineas = bloque.strip().splitlines()
        if not lineas:
            continue
        paso = int(lineas[0].split()[1])
        clusters_linea = lineas[2].strip()
        clusters = []
        for grupo in clusters_linea.split():
            indices = [label_to_index[c] for c in grupo]
            clusters.append(set(indices))
        matriz = []
        i = 4
        while i < len(lineas) and not lineas[i].startswith("Fusionados:"):
            fila = lineas[i].strip().split()
            try:
                fila_convertida = [float(x.replace("∞", "inf")) for x in fila]
                matriz.append(fila_convertida)
            except ValueError:
                break
            i += 1
        fusion = None
        if i < len(lineas) and "Fusionados:" in lineas[i]:
            match = re.search(r"Fusionados: (\w+) y (\w+) con distancia: ([\d.]+)", lineas[i])
            if match:
                name1, name2 = match.group(1), match.group(2)
                dist = float(match.group(3))

                # Buscar índices reales en clusters
                def encontrar_idx(nombre):
                    letras = sorted(nombre)
                    for idx, cluster in enumerate(clusters):
                        if sorted([labels[i] for i in cluster]) == letras:
                            return idx
                    raise ValueError(f"No se encontró el cluster: {nombre}")

                try:
                    idx1 = encontrar_idx(name1)
                    idx2 = encontrar_idx(name2)
                    fusion = (idx1, idx2, dist)
                except ValueError as e:
                    print(f"Error al encontrar fusión: {e}")

        pasos.append({
            "paso": paso,
            "clusters": clusters,
            "matriz": np.array(matriz),
            "fusion": fusion
        })
    return pasos

def dibujar_matriz(ax, M, clusters, fusion=None):
    names = [''.join(sorted([labels[i] for i in sorted(c)])) for c in clusters]
    ax.clear()
    im = ax.imshow(M, cmap='viridis', interpolation='nearest')
    ax.set_xticks(range(len(names)))
    ax.set_xticklabels(names, rotation=45, fontsize=12)
    ax.set_yticks(range(len(names)))
    ax.set_yticklabels(names, fontsize=12)
    for i in range(len(M)):
        for j in range(len(M)):
            if i != j:
                color = "w"
                if fusion:
                    fi, fj, _ = fusion
                    if (fi in clusters[i] and fj in clusters[j]) or (fj in clusters[i] and fi in clusters[j]):
                        color = "red"
                ax.text(j, i, f"{M[i,j]:.2f}", ha='center', va='center', color=color, fontsize=10)
    ax.set_title("Matriz de distancias", fontsize=14)

def dibujar_dendrograma(ax, pasos, hasta_paso):
    ax.clear()
    cmap = cm.get_cmap('tab10')
    ax.set_xlim(-1, len(labels))
    ax.set_ylim(0, max([p["fusion"][2] for p in pasos if p["fusion"]] + [1]) + 0.5)
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, fontsize=12)
    ax.set_ylabel("Distancia")
    ax.set_title("Dendrograma", fontsize=14)

    posiciones = {i: i for i in range(len(labels))}
    alturas = {i: 0 for i in range(len(labels))}
    cluster_id = len(labels)

    clusters_ids = [{i} for i in range(len(labels))]

    for idx in range(1, hasta_paso + 1):
        paso = pasos[idx]
        f = paso["fusion"]
        if not f:
            continue
        i1, i2, dist = f

        # Buscar los índices en `clusters_ids`
        a_idx, b_idx = -1, -1
        for idx_c, cluster in enumerate(clusters_ids):
            if i1 in cluster:
                a_idx = idx_c
            if i2 in cluster:
                b_idx = idx_c

        if a_idx == -1 or b_idx == -1:
            continue

        x1, x2 = posiciones[a_idx], posiciones[b_idx]
        y1, y2 = alturas[a_idx], alturas[b_idx]
        new_x = (x1 + x2) / 2
        new_y = dist

        c = cmap(idx % 10)
        ax.plot([x1, x1], [y1, new_y], '-', color=c, lw=2)
        ax.plot([x2, x2], [y2, new_y], '-', color=c, lw=2)
        ax.plot([x1, x2], [new_y, new_y], '-', color=c, lw=2)
        ax.text(new_x + 0.05, new_y, f"{dist:.2f}", fontsize=10, color=c)

        # Actualizar estructuras
        clusters_ids.append(clusters_ids[a_idx] | clusters_ids[b_idx])
        posiciones[len(clusters_ids)-1] = new_x
        alturas[len(clusters_ids)-1] = new_y

        for idx_r in sorted([a_idx, b_idx], reverse=True):
            del clusters_ids[idx_r]
            posiciones.pop(idx_r)
            alturas.pop(idx_r)

def graficar_pasos(pasos, carpeta):
    os.makedirs(carpeta, exist_ok=True)
    for paso in pasos:
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6), gridspec_kw={'width_ratios': [3, 2]})
        dibujar_dendrograma(ax1, pasos, paso["paso"])
        dibujar_matriz(ax2, paso["matriz"], paso["clusters"], paso.get("fusion"))
        fig.suptitle(f"Paso {paso['paso']}", fontsize=16)
        fig.tight_layout(pad=3.0)
        plt.savefig(f"{carpeta}/paso_{paso['paso']:02d}.jpg", dpi=150)
        plt.close()

# Ejecutar
archivo = "salida_single.txt"
pasos = parsear_archivo(archivo)
graficar_pasos(pasos, "graficos_single")
