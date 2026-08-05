# ─────────────────────────────────────────────────────────────
# REUTILIZADO DE: código Colab (ImagenBase, Tono, Filtros,
# Transformaciones, Segmentacion, Editor)
# MODIFICACIONES:
#   - __init__ acepta PIL Image además de rutas
#   - Se agregan reducir_ruido() y aumentar_saturacion()
#   - Se integra con utilidades.py para conversiones
# ─────────────────────────────────────────────────────────────

import cv2
import numpy as np
from pathlib import Path
from PIL import Image, ImageEnhance, ImageFilter, ImageOps
from utilidades import pil_a_cv, cv_a_pil


# ══════════════════════════════════════════════════════════════
# CLASE BASE
# ══════════════════════════════════════════════════════════════

class ImagenBase:
    """
    Clase base que encapsula una imagen PIL.
    Todas las clases de edición heredan de esta.
    El atributo _image usa guión bajo para indicar uso interno. Obliga a usar get_image()
    para acceder, lo que evita modificaciones accidentales desde afuera de la clase.
    """
    def __init__(self, fuente):#
        """
        Inicializa el editor con una imagen.

        Parámetros:
            fuente: puede ser:
                - str o Path: ruta a un archivo de imagen en disco
                - PIL Image: imagen ya cargada en memoria

        Por qué aceptar PIL Image directamente:
            El mejorador trabaja con imágenes en memoria.
            Evitamos el ciclo inútil de guardar → leer → procesar.
        """
        if isinstance(fuente, (str, Path)):
            # Cargamos desde disco y forzamos RGB
            # RGB porque PIL internamente puede abrir RGBA, L (gris), etc.
            # Normalizar a RGB simplifica todas las operaciones siguientes.
            self._image = Image.open(str(fuente)).convert("RGB")

        elif isinstance(fuente, Image.Image):
            # Hacemos una copia para no modificar la imagen original
            # que nos pasaron desde afuera
            self._image = fuente.copy().convert("RGB")

        else:
            raise TypeError(
                f"fuente debe ser ruta (str/Path) o PIL Image, "
                f"no {type(fuente).__name__}"
            )

    def get_image(self) -> Image.Image:
        #Devuelve la imagen actual.
        return self._image

    def save(self, ruta_destino: str):
        """
        Guarda la imagen actual en disco.

        Parámetros:
            ruta_destino: ruta completa donde guardar (incluye nombre y extensión)

        Retorna:
            self para permitir encadenamiento: editor.brillo(1.2).save("out.jpg")
        """
        self._image.save(str(ruta_destino))
        return self


# ══════════════════════════════════════════════════════════════
# OPERACIONES DE TONO
# ══════════════════════════════════════════════════════════════

class Tono(ImagenBase):
    """
    Operaciones que modifican los valores de intensidad y color:
    brillo, contraste, saturación, escala de grises, ecualización.
    """

    def brillo(self, factor: float = 1.0):
        """Ajusta el brillo de la imagen.factor < 1.0 → más oscura  (ej: 0.7), factor = 1.0 → sin cambio,
        factor > 1.0 → más clara(ej: 1.3)Retorna self"""
        self._image = ImageEnhance.Brightness(self._image).enhance(factor)
        return self
        

    def contraste(self, factor: float = 1.0):
        """Factor → < 1.0 menos contraste (imagen más plana), > 1.0 más contraste(diferencias más marcadas)."""
        self._image = ImageEnhance.Contrast(self._image).enhance(factor)
        return self
        

    def saturacion(self, factor: float = 1.0):
        """Ajusta la saturación (viveza de los colores).
        Factor → 0.0 quita el color(escala de grises total), 1.0 sin cambio, > 1.0 lo intensifica(colores más intensos)."""
        self._image = ImageEnhance.Color(self._image).enhance(factor)
        return self
       

    def escala_grises(self):
        self._image = self._image.convert("L")
        return self

    def ecualizar_histograma(self):
        """Redistribuye los píxeles para ocupar todo el rango 0-255.
        Solo se recomienda cuando el contraste es muy bajo porque puede sobreexponer si la imagen ya tiene buen contraste."""
        self._image = ImageOps.equalize(self._image)
        return self


# ══════════════════════════════════════════════════════════════
# FILTROS
# ══════════════════════════════════════════════════════════════

class Filtros(ImagenBase):
    """Filtros espaciales que modifican la imagen basándose en la relación entre píxeles vecinos."""
    

    def desenfoque(self):
        """Aplica un desenfoque simple (promedia píxeles vecinos).Más agresivo que el gaussiano."""
        self._image = self._image.filter(ImageFilter.BLUR)
        return self
        

    def gaussiano(self, radio: float = 2.0):
        """Aplica desenfoque gaussiano (más suave y natural).
        radio: cuántos píxeles de radio abarca el desenfoque.Radio mayor = más desenfoque."""
        self._image = self._image.filter(ImageFilter.GaussianBlur(radio))
        return self
           
    def nitidez(self):
        """Aplica un filtro de nitidez (realza los bordes)"""
        self._image = self._image.filter(ImageFilter.SHARPEN)
        return self
        
    def bordes(self):
        """Detecta y resalta los bordes de la imagen.El resultado es una imagen que muestra solo los contornos."""
        self._image = self._image.filter(ImageFilter.FIND_EDGES)
        return self      

    def relieve(self):   
        """Útil para visualizar texturas."""     
        self._image = self._image.filter(ImageFilter.EMBOSS)
        return self
        

    def reducir_ruido(self):
        """Filtro bilateral: reduce ruido preservando bordes. A diferencia del gaussiano, no desenfoca zonas con bordes definidos."""
        # Convertimos PIL → OpenCV para usar cv2.bilateralFilter
        img_cv = pil_a_cv(self._image)

        # Parámetros: d=9 (diámetro del vecindario),
        # sigmaColor=75 (rango de color), sigmaSpace=75 (rango espacial)
        # Valores más altos = más suavizado
        filtrada = cv2.bilateralFilter(img_cv, 9, 75, 75)

        # Volvemos a PIL
        self._image = cv_a_pil(filtrada)
        return self
        

