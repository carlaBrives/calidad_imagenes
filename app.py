from datetime import datetime
from pathlib import Path

from flask import Flask, render_template, request, send_from_directory
from werkzeug.utils import secure_filename

from evaluador import Evaluador
from mejorador import Mejorador
from utilidades import guardar_imagen, leer_imagen_pil

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "img_output"
UPLOAD_DIR = BASE_DIR / "tmp_uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "bmp", "gif", "webp"}

OUTPUT_DIR.mkdir(exist_ok=True)
UPLOAD_DIR.mkdir(exist_ok=True)

app = Flask(__name__)


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def make_filename(prefix: str, filename: str) -> str:
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    return f"{prefix}_{timestamp}_{secure_filename(filename)}"


@app.route("/", methods=["GET", "POST"])
def index():
    error = None
    result = None

    if request.method == "POST":
        archivo = request.files.get("imagen")

        if archivo is None or archivo.filename == "":
            error = "Selecciona un archivo de imagen para procesar."
        elif not allowed_file(archivo.filename):
            error = "Formato de imagen no válido. Usa PNG, JPG, JPEG, BMP, GIF o WEBP."
        else:
            temp_path = UPLOAD_DIR / make_filename("upload", archivo.filename)
            archivo.save(str(temp_path))

            try:
                imagen = leer_imagen_pil(str(temp_path))
            except Exception as exc:
                error = f"No se pudo leer la imagen: {exc}"
            else:
                try:
                    evaluador = Evaluador()
                    evaluacion_inicial = evaluador.evaluar(imagen)

                    mejorador = Mejorador()
                    resultado_mejora = mejorador.procesar(imagen)

                    nombre_original = make_filename("original", archivo.filename)
                    guardar_imagen(imagen, nombre_original)

                    nombre_mejorada = make_filename("mejorada", archivo.filename)
                    guardar_imagen(resultado_mejora["imagen_final"], nombre_mejorada)

                    result = {
                        "original_url": url_for_img_output(nombre_original),
                        "mejorada_url": url_for_img_output(nombre_mejorada),
                        "evaluacion_inicial": evaluacion_inicial,
                        "evaluacion_final": resultado_mejora["iteraciones"][-1],
                        "score_final": resultado_mejora["score_final"],
                        "iteraciones": resultado_mejora["total_iteraciones"],
                        "mejora_porcentual": resultado_mejora["mejora_porcentual"],
                        "exitoso": resultado_mejora["exitoso"],
                        "metricas_inicial": evaluacion_inicial["metricas"],
                        "metricas_final": resultado_mejora["iteraciones"][-1]["metricas"],
                    }
                except Exception as exc:
                    error = f"Error al procesar la imagen: {exc}"

    return render_template("index.html", error=error, result=result)


def url_for_img_output(filename: str) -> str:
    return f"/img_output/{filename}"


@app.route("/img_output/<path:filename>")
def img_output(filename: str):
    return send_from_directory(str(OUTPUT_DIR), filename)


if __name__ == "__main__":
    app.run(debug=True)
