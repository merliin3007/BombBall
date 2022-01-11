from math import sqrt
import multiprocessing

from engine.canvas import Canvas
from engine.texture import Texture
from engine.shader import PixelShader, StandardShader, NoShader

"""
Hier enthaltene Funktionen sind dafür zuständig, direkt auf die Pixeldaten 
eines Canvas zu zeichenen. Alle Positions- und Größenangaben müssen in 
Pixeln angegegeben werden.

Texturen sind effizienter als die Drawing-Algorithmen, da das Zeichnen von 
Pixeln außerhalb des sichtbaren Bereichs verhindert werden kann und
außerdem nicht die in Pyhton langsamen wihle-loops verwendet werden müssen.
Außnahmen, was das Zeichnen von Pixeln außerhalb des sichtbaren Bereichs angeht:
    - Rectangle (momentan noch nicht)
"""


no_shader = NoShader()


"""
blend_argb_pixel
    Zeichnet einen Argb-Pixel unter Berücksichtigung der Deckkraft auf ein Canvas

Args:
    canvas(Canvas): Das Canvas, auf den der Pixel gezeichnet werden soll
    x(int): Die X-Koordinate, an der der Argb-Pixel gezeichnet werden soll (in Pixeln)
    y(int): Die Y-Koordinate, an der der Argb-Pixel gezeichnet werden soll (in Pixeln)
    argb_pixel(list[4]): Der Argb-Pixel ([a,r,g,b])
    opacity(float): Die Deckkraft des Pixels
    shader(PixelShader): Der Shader, mit dem der Pixel gezeichnet werden soll
"""
def blend_argb_pixel(canvas: Canvas, x: int, y: int, argb_pixel: list, opacity: float = 1.0, shader: PixelShader = no_shader):
    alpha: float = argb_pixel[0] / 255.0
    alpha *= opacity
    if alpha == 0.0:
        return
    if shader != None:
        argb_pixel = shader[x, y, argb_pixel]
    r = int((canvas[x,y][0] * (1.0 - alpha)) + (argb_pixel[1] * alpha))
    g = int((canvas[x,y][1] * (1.0 - alpha)) + (argb_pixel[2] * alpha))
    b = int((canvas[x,y][2] * (1.0 - alpha)) + (argb_pixel[3] * alpha))
    canvas[x,y] = [r, g, b]

"""
draw_rectangle
    Zeichnet ein Rechteck

Args:
    canvas(Canvas): Canvas, auf das gezeichnet werden soll.
    x(int): X-Position der oberen linken Ecke (in Pixeln)
    y(int): Y-Postiion der oberen linken Ecke (in Pixeln)
    width(int): Breite (in Pixeln)
    height(int): Höhe (in Pixeln)
    color(list): Farbe ([r,g,b])
"""
def draw_rectangle(canvas: Canvas, x: int, y: int, width: int, height: int, color: list):
    for j in range(width):
        for i in range(height):
            blend_argb_pixel(canvas, x + j, y + i, [255, color[0], color[1], color[2]])
            #canvas[x + j, y - i] = color

"""
draw_thich_line
    anti-aliased thick line (Bresenham)
    http://members.chello.at/~easyfilter/bresenham.html

-> Funktioniert aus irgendeinem Grund nicht, kann weg.
"""
def draw_thick_line(canvas: Canvas, x0: int, y0: int, x1: int, y1: int, color: list, wd: float):
    dx = abs(x1 - x0)
    sx = 1 if x0 < x1 else -1
    dy = abs(y1 - y0)
    sy = 1 if y0 < y1 else -1
    err = dx - dy
    e2 = 0
    x2 = 0
    y2 = 0
    ed = 1 if dx + dy == 0 else sqrt(float(dx * dx) + float(dy * dy))

    wd = (wd + 1) / 2
    while True:
        # set pixel color
        pixel_opacity = max(0, abs(err-dx+dy)/ed-wd+1) # 0.0 - 1.0
        canvas[x0, y0] = [color[0] * pixel_opacity, color[1] * pixel_opacity, color[2] * pixel_opacity]
        
        e2 = err
        x2 = x0
        if 2*e2 >= -dx:
            e2 = dx-e2
            while e2 < ed*wd and (x1 != x2 or dx < dy):
                # set pixel color
                pixel_opacity = max(0, abs(e2)/ed-wd+1) # 0.0 - 1.0
                canvas[x0, y2] = [color[0] * pixel_opacity, color[1] * pixel_opacity, color[2] * pixel_opacity]
                y2 += sy
                # increment
                e2 += dy
            if x0 == x1:
                break
            e2 = err
            err -= dy
            x0 += sx
        if 2*e2 <= dy:
            e2 = dx-e2
            while e2 < ed*wd and (x1 != x2 or dx < dy):
                # set pixel color
                pixel_opacity = max(0, abs(e2)/ed-wd+1) # 0.0 - 1.0
                canvas[x2, y0] = [color[0] * pixel_opacity, color[1] * pixel_opacity, color[2] * pixel_opacity]
                x2 += sx
                # increment
                e2 += dx
            if y0 == y1:
                break
            err += dx
            y0 += sy