# ══════════════════════════════════════════════════════════════
# TRANSFORMACIONES GEOMÉTRICAS
# ══════════════════════════════════════════════════════════════

class Transformaciones(ImagenBase):
    """
    Operaciones que cambian la geometría de la imagen:
    rotación, escala, recorte, volteo.
    """

    def rotar(self, grados: int):
        """
        Rota la imagen en sentido antihorario.
        grados=90 → rota 90° a la izquierda.
        """
        self._image = self._image.rotate(grados)
        return self

    def redimensionar(self, size: tuple):
        """
        Cambia el tamaño de la imagen.

        Parámetros:
            size: tupla (ancho, alto) en píxeles. Ej: (800, 600)

        Nota: PIL no preserva proporción automáticamente.
        Si necesitás mantener el aspect ratio, calculá las
        dimensiones antes de llamar esta función.
        """
        self._image = self._image.resize(size)
        return self

    def recortar(self, box: tuple):
        """
        Recorta un área rectangular de la imagen.

        Parámetros:
            box: tupla (izquierda, arriba, derecha, abajo) en píxeles
            Ej: (100, 50, 400, 300) recorta desde (100,50) hasta (400,300)
        """
        self._image = self._image.crop(box)
        return self

    def flip_horizontal(self):
        """Espeja la imagen horizontalmente (izquierda ↔ derecha)."""
        self._image = self._image.transpose(Image.FLIP_LEFT_RIGHT)
        return self

    def flip_vertical(self):
        """Espeja la imagen verticalmente (arriba ↔ abajo)."""
        self._image = self._image.transpose(Image.FLIP_TOP_BOTTOM)
        return self


# ══════════════════════════════════════════════════════════════
# SEGMENTACIÓN
# ══════════════════════════════════════════════════════════════

class Segmentacion(ImagenBase):
    """
    Operaciones de segmentación: separar regiones de la imagen
    según criterios de intensidad o bordes.
    """

    def umbral(self, valor: int = 128):
        """
        Binariza la imagen: cada píxel queda en blanco o negro
        según si supera el valor umbral.

        valor=128: punto medio del rango 0-255.
        Útil para separar objetos del fondo en imágenes con
        buen contraste entre ambos.
        """
        # Primero convertimos a grises porque el umbral trabaja
        # con un solo canal de intensidad
        gray = self._image.convert("L")
        # lambda aplica la condición píxel por píxel
        self._image = gray.point(lambda p: 255 if p > valor else 0)
        return self

    def contornos(self):
        """
        Detecta y dibuja los contornos de los objetos en la imagen.

        Por qué OpenCV para esto y no PIL:
            cv2.Canny y cv2.findContours no tienen equivalente
            en PIL. Son algoritmos específicos de visión por computadora.

        Proceso:
            1. Convertir a grises
            2. Canny: detecta bordes (gradientes fuertes)
            3. findContours: encuentra las curvas cerradas
            4. drawContours: las dibuja sobre la imagen
        """
        img_np = np.array(self._image)

        # Manejamos el caso en que la imagen ya esté en grises
        # (si se llamó escala_grises() antes que contornos())
        if self._image.mode != 'L':
            img_cv = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
        else:
            img_cv = img_np

        # Canny detecta bordes: umbral bajo=50, umbral alto=150
        edges = cv2.Canny(img_cv, 50, 150)

        # Encontramos los contornos externos (RETR_EXTERNAL)
        # CHAIN_APPROX_SIMPLE comprime segmentos rectos para ahorrar memoria
        contours, _ = cv2.findContours(
            edges,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )

        # Creamos imagen en color para dibujar los contornos en verde
        img_contour = cv2.cvtColor(img_cv, cv2.COLOR_GRAY2BGR)
        # -1 significa "todos los contornos", (0,255,0) es verde, 2 es grosor
        cv2.drawContours(img_contour, contours, -1, (0, 255, 0), 2)

        # Convertimos de vuelta a PIL usando nuestra utilidad
        self._image = cv_a_pil(img_contour)
        return self


# ══════════════════════════════════════════════════════════════
# EDITOR — CLASE PRINCIPAL
# ══════════════════════════════════════════════════════════════

class Editor(Tono, Filtros, Transformaciones, Segmentacion):
    """Clase principal que hereda de Tono, Filtros, Transformaciones y Segmentacion mediante herencia múltiple.
    Esto significa que un objeto Editor puede encadenar operaciones: editor.brillo(1.2).nitidez().ecualizar_histograma()
    El encadenamiento de métodos (method chaining) funciona porque cada método retorna 'self'."""
    pass
