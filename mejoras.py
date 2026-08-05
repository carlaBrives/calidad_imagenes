# mejoras.py
# ─────────────────────────────────────────────────────────────
# Funciones individuales de mejora de imagen.
# Extraídas de _aplicar_mejoras() en mejorador.py para separar
# responsabilidades:
#   - mejorador.py → coordina el orden de las mejoras
#   - mejoras.py   → decide cómo corregir cada problema
# ─────────────────────────────────────────────────────────────
from editor import Editor

# ──BRILLO ─────────────────────────────────────────
def mejorar_brillo(editor: Editor, texto_problemas: str,
                   metricas: dict) -> list:
    """Corrige problemas de brillo según la severidad.
    Oscura/subexpuesta → sube el brillo (fuerte si brillo < 40, moderado si no).
    Sobreexpuesta → baja el brillo (fuerte si brillo > 220, moderado si no)."""
    mejoras = []
    brillo_actual = metricas["brillo"]
    if "oscura" in texto_problemas or "subexpuesta" in texto_problemas:
        if brillo_actual < 40:
            # Muy oscura: aumento fuerte
            editor.brillo(1.5)
            mejoras.append("Aumento de brillo fuerte (×1.5)")
        else:
            # Levemente oscura: ajuste moderado para no sobreexponer
            editor.brillo(1.25)
            mejoras.append("Aumento de brillo moderado (×1.25)")

    elif "sobreexpuesta" in texto_problemas:
        if brillo_actual > 220:
            # Muy sobreexpuesta: reducción fuerte
            editor.brillo(0.65)
            mejoras.append("Reducción de brillo fuerte (×0.65)")
        else:
            # Levemente sobreexpuesta: reducción suave
            editor.brillo(0.82)
            mejoras.append("Reducción de brillo moderada (×0.82)")

    # Si no había problema de brillo, retorna lista vacía y no toca la imagen
    return mejoras

# ──Ruido ─────────────────────────────────────────
def mejorar_ruido(editor: Editor, texto_problemas: str,
                  metricas: dict) -> list:
    """
    Corrige problemas de ruido según la severidad detectada.
    Lógica:
        - Ruido alto  → filtro bilateral (preserva bordes)
        - Ruido leve  → gaussiano suave (más rápido, suficiente)
        - Sin ruido   → no toca nada, devuelve lista vacía
    """
    mejoras = []

    if "ruido" in texto_problemas:
        if "ruido alto" in texto_problemas:
            #Ruido severo: Bilatera, suaviza zonas uniformes pero respeta los bordes
            editor.reducir_ruido()
            mejoras.append("Reducción de ruido (filtro bilateral)")
        else:
            # Ruido leve: Gaussiano suave, para ruido leve alcanza con esto
            editor.gaussiano(radio=1.0)
            mejoras.append("Suavizado leve (gaussiano radio 1)")

    return mejoras

# ──Contraste ─────────────────────────────────────────
def mejorar_contraste(editor: Editor, texto_problemas: str,
                      metricas: dict) -> list:
    """
    Corrige el contraste según la severidad.
    Muy bajo (< 15) → ecualización de histograma (redistribuye todo el rango 0-255).
    Bajo → aumento moderado (×1.4).
    """
    mejoras = []

    if "contraste" in texto_problemas:
        contraste_actual = metricas["contraste"]
        if contraste_actual < 15:
            # Contraste muy bajo: ecualización de histograma
            # (redistribuye los píxeles en todo el rango 0-255)
            editor.ecualizar_histograma()
            mejoras.append("Ecualización de histograma")
        else:
            # Bajo: aumento moderado es suficiente
            editor.contraste(1.4)
            mejoras.append("Mejora de contraste (×1.4)")

    return mejoras

# ── SATURACIÓN ─────────────────────────────────────
def mejorar_saturacion(editor: Editor, texto_problemas: str,
                       metricas: dict) -> list:
    """
    Corrige problemas de saturación si los colores están apagados.
    Busca con y sin tilde por si el evaluador genera el texto distinto según el sistema operativo.
    Lógica:
        - Saturación baja → aumentamos la viveza de los colores (×1.3)
        - Sin problema    → no toca nada, lista vacía
    """
    mejoras = []

    if "saturación" in texto_problemas or "saturacion" in texto_problemas:
        editor.saturacion(1.3)
        mejoras.append("Aumento de saturación (×1.3)")

    return mejoras

# ── NITIDEZ ─────────────────────
def mejorar_nitidez(editor: Editor, texto_problemas: str,
                    metricas: dict) -> list:
    """
    Realza los bordes según la severidad. Se aplica siempre al final para no amplificar el ruido que ya fue reducido antes.
    Lógica:
        - Muy desenfocada → doble pasada de nitidez
        - Levemente desenfocada → una sola pasada
        - Sin problema → no toca nada, lista vacía
    """
    mejoras = []

    if "desenfocada" in texto_problemas:
        if "muy desenfocada" in texto_problemas:
            # Doble pasada para casos severos
            editor.nitidez()
            editor.nitidez()
            mejoras.append("Nitidez doble (imagen muy desenfocada)")
        else:
            # Una pasada es suficiente para desenfoque leve
            editor.nitidez()
            mejoras.append("Nitidez simple")

    return mejoras