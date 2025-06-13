#!/bin/bash

# === Verificación de argumentos ===
if [ $# -lt 1 ]; then
    echo "[ERROR] Uso: ./run.sh archivo_entrada.txt [--pasos]"
    exit 1
fi

ENTRADA=$1
MOSTRAR_PASOS="no"

# Bandera opcional --pasos
if [ "$2" == "--pasos" ]; then
    MOSTRAR_PASOS="si"
fi

# === Verificar existencia del archivo de entrada ===
if [ ! -f "$ENTRADA" ]; then
    echo "[ERROR] El archivo '$ENTRADA' no existe."
    exit 1
fi

# === Paso 0: Crear y activar entorno virtual ===
echo "[0/5] [INFO] Verificando entorno virtual..."
if [ ! -d "venv" ]; then
    echo "[INFO] Creando entorno virtual en ./venv ..."
    python3 -m venv venv
fi

echo "[INFO] Activando entorno virtual..."
source venv/bin/activate

# === Instalar dependencias de Python desde requirements.txt ===
if [ ! -f "requirements.txt" ]; then
    echo -e "numpy\nmatplotlib\nscipy" > requirements.txt
    echo "[INFO] Archivo 'requirements.txt' generado automáticamente."
fi

echo "[INFO] Instalando dependencias de Python..."
pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt

# === Paso 1: Limpieza de carpetas ===
echo "[1/5] [INFO] Limpiando subcarpetas dentro de 'img/'..."
mkdir -p img
find img -mindepth 1 -maxdepth 1 -type d -exec rm -rf {} +

# === Paso 2: Compilación del código C++ ===
echo "[2/5] [INFO] Compilando código C++..."
g++ -std=c++17 -o main main.cpp
if [ $? -ne 0 ]; then
    echo "[ERROR] Falló la compilación del código C++."
    deactivate
    exit 1
fi

# === Paso 3: Ejecución del programa C++ ===
echo "[3/5] [INFO] Ejecutando programa C++..."
./main "$ENTRADA"

# === Paso 4: Procesamiento de resultados ===
BASENAME=$(basename "$ENTRADA" .txt)
METODOS=("single" "complete" "average")
TOTAL=${#METODOS[@]}
PROCESADOS=0

echo "[4/5] [INFO] Procesando resultados para métodos: ${METODOS[*]}"

for i in "${!METODOS[@]}"; do
    METODO="${METODOS[$i]}"
    JSON="salida_${BASENAME}_${METODO}.json"
    INDICE=$((i + 1))

    printf "  - [%d/%d] Método %-9s ... " "$INDICE" "$TOTAL" "'$METODO'"

    if [ ! -f "$JSON" ]; then
        echo "[WARN] Archivo no encontrado: $JSON"
        continue
    fi

    if [ "$MOSTRAR_PASOS" == "si" ]; then
        python3 graficar_resultados.py "$JSON" "$METODO" --pasos > /dev/null
    else
        python3 graficar_resultados.py "$JSON" "$METODO" > /dev/null
    fi

    echo "✔️  OK"
    ((PROCESADOS++))
done

# === Paso 5: Finalización ===
echo "[5/5] [INFO] Proceso finalizado. Métodos procesados: $PROCESADOS de $TOTAL."
echo "[INFO] Puedes desactivar el entorno virtual con: deactivate"