"""
draw_circle
    Zeichnet einen gefüllten Kreis mithilfe des 'Horn-Algorithmus'
    Abgewandelt von http://members.chello.at/~easyfilter/bresenham.html
        -> ergänzt um horizontale Linien, um einen gefüllten Kreis zu zeichnen.

Args:
    canvas(Canvas): Das Canvas, auf dem der Kreis gezeichnet werden soll
    radius(float): Der Radius des Kreises (in Pixeln)
    center_x(float): Die X-Koordinate des Kreises (in Pixeln)
    center_y(float): Die Y-Koordinate des Kreises (in Pixeln)
    color(list): Die Farbe des Kreises ([r,g,b])
"""
def draw_circle(canvas: Canvas, radius: float, center_x: float, center_y: float, color: list):
    # Horn Algorithmus
    d = -radius
    x = radius
    y = 0
    while not(y > x):
        # fill (drawing horizontal lines)
        for i in range(x):
            canvas[center_x + i, center_y + y] = color
            canvas[center_x + i, center_y - y] = color
            canvas[center_x - i, center_y - y] = color
            canvas[center_x - i, center_y + y] = color

            canvas[center_x + y, center_y + i] = color
            canvas[center_x + y, center_y - i] = color
            canvas[center_x - y, center_y - i] = color
            canvas[center_x - y, center_y + i] = color

        d = d + 2 * y + 1
        y = y + 1
        if d > 0:
            x -= 1
            d -= 2 * x 

"""
draw_line
    Zeichnet eine Linie mithilfe von 'Bresenhams line algorithm'
    Abgewandelt von: http://members.chello.at/~easyfilter/bresenham.html

Args:
    canvas(Canvas): Das Canvas, auf dem die Linie gezeichnet werden soll.
    x0(int): Die X-Koordinate des Anfangspunktes der Linie (in Pixeln)
    y0(int): Die Y-Koordinate des Anfangspunktes der Linie (in Pixeln)
    x1(int): Die X-Koordinate des Endpunktes der Linie (in Pixeln)
    y1(int): Die Y-Koordinate des Endpunktes des Linie (in Pixeln)
    color(list): Die Farbe der Linie ([r,g,b])
    thickness(int): Die Stärke der Linie (in Pixeln)
"""
def draw_line(canvas: Canvas, x0: int, y0: int, x1: int, y1: int, color: list, thickness: int):
    dot_radius = int(thickness / 2)
    # Bresenham's line algorithm
    dx = abs(x1-x0)
    sx = 1 if x0<x1 else -1
    dy = -abs(y1-y0)
    sy = 1 if y0<y1 else -1
    err = dx+dy
    e2 = 0

    while True:
        draw_circle(canvas, dot_radius, x0, y0, color)
        if x0 == x1 and y0 == y1:
            break
        e2 = 2*err
        if e2 > dy:
            err += dy
            x0 += sx
        if e2 < dx:
            err += dx
            y0 += sy

"""
get_bezier_point
    Hilfsfunktion für die Prozedur 'draw_bezier_curve'
    http://members.chello.at/~easyfilter/bresenham.html
"""
def get_bezier_point(points: list, t: float):
    tmp = []
    for point in points:
        tmp.append(point.copy())
    
    i = len(tmp) - 1
    while (i > 0):
        k = 0
        while k < i:
            tmp[k][0] = tmp[k][0] + t * (tmp[k+1][0] - tmp[k][0])
            tmp[k][1] = tmp[k][1] + t * (tmp[k+1][1] - tmp[k][1])
            # increment
            k += 1
        # decrement
        i -= 1
    answer = tmp[0]
    return answer

"""
draw_bezier_curve
    Zeichnet eine Bezier-Kurve mit beliebiger Anzahl von Punkten
    http://members.chello.at/~easyfilter/bresenham.html

bezier_precision(float): Die Genauigkeit, mit der Bezierkurven gezeichnet werden
    (Da die Auflösung des Lighthouse sehr niedrig ist, sind höhe Genauigkeiten unnötig rechenintensiv)

Args:
    canvas(Canvas): Das Canvas, auf dem die Bezier-Kurve gezeichnet werden soll
    points(list): Liste der Punkte der Bezier-Kurve ([[x0,y0], [x1,y1], [x2, y2], ...]) (x,y in Pixeln)
    color(list): Die Farbe der Bezier-Kurve ([r,g,b])
    thickness(int): Die Stärke der Linie (in Pixeln)
"""
bezier_precision: float = 0.1
def draw_bezier_curve(canvas: Canvas, points: list, color: list, thickness: int):
    last_point = get_bezier_point(points, 0.0)
    for i in range(1, int(1 / bezier_precision) + 1):
        pnt = get_bezier_point(points, i * bezier_precision)
        draw_line(canvas, int(last_point[0]), int(last_point[1]), int(pnt[0]), int(pnt[1]), color, thickness)
        last_point = pnt

