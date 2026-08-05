# Sistema de evaluación y mejora de calidad de imágenes

Este proyecto analiza y mejora automáticamente la calidad técnica de imágenes. Está diseñado para evaluar brillo, contraste, nitidez, ruido y saturación, y luego aplicar correcciones iterativas hasta alcanzar un nivel aceptable de calidad visual.

## Descripción

La aplicación permite:

- evaluar la calidad inicial de una imagen
- detectar problemas visuales comunes
- aplicar mejoras automáticas en orden controlado
- guardar la imagen original y la imagen mejorada
- visualizar el resultado mediante una interfaz web

## Características principales

- análisis de imagen con OpenCV y Pillow
- cálculo de métricas de calidad por componente
- mejora iterativa basada en score y criterios definidos
- soporte para imágenes PNG, JPG, JPEG, BMP, GIF y WEBP
- interfaz web para cargar imágenes y ver resultados

## Estructura del proyecto

- `app.py`: aplicación Flask para la interfaz web
- `main.py`: punto de entrada para uso desde consola
- `configuracion.py`: parámetros y umbrales del sistema
- `utilidades.py`: utilidades de lectura, guardado y procesamiento
- `editor.py`: operaciones de edición de imágenes
- `evaluador.py`: evaluación de calidad de la imagen
- `mejorador.py`: lógica del ciclo de mejora iterativa
- `mejoras.py`: funciones para corregir problemas específicos
- `templates/index.html`: interfaz web
- `img_input/`: imágenes de prueba de entrada
- `img_output/`: resultados generados por el sistema
- `tests/test_mejorador.py`: pruebas unitarias básicas
- `requirements.txt`: dependencias del proyecto

## Requisitos

El proyecto usa estas dependencias:

- Flask
- Pillow
- opencv-python
- numpy

## Instalación

### Windows

```powershell
cd "ruta\a\tu\proyecto"
python -m pip install -r requirements.txt
```

### macOS / Linux

```bash
cd /ruta/del/proyecto
python3 -m pip install -r requirements.txt
```

## Ejecutar la aplicación web

### Windows

```powershell
python app.py
```

### macOS / Linux

```bash
python3 app.py
```

Luego abre tu navegador en:

```text
http://127.0.0.1:5000
```

La interfaz permite:

1. seleccionar una imagen
2. ver la versión original
3. ver la versión mejorada
4. observar el score inicial y final
5. revisar problemas detectados y mejoras aplicadas

## Uso desde consola

Coloca una imagen en `img_input/` y ejecuta:

### Windows

```powershell
python main.py img_input\i1.png --salida resultado_i1.jpg
```

### macOS / Linux

```bash
python3 main.py img_input/i1.png --salida resultado_i1.jpg
```

El programa:

1. carga la imagen
2. guarda una copia original en `img_output/`
3. evalúa la calidad inicial
4. aplica mejoras iterativas si es necesario
5. guarda la imagen final mejorada
6. muestra el score inicial, final y mejoras realizadas

## Mejoras que aplica el sistema

El sistema puede corregir:

- brillo bajo o excesivo
- contraste bajo
- nitidez insuficiente
- ruido elevado
- saturación baja

El orden de corrección está diseñado para evitar efectos adversos:

1. reducción de ruido
2. ajuste de brillo
3. ajuste de contraste
4. aumento de saturación
5. nitidez

## Ejemplos de imágenes

El proyecto incluye ejemplos en `img_input/` como:

- `i1.png`
- `im3.png`
- `image.png`
- `img_ruido.png`

## Notas

- Si la imagen ya cumple con la calidad mínima, el sistema la guarda sin cambios.
- Si una iteración empeora el score, se restaura la versión anterior.
- El máximo de iteraciones está definido en `configuracion.py` como `MAX_ITERACIONES = 5`.

## Estado del proyecto

Este repositorio está orientado a demostrar un flujo de análisis y mejora automática de imágenes aplicando criterios visuales y métricas de calidad.
