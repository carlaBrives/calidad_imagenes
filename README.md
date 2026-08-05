# Sistema de evaluación y mejora de calidad de imágenes

Este proyecto analiza y mejora automáticamente la calidad técnica de imágenes. Está diseñado para evaluar brillo, contraste, nitidez, ruido y saturación, y luego aplicar correcciones iterativas hasta alcanzar una calidad mínima aceptable.

## Estructura del proyecto

- `main.py`: punto de entrada que carga la imagen, ejecuta la evaluación y el ciclo de mejora, y guarda los resultados.
- `configuracion.py`: define umbrales, pesos, rutas y parámetros globales de control.
- `utilidades.py`: funciones de lectura/escritura de imágenes, conversión entre PIL y OpenCV, y presentación en consola.
- `editor.py`: clase `Editor` con operaciones de edición de imágenes (brillo, contraste, saturación, filtros, transformaciones y segmentación).
- `evaluador.py`: clase `Evaluador` que calcula métricas de calidad y devuelve un score, clasificación, problemas y métricas numéricas.
- `mejorador.py`: clase `Mejorador` que ejecuta el ciclo iterativo de mejora y decide cuándo detenerse.
- `mejoras.py`: funciones específicas que aplican correcciones según los problemas detectados.
- `img_input/`: carpeta para colocar las imágenes que se desean procesar.
- `img_output/`: carpeta donde se guardan la imagen original y la imagen final mejorada.

## Dependencias

El archivo `requirements.txt` incluye:

- `Flask`
- `Pillow`
- `opencv-python`
- `numpy`

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

Reemplaza la ruta por la carpeta donde hayas guardado el proyecto.

## Interfaz web

También podés usar una página local para cargar imágenes y ver resultados visuales.

### Windows

```powershell
python app.py
```

### macOS / Linux

```bash
python3 app.py
```

1. Ejecutá el servidor web.
2. En la terminal verás un mensaje como:

```text
 * Running on http://127.0.0.1:5000
```

3. Abrí el navegador en la dirección mostrada, por ejemplo:

```text
http://127.0.0.1:5000
```

4. Carga una imagen desde la página y verás:
   - imagen original
   - imagen mejorada
   - score inicial y final
   - problemas detectados
   - mejoras aplicadas

> Esa dirección funciona sólo en la computadora donde se ejecuta `app.py`.

## Uso

Coloca una imagen en `img_input/` y ejecutá el programa con:

### Windows

```powershell
python main.py img_input\i1.png --salida resultado_i1.jpg
```

### macOS / Linux

```bash
python3 main.py img_input/i1.png --salida resultado_i1.jpg
```

El programa:

1. Carga la imagen y guarda una copia original en `img_output/`.
2. Evalúa la calidad inicial de la imagen.
3. Si es necesario, aplica mejoras iterativas sobre la imagen.
4. Guarda la imagen final mejorada en `img_output/resultado_i1.jpg`.
5. Muestra en consola el score inicial, score final, problemas detectados y mejoras aplicadas.

## Ejemplos de imágenes

En el proyecto ya hay archivos de ejemplo en `img_input/`:

- `i1.png`
- `im3.png`

Para probar con otro archivo, cambia la ruta en el comando.

## Mejoras existentes

El sistema puede corregir:

- brillo (bajo o sobreexpuesto)
- contraste bajo
- nitidez baja
- ruido alto
- saturación baja

Las correcciones se aplican en este orden para evitar efectos adversos:

1. reducción de ruido
2. ajuste de brillo
3. ajuste de contraste
4. aumento de saturación
5. nitidez

## Notas

- Si la imagen ya cumple con la calidad mínima y no tiene problemas, se guarda tal cual.
- Si una iteración empeora el score, se restaura la versión anterior.
- El número máximo de iteraciones está definido en `configuracion.py` como `MAX_ITERACIONES = 5`.
