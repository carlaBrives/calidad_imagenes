# mejorador.py
# ─────────────────────────────────────────────────────────────
# Coordina el ciclo iterativo de evaluación y mejora.
# Usa Evaluador para analizar y Editor para corregir.
# REUTILIZADO DE: función mejorar() del Colab
# MODIFICACIONES:
#   - Clase en lugar de función suelta
#   - Devuelve historial completo de iteraciones
#   - Lógica de cada mejora separada en mejoras.py
# ─────────────────────────────────────────────────────────────

from PIL import Image
from editor import Editor
from evaluador import Evaluador
from configuracion import (
    SCORE_MINIMO_ACEPTABLE,
    MAX_ITERACIONES
)

class Mejorador:
    """
    Ejecuta el ciclo iterativo de mejora de calidad de imagen.

    Uso:
        mejorador = Mejorador()
        resultado = mejorador.procesar(imagen_pil)

        resultado["imagen_final"]   → PIL Image procesada
        resultado["score_inicial"]  → float
        resultado["score_final"]    → float
        resultado["iteraciones"]    → lista con detalle de cada paso
        resultado["exitoso"]        → True si alcanzó el score mínimo
    """

    def __init__(self):
        # Instanciamos el evaluador una sola vez y lo reutilizamos en todas las iteraciones. Crearlo dentro del bucle sería un desperdicio de recursos.
        self._evaluador = Evaluador()


    # ══════════════════════════════════════════════════════════
    # PUNTO DE ENTRADA PRINCIPAL
    # ══════════════════════════════════════════════════════════

    def procesar(self, imagen_original: Image.Image) -> dict:
        """
        Ejecuta el ciclo completo de evaluación y mejora.

        Parámetros:
            imagen_original: PIL Image a procesar

        Retorna:
            dict con imagen_final, scores, historial e indicador de éxito
        """
        # Guardamos la original sin tocarla para poder mostrarla al final
        imagen_actual = imagen_original.copy()

        # Evaluación inicial — antes de cualquier modificación
        evaluacion_inicial = self._evaluador.evaluar(imagen_actual)
        score_inicial = evaluacion_inicial["score"]

        # Historial: lista de dicts, uno por iteración
        # Nos permite mostrar la evolución completa al usuario
        historial = [{
            "iteracion":    0,
            "score":        score_inicial,
            "clasificacion":evaluacion_inicial["clasificacion"],
            "problemas":    evaluacion_inicial["problemas"],
            "metricas":     evaluacion_inicial["metricas"],
            "mejoras_aplicadas": [],
            "imagen":       imagen_actual.copy(),
        }]

        #solo corta si el score es bueno Y no hay problemas
        hay_problemas = len(evaluacion_inicial["problemas"]) > 0

        if score_inicial >= SCORE_MINIMO_ACEPTABLE and not hay_problemas:
            return self._armar_resultado(
            imagen_final=imagen_actual,
            score_inicial=score_inicial,
            score_final=score_inicial,
            historial=historial,
            exitoso=True
        )

        # ── BUCLE ITERATIVO ───────────────────────────────────
        imagen_anterior = imagen_actual.copy()
        score_anterior  = score_inicial

        for i in range(1, MAX_ITERACIONES + 1):

            # Determinamos qué mejorar según los problemas actuales
            problemas_actuales = historial[-1]["problemas"]
            metricas_actuales  = historial[-1]["metricas"]

            # Aplicamos las mejoras y registramos cuáles se usaron
            imagen_mejorada, mejoras_aplicadas = self._aplicar_mejoras(
                imagen_actual,
                problemas_actuales,
                metricas_actuales
            )

            # Evaluamos la imagen después de las mejoras
            evaluacion_nueva = self._evaluador.evaluar(imagen_mejorada)
            score_nuevo      = evaluacion_nueva["score"]

            # ── CONTROL DE EMPEORAMIENTO ──────────────────────
            # Si las mejoras empeoraron la imagen, restauramos la versión anterior y terminamos el ciclo.
            if score_nuevo < score_anterior:
                historial.append({
                    "iteracion":         i,
                    "score":             score_anterior,
                    "clasificacion":     historial[-1]["clasificacion"],
                    "problemas":         historial[-1]["problemas"],
                    "metricas":          historial[-1]["metricas"],
                    "mejoras_aplicadas": mejoras_aplicadas,
                    "imagen":            imagen_anterior.copy(),
                    "restaurado":        True,   # flag para que main.py lo muestre
                })
                imagen_actual = imagen_anterior.copy()
                break

            # Registramos esta iteración en el historial
            historial.append({
                "iteracion":         i,
                "score":             score_nuevo,
                "clasificacion":     evaluacion_nueva["clasificacion"],
                "problemas":         evaluacion_nueva["problemas"],
                "metricas":          evaluacion_nueva["metricas"],
                "mejoras_aplicadas": mejoras_aplicadas,
                "imagen":            imagen_mejorada.copy(),
                "restaurado":        False,
            })

            # Actualizamos para la próxima iteración
            imagen_anterior = imagen_actual.copy()
            imagen_actual   = imagen_mejorada.copy()
            score_anterior  = score_nuevo

            # Si alcanzamos la calidad mínima, terminamos antes
            if score_nuevo >= SCORE_MINIMO_ACEPTABLE:
                break

        # ── FIN DEL BUCLE ─────────────────────────────────────
        score_final = historial[-1]["score"]
        exitoso     = score_final >= SCORE_MINIMO_ACEPTABLE

        return self._armar_resultado(
            imagen_final=imagen_actual,
            score_inicial=score_inicial,
            score_final=score_final,
            historial=historial,
            exitoso=exitoso
        )


    # ══════════════════════════════════════════════════════════
    # LÓGICA DE MEJORA
    # ══════════════════════════════════════════════════════════

    def _aplicar_mejoras(self, imagen: Image.Image,
                         problemas: list,
                         metricas: dict) -> tuple:
        """
        Coordina la decisión de qué mejora aplicar según los problemas detectados.
        Cada tipo de mejora tiene su propio método para mantener las responsabilidades separadas.
        """
        editor = Editor(imagen)
        mejoras_aplicadas = []
        texto_problemas = " ".join(problemas).lower()

        mejoras_aplicadas += self._aplicar_mejora_ruido(editor, texto_problemas, metricas)
        mejoras_aplicadas += self._aplicar_mejora_brillo(editor, texto_problemas, metricas)
        mejoras_aplicadas += self._aplicar_mejora_contraste(editor, texto_problemas, metricas)
        mejoras_aplicadas += self._aplicar_mejora_saturacion(editor, texto_problemas, metricas)
        mejoras_aplicadas += self._aplicar_mejora_nitidez(editor, texto_problemas, metricas)

        if not mejoras_aplicadas:
            editor.contraste(1.2)
            editor.brillo(1.05)
            mejoras_aplicadas.append("Mejora genérica conservadora (contraste + brillo leve)")

        return editor.get_image(), mejoras_aplicadas

    def _aplicar_mejora_ruido(self, editor: Editor, texto_problemas: str, metricas: dict) -> list:
        if "ruido" not in texto_problemas:
            return []

        if "ruido alto" in texto_problemas:
            editor.reducir_ruido()
            return ["Reducción de ruido (filtro bilateral)"]

        editor.gaussiano(radio=1.0)
        return ["Suavizado leve (gaussiano radio 1)"]

    def _aplicar_mejora_brillo(self, editor: Editor, texto_problemas: str, metricas: dict) -> list:
        brillo_actual = metricas.get("brillo", 128)

        if "oscura" in texto_problemas or "subexpuesta" in texto_problemas:
            if brillo_actual < 40:
                editor.brillo(1.5)
                return ["Aumento de brillo fuerte (×1.5)"]
            editor.brillo(1.25)
            return ["Aumento de brillo moderado (×1.25)"]

        if "sobreexpuesta" in texto_problemas:
            if brillo_actual > 220:
                editor.brillo(0.65)
                return ["Reducción de brillo fuerte (×0.65)"]
            editor.brillo(0.82)
            return ["Reducción de brillo moderada (×0.82)"]

        return []

    def _aplicar_mejora_contraste(self, editor: Editor, texto_problemas: str, metricas: dict) -> list:
        if "contraste" not in texto_problemas:
            return []

        contraste_actual = metricas.get("contraste", 50)
        if contraste_actual < 15:
            editor.ecualizar_histograma()
            return ["Ecualización de histograma"]

        editor.contraste(1.4)
        return ["Mejora de contraste (×1.4)"]

    def _aplicar_mejora_saturacion(self, editor: Editor, texto_problemas: str, metricas: dict) -> list:
        if "saturación" in texto_problemas or "saturacion" in texto_problemas:
            editor.saturacion(1.3)
            return ["Aumento de saturación (×1.3)"]
        return []

    def _aplicar_mejora_nitidez(self, editor: Editor, texto_problemas: str, metricas: dict) -> list:
        if "desenfocada" not in texto_problemas:
            return []

        if "muy desenfocada" in texto_problemas:
            editor.nitidez()
            editor.nitidez()
            return ["Nitidez doble (imagen muy desenfocada)"]

        editor.nitidez()
        return ["Nitidez simple"]


    # ══════════════════════════════════════════════════════════
    # HELPERS
    # ══════════════════════════════════════════════════════════

    def _armar_resultado(self, imagen_final, score_inicial,
                         score_final, historial, exitoso) -> dict:
        """Construye el dict de resultado final de forma consistente."""
        mejora_porcentual = (score_final - score_inicial) * 100

        return {
            "imagen_final":       imagen_final,
            "score_inicial":      score_inicial,
            "score_final":        score_final,
            "mejora_porcentual":  round(mejora_porcentual, 2),
            "iteraciones":        historial,
            "total_iteraciones":  len(historial) - 1,  # sin contar la inicial
            "exitoso":            exitoso,
        }