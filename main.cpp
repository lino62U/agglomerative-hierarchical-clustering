#include <iostream>
#include <fstream>
#include <numeric>
#include <vector>
#include <set>
#include <limits>
#include <iomanip>
#include <algorithm>
#include <string>

using namespace std;

using Cluster = set<int>;
using Matriz = vector<vector<double>>;

vector<string> labels = {"A", "B", "C", "D", "E", "F", "G"};

vector<vector<double>> dist_lower = {
    {0},
    {2.15, 0},
    {0.7, 1.53, 0},
    {1.07, 1.14, 0.43, 0},
    {0.85, 1.38, 0.21, 0.29, 0},
    {1.16, 1.01, 0.55, 0.22, 0.41, 0},
    {1.56, 2.83, 1.86, 2.04, 2.02, 2.05, 0}
};

Matriz crearMatriz() {
    int n = labels.size();
    Matriz D(n, vector<double>(n, 0));
    for (int i = 0; i < n; ++i)
        for (int j = 0; j <= i; ++j)
            D[i][j] = D[j][i] = dist_lower[i][j];
    return D;
}

double calcularDistancia(const Cluster& a, const Cluster& b, const Matriz& D, const string& metodo) {
    vector<double> dists;
    for (int i : a)
        for (int j : b)
            if (i != j && i < D.size() && j < D.size())
                dists.push_back(D[i][j]);
    if (dists.empty()) return 0.0;
    if (metodo == "single")
        return *min_element(dists.begin(), dists.end());
    if (metodo == "complete")
        return *max_element(dists.begin(), dists.end());
    if (metodo == "average")
        return accumulate(dists.begin(), dists.end(), 0.0) / dists.size();
    return 0.0; // fallback
}

void guardarPasoJSON(ofstream& out, int paso, const vector<Cluster>& clusters, const Matriz& M,
                     double distancia = -1, string nombre_a = "", string nombre_b = "", bool es_ultimo = false) {
    out << "  {\n";
    out << "    \"paso\": " << paso << ",\n";

    // Clusters
    out << "    \"clusters\": [";
    for (size_t i = 0; i < clusters.size(); ++i) {
        out << "[";
        int count = 0;
        for (int idx : clusters[i]) {
            if (count++) out << ", ";
            out << "\"" << labels[idx] << "\"";
        }
        out << "]";
        if (i + 1 < clusters.size()) out << ", ";
    }
    out << "],\n";

    // Matriz
    out << "    \"matriz\": [\n";
    for (size_t i = 0; i < M.size(); ++i) {
        out << "      [";
        for (size_t j = 0; j < M[i].size(); ++j) {
            if (M[i][j] >= 1e10)
                out << "null";
            else
                out << fixed << setprecision(5) << M[i][j];
            if (j + 1 < M[i].size()) out << ", ";
        }
        out << "]";
        if (i + 1 < M.size()) out << ",";
        out << "\n";
    }
    out << "    ],\n";

    // Fusión
    if (!nombre_a.empty() && !nombre_b.empty()) {
        out << "    \"fusion\": {\n";
        out << "      \"clusters\": [\"" << nombre_a << "\", \"" << nombre_b << "\"],\n";
        out << "      \"distancia\": " << fixed << setprecision(5) << distancia << "\n";
        out << "    }\n";
    } else {
        out << "    \"fusion\": null\n";
    }

    out << "  }";
    if (!es_ultimo) out << ",";
    out << "\n";
}

void clusteringJerarquico(const string& metodo, const string& archivo_salida) {
    ofstream out(archivo_salida);
    out << "[\n";

    const Matriz D_original = crearMatriz(); // Nunca se modifica
    Matriz D_actual = D_original;

    int n = labels.size();
    vector<Cluster> clusters(n);
    for (int i = 0; i < n; ++i)
        clusters[i] = {i};

    int paso = 0;
    guardarPasoJSON(out, paso++, clusters, D_actual);

    while (clusters.size() > 1) {
        int best_i = -1, best_j = -1;
        double best_dist = numeric_limits<double>::max();

        for (int i = 0; i < clusters.size(); ++i)
            for (int j = i + 1; j < clusters.size(); ++j) {
                double d = calcularDistancia(clusters[i], clusters[j], D_original, metodo);
                if (d < best_dist) {
                    best_dist = d;
                    best_i = i;
                    best_j = j;
                }
            }

        Cluster nuevo;
        nuevo.insert(clusters[best_i].begin(), clusters[best_i].end());
        nuevo.insert(clusters[best_j].begin(), clusters[best_j].end());

        string nombre_a, nombre_b;
        for (int i : clusters[best_i]) nombre_a += labels[i];
        for (int i : clusters[best_j]) nombre_b += labels[i];

        vector<Cluster> nuevos_clusters;
        for (int i = 0; i < clusters.size(); ++i)
            if (i != best_i && i != best_j)
                nuevos_clusters.push_back(clusters[i]);
        nuevos_clusters.push_back(nuevo);
        clusters = nuevos_clusters;

        int m = clusters.size();
        Matriz nuevaM(m, vector<double>(m, 0));
        for (int i = 0; i < m; ++i)
            for (int j = 0; j < m; ++j)
                nuevaM[i][j] = (i == j) ? numeric_limits<double>::infinity()
                                       : calcularDistancia(clusters[i], clusters[j], D_original, metodo);

        bool es_ultimo = (clusters.size() == 1);
        guardarPasoJSON(out, paso++, clusters, nuevaM, best_dist, nombre_a, nombre_b, es_ultimo);

        D_actual = nuevaM; // Solo se usa para visualización
    }

    out << "]\n";
    out.close();
}

int main() {
    clusteringJerarquico("single", "salida_single.json");
    clusteringJerarquico("complete", "salida_complete.json");
    clusteringJerarquico("average", "salida_average.json");
    return 0;
}
