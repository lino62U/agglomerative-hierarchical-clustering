import numpy as np
import matplotlib.pyplot as plt
import os

def generar_colores(n):
    base = plt.get_cmap('tab20')
    colores = [base(i % 20) for i in range(n)]
    return colores

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
    return D, labels, n

def distancia(c1, c2, D, metodo):
    vals = [D[i][j] for i in c1 for j in c2 if i != j]
    if not vals:
        return 0
    if metodo == 'single':
        return min(vals)
    elif metodo == 'complete':
        return max(vals)
    elif metodo == 'average':
        return sum(vals) / len(vals)
    else:
        raise ValueError(f"Método desconocido: {metodo}")

def matriz_distancias(clusters, D, metodo):
    size = len(clusters)
    M = np.full((size, size), np.inf)
    for i in range(size):
        for j in range(i):
            M[i][j] = distancia(clusters[i][1], clusters[j][1], D, metodo)
            M[j][i] = M[i][j]
    return M

def guardar_paso_txt(f, paso, metodo, M, clusters, merge_info, labels_base):
    f.write(f"\n[Método: {metodo.upper()}] Paso {paso+1}\n")
    nombres = [''.join([labels_base[i] for i in sorted(c[1])]) for c in clusters]
    f.write("Clusters actuales:\n")
    f.write("\t".join(nombres) + "\n")
    f.write("Matriz de distancias:\n")
    for fila in M:
        f.write("\t".join(f"{d:.2f}" if np.isfinite(d) else "∞" for d in fila))
        f.write("\n")
    id_a, id_b, new_id, dist, _ = merge_info
    nombre_a = labels_base[id_a] if id_a < len(labels_base) else f"C{str(id_a)}"
    nombre_b = labels_base[id_b] if id_b < len(labels_base) else f"C{str(id_b)}"
    f.write(f"Se unieron: {nombre_a} + {nombre_b} con distancia: {dist:.2f}\n")

def dibujar_dendrograma_final(merge_log, labels_base, method, n):
    posiciones = {}
    alturas = {}
    colores = generar_colores(n + len(merge_log))
    fig, ax = plt.subplots(figsize=(10, 6))

    for i in range(n):
        posiciones[i] = i
        alturas[i] = 0

    for p, (id_a, id_b, new_id, dist, color) in enumerate(merge_log):
        x1, x2 = posiciones[id_a], posiciones[id_b]
        y1, y2 = alturas[id_a], alturas[id_b]
        new_x = (x1 + x2) / 2

        ax.plot([x1, x1], [y1, dist], '-', color=color)
        ax.plot([x2, x2], [y2, dist], '-', color=color)
        ax.plot([x1, x2], [dist, dist], '-', color=color)
        ax.text(new_x + 0.1, dist, f"{dist:.2f}", fontsize=9, color=color)

        posiciones[new_id] = new_x
        alturas[new_id] = dist

    ax.set_xticks(range(n))
    ax.set_xticklabels(labels_base)
    ax.set_ylabel("Distancia")
    ax.set_title(f"Dendrograma final ({method})")
    plt.tight_layout()
    plt.show()

def clustering(D, method, labels_base, n, output_path):
    clusters = [(i, [i]) for i in range(n)]
    next_id = n
    merge_log = []
    colores = generar_colores(n + n - 1)
    cluster_colores = {i: colores[i] for i in range(n)}

    with open(output_path, 'a') as file_out:
        file_out.write(f"\n=== MÉTODO: {method.upper()} ===\n")

        for paso in range(n - 1):
            M = matriz_distancias(clusters, D, method)
            i, j = np.unravel_index(np.argmin(M + np.eye(len(M)) * 1e9), M.shape)
            id_a, cont_a = clusters[i]
            id_b, cont_b = clusters[j]
            dist = M[i, j]
            new_id = next_id
            new_cluster = cont_a + cont_b
            new_color = cluster_colores[id_a]

            merge_log.append((id_a, id_b, new_id, dist, new_color))

            # Fusionar clusters
            indices = sorted([i, j], reverse=True)
            for idx in indices:
                clusters.pop(idx)
            clusters.append((new_id, new_cluster))

            cluster_colores[new_id] = new_color
            next_id += 1

            guardar_paso_txt(file_out, paso, method, M, clusters, merge_log[-1], labels_base)

        dibujar_dendrograma_final(merge_log, labels_base, method, n)

if __name__ == "__main__":
    output_path = "resultados_clustering.txt"
    if os.path.exists(output_path):
        os.remove(output_path)

    D, labels, n = leer_matriz_y_labels("distancia.txt")
    for metodo in ['single', 'complete', 'average']:
        clustering(D, metodo, labels, n, output_path)
