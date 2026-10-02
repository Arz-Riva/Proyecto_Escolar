# ==========================================
# Encabezados y Librerias
# ==========================================
import os
import math
from PIL import Image, ImageDraw, ImageFont

# ==========================================
# Declaracion de Constantes
# ==========================================
DIR_ACTUAL = os.path.dirname(os.path.abspath(__file__))
RUTA_PNG_ICON = os.path.join(DIR_ACTUAL, "intresta-icon.png")
RUTA_ICO_ICON = os.path.join(DIR_ACTUAL, "intresta-icon.ico")
RUTA_PNG_LOGO = os.path.join(DIR_ACTUAL, "intresta-logo-horizontal.png")

COLOR_GRAD_INICIO = (59, 31, 92)    # #3B1F5C
COLOR_GRAD_FIN = (13, 7, 20)        # #0D0714
COLOR_DORADO = (245, 196, 0)        # #F5C400
COLOR_BLANCO = (255, 255, 255)


def crear_imagen_icono(ancho: int = 512, alto: int = 512) -> Image.Image:
    """Genera la imagen del icono de Intresta con fondo degradado y graficos vectoriales."""
    img = Image.new("RGBA", (ancho, alto), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Mascara redondeada
    mascara_fondo = Image.new("L", (ancho, alto), 0)
    draw_mascara = ImageDraw.Draw(mascara_fondo)
    draw_mascara.rounded_rectangle((0, 0, ancho - 1, alto - 1), radius=int(96 * ancho / 512), fill=255)

    # Fondo con degradado diagonal
    fondo_grad = Image.new("RGBA", (ancho, alto))
    draw_grad = ImageDraw.Draw(fondo_grad)
    for y in range(alto):
        for x in range(ancho):
            t = (x + y) / (ancho + alto)
            r = int(COLOR_GRAD_INICIO[0] + t * (COLOR_GRAD_FIN[0] - COLOR_GRAD_INICIO[0]))
            g = int(COLOR_GRAD_INICIO[1] + t * (COLOR_GRAD_FIN[1] - COLOR_GRAD_INICIO[1]))
            b = int(COLOR_GRAD_INICIO[2] + t * (COLOR_GRAD_FIN[2] - COLOR_GRAD_INICIO[2]))
            draw_grad.point((x, y), fill=(r, g, b, 255))

    img.paste(fondo_grad, (0, 0), mascara_fondo)

    # Factor de escala
    escala = ancho / 512.0

    # Barras ascendentes
    draw.rounded_rectangle(
        (140 * escala, 300 * escala, (140 + 56) * escala, (300 + 120) * escala),
        radius=int(10 * escala), fill=COLOR_BLANCO
    )
    draw.rounded_rectangle(
        (228 * escala, 230 * escala, (228 + 56) * escala, (230 + 190) * escala),
        radius=int(10 * escala), fill=COLOR_DORADO
    )
    draw.rounded_rectangle(
        (316 * escala, 150 * escala, (316 + 56) * escala, (150 + 270) * escala),
        radius=int(10 * escala), fill=COLOR_BLANCO
    )

    # Flecha ascendente
    puntos_flecha = [
        (150 * escala, 260 * escala),
        (260 * escala, 170 * escala),
        (360 * escala, 130 * escala)
    ]
    draw.line(puntos_flecha, fill=COLOR_DORADO, width=int(18 * escala), joint="round")

    # Punta de flecha
    cabeza_flecha = [
        (360 * escala, 130 * escala),
        (400 * escala, 122 * escala),
        (392 * escala, 162 * escala)
    ]
    draw.polygon(cabeza_flecha, fill=COLOR_DORADO)

    return img


def crear_logo_horizontal(ancho: int = 450, alto: int = 130) -> Image.Image:
    """Genera el logo horizontal de Intresta con el isotipo a la izquierda y el nombre a la derecha."""
    img = Image.new("RGBA", (ancho, alto), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Generar el icono a escala para el lateral
    tamano_icono = alto - 10
    icono_cuadrado = crear_imagen_icono(tamano_icono, tamano_icono)
    img.paste(icono_cuadrado, (5, 5), icono_cuadrado)

    # Dibujar el texto "Intresta"
    # Buscar una fuente del sistema limpia (Segoe UI o Arial)
    fuente = None
    for nombre_fuente in ["segoeuib.ttf", "segoeui.ttf", "arialbd.ttf", "arial.ttf"]:
        try:
            ruta_fuente = os.path.join(os.environ.get("WINDIR", "C:\\Windows"), "Fonts", nombre_fuente)
            if os.path.exists(ruta_fuente):
                fuente = ImageFont.truetype(ruta_fuente, size=int(alto * 0.52))
                break
        except Exception:
            continue

    if fuente is None:
        fuente = ImageFont.load_default()

    # Color blanco brillante para contrastar perfectamente sobre el fondo morado
    pos_x = tamano_icono + 24
    pos_y = int((alto - (alto * 0.52)) / 2) - 4
    draw.text((pos_x, pos_y), "Intresta", font=fuente, fill=(255, 255, 255, 255))

    return img


def main():
    print("Generando recursos graficos en:", DIR_ACTUAL)
    # 1. Generar PNG de alta resolucion
    img_icon = crear_imagen_icono(256, 256)
    img_icon.save(RUTA_PNG_ICON, format="PNG")

    # 2. Generar ICO con multiples tamanos para Windows
    img_icon.save(
        RUTA_ICO_ICON,
        format="ICO",
        sizes=[(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)]
    )

    # 3. Generar logo horizontal para el encabezado
    img_logo = crear_logo_horizontal(320, 75)
    img_logo.save(RUTA_PNG_LOGO, format="PNG")

    print("Archivos generados exitosamente:")
    print(" -", RUTA_PNG_ICON)
    print(" -", RUTA_ICO_ICON)
    print(" -", RUTA_PNG_LOGO)


if __name__ == "__main__":
    main()
