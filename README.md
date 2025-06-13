
# Agrupamiento Jerárquico Aglomerativo

Este proyecto implementa un algoritmo de **clustering jerárquico aglomerativo** en C++, con visualización de resultados paso a paso usando Python.

## 🔧 Requisitos

- `g++` (compatible con C++17)
- Python 3

No necesitas instalar manualmente bibliotecas de Python, ya que el script `run.sh` se encarga de crear un entorno virtual (`venv`) y de instalar las dependencias necesarias (`numpy`, `matplotlib`, `scipy`).

## 🚀 Ejecución del script

Para compilar, ejecutar y graficar los resultados, usa el script:

```bash
./run.sh archivo_entrada.txt [--pasos]
````

### 📌 Parámetros

* `archivo_entrada.txt`: archivo de entrada con la matriz de distancias.
* `--pasos` *(opcional)*: muestra las gráficas paso a paso del clustering.

### 🧠 Ejemplo de uso

```bash
./run.sh datos_ejemplo.txt --pasos
```

Este comando:

1. Verifica o crea un entorno virtual (`venv`).
2. Instala las dependencias necesarias desde `requirements.txt`.
3. Limpia las subcarpetas de `img/`.
4. Compila el código C++ (`main.cpp`).
5. Ejecuta el programa con el archivo de entrada.
6. Procesa los resultados para cada método (`single`, `complete`, `average`) y genera gráficas.
7. (Opcional) Si se usa `--pasos`, también se visualizan las etapas del clustering.

## 📁 Salida

* Las gráficas y visualizaciones se guardan en la carpeta `img/`, organizadas por método y paso.

## 📝 Notas

* Si el archivo de entrada no existe, el script se detiene con un mensaje de error.
* Si no se encuentra un archivo `.json` generado por el programa en C++, se muestra una advertencia y se omite ese método.
* Puedes desactivar el entorno virtual al finalizar con:

```bash
deactivate
```