"""
draw_texture
    Zeichnet eine Textur
    Nur der sichtbare Bereich wird gerendert, um unnötige Berechnungen zu verhindern

Laufzeitkomplexität:
    Textur ist im sichtbaren Bereich: O(n) (bei n sichtbaren Pixeln)
    Textur ist außerhalb des sichtbaren Bereichs: O(1)

Args:
    canvas(Canvas): Das Canvas, auf dem die Textur gezeichnet werden soll.
    x(int): Die X-Koordinate der Oberen Linken Ecke der zu zeichnenden Textur
    y(int): Die Y-Koordinate der Oberen Linken Ecke der zu zeichnenden Textur
    texture(Texture): Die zu zeichnende Textur
    opacity(float): Die Deckkraft der Textur
    shader(PixelShader): Der Shader, mit dem die Textur gezeichnet werden soll
"""
def draw_texture(canvas: Canvas, x, y, tex: Texture, opacity: float = 1.0, shader: PixelShader = no_shader):
    if x > canvas.pixel_width: return
    if y > canvas.pixel_height: return

    if shader == None: 
        shader = no_shader

    tex.calc_render_dimensions(canvas)

    # Den Ausschnitt der Textur berechnen, der tatsächlich im Bereich des Canvas und damit sichtbar ist
    begin_j: int = max(0, min(-x, tex.pixel_width))
    end_j: int = min(tex.pixel_width - max(0, (tex.pixel_width + x) - canvas.pixel_width), tex.pixel_width)    
    begin_i: int = max(0, min(-y, tex.pixel_height))
    end_i: int = min(tex.pixel_height - max(0, (tex.pixel_height + y) - canvas.pixel_height), tex.pixel_height)

    # Textur zeichnen
    #[blend_argb_pixel(canvas, x + j, y + i, tex[j, i], opacity, shader) for i in range(begin_i, end_i) for j in range(begin_j, end_j)] # soll schneller sein, erkenne aber keinen unterschied
    #return
    for j in range(begin_j, end_j):
        for i in range(begin_i, end_i):
            blend_argb_pixel(canvas, x + j, y + i, tex[j, i], opacity, shader)










"""
draw_prescaled_texture
    Zeichnet eine Vorskalierte Textur
    Nur der sichtbare Bereich wird gerendert, um unnötige Berechnungen zu verhindern

Laufzeitkomplexität:
    Textur ist im sichtbaren Bereich: O(n) (bei n sichtbaren Pixeln)
    Textur ist außerhalb des sichtbaren Bereichs: O(1)

Args:
    canvas(Canvas): Das Canvas, auf dem die Textur gezeichnet werden soll.
    x(int): Die X-Koordinate der Oberen Linken Ecke der zu zeichnenden Textur
    y(int): Die Y-Koordinate der Oberen Linken Ecke der zu zeichnenden Textur
    texture(Texture): Die zu zeichnende Textur
"""
def draw_prescaled_texture(canvas: Canvas, x, y, tex: Texture):
    if x > canvas.pixel_width: return
    if y > canvas.pixel_height: return

    # Den Ausschnitt der Textur berechnen, der tatsächlich im Bereich des Canvas ist und damit sichtbar ist
    begin_j: int = max(0, min(-x, tex.pixel_width))
    end_j: int = min(tex.pixel_width - max(0, (tex.pixel_width + x) - canvas.pixel_width), tex.pixel_width)    
    begin_i: int = max(0, min(-y, tex.pixel_height))
    end_i: int = min(tex.pixel_height - max(0, (tex.pixel_height + y) - canvas.pixel_height), tex.pixel_height)

    # Textur zeichnen
    for j in range(begin_j, end_j):
        for i in range(begin_i, end_i):
            blend_argb_pixel(canvas, x + j, y + i, tex[j, i])

# ohne Optimisierung, zeichnet auch pixel außerhalb des Canvas
def draw_texture_old(canvas: Canvas, x, y, tex: Texture):
    for j in range(tex.pixel_width):
        for i in range(tex.pixel_height):
            blend_argb_pixel(canvas, x + j, y + i, tex[j, i])
            #canvas[x + j, y + i] = tex[j, i]
    pass