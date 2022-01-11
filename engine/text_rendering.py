from numpy import sin
from engine.canvas import Canvas
from engine.render_layer import RenderLayer
from engine.render_object import RenderObject
from engine.fonts.std_font import std_font
from engine.drawing import draw_bezier_curve, draw_circle, draw_line

import math

CHAR_MIN_PXL_THICHNESS = 2 # Die minimale Dicke ein Linie eines Chars

"""
CharRenderObject(RenderObject) Class
    Ein RenderObject, durch dass ein Buchstabe oder Zeichen gerendert werden kann.
"""
class CharRenderObject(RenderObject):
    def __init__(self, char_code: int):
        super().__init__()

        self.char_code = char_code
        self.line_thichness = 5
        self.font_size = 0.75 # 1.0 = Bildfüllend
        #self.brightness = 1.0
        self.time = 0.0
        self.shift_x = 0.0
        self.shift_y = 0.0

    """
    set_shift
        Legt die Position des Chars fest

    Args:
        x(float): Die Menge, um die der Char entlang der X-Achse verschoben sein soll
        y(float): Die Menge, um die der Char englang der Y-Achse verschoben sein soll
    """
    def set_shift(self, x: float, y: float):
        self.shift_x = x
        self.shift_y = y

    """
    [OVERRIDE] update

    Args:
        delta_time(float): Die Zeit, die seit dem letzten Aufruf der Prozedur vergangen ist
    """
    def update(self, delta_time: float):
        #self.time += 0.1 * delta_time
        #self.font_size -= 0.01
        pass

    """
    [OVERRIDE] draw
        Zeichnet den Char auf ein Canvas

    Args:
        canvas(Canvas): Das Canvas, auf das gezeichnet werden soll
    """
    def draw(self, canvas: Canvas):
        line_thickness_pixels = max(CHAR_MIN_PXL_THICHNESS, int(self.line_thichness * self.font_size * canvas.supersampling))
        margin = (1.0 - self.font_size) / 2.0
        for line in std_font.chars[self.char_code]:
            # dot
            if len(line) == 1:
                x, y = canvas.get_pixel_position(line[0][0] * self.font_size + margin + self.shift_x, line[0][1] * self.font_size + margin + self.shift_y)
                draw_circle(canvas, line_thickness_pixels, x, y, [255, 255, 255])
            # line
            elif len(line) == 2:
                x0, y0 = canvas.get_pixel_position(line[0][0] * self.font_size + margin + self.shift_x, line[0][1] * self.font_size + margin + self.shift_y)
                x1, y1 = canvas.get_pixel_position(line[1][0] * self.font_size + margin + self.shift_x, line[1][1] * self.font_size + margin + self.shift_y)
                draw_line(canvas, x0, y0, x1, y1, [255, 255, 255], line_thickness_pixels)
            # bezier curve
            elif len(line) > 2:
                points = []
                for point in line:
                    x, y = canvas.get_pixel_position(point[0] * self.font_size + margin + self.shift_x, point[1] * self.font_size + margin)
                    points.append([x,y])
                draw_bezier_curve(canvas, points, [255, 255, 255], line_thickness_pixels)

"""
HorizontalScrollTextLayer(RenderLayer) Class
    Ein RenderLayer, der einen scrollenden Text rendert
"""
class HorizontalScrollTextLayer(RenderLayer):
    def __init__(self, text: str):
        self.repeat = True
        self.is_playing = True
        self.text = text
        self.text_size = 0.75
        self.char_spacing = 0.1
        self.current_shift = -self.text_size
        self.__init_char_render_objects()

    """
    [OVERRIDE] update
        Updated den Scrolltext

    Args:
        delta_time(float): Die Zeit, die seit dem letzten Aufruf der Prozedur vergangen ist
    """
    def update(self, delta_time: float):
        self.current_shift += delta_time

    """
    [OVERRIDE] render
        Rendert den ScrollText auf ein Canvas

    Args:]
        canvas(Canvas): Das Canvas, auf das gerendert werden soll
    """
    def render(self, canvas: Canvas):
        if not self.is_playing:
            return
        rendered_char = False
        for i in range(len(self.char_render_objects)):
            position = (i * self.text_size) - self.current_shift
            # Wenn Char links außerhalb des Canvas ist:
            if position < -self.text_size:
                continue
            # Wenn Char richts außerhalt des Canvss ist:
            if position > 1.0 + self.text_size:
                break # Loop kann abgebrochen weden, da alle weiteren Chars auch außerhalb sind
            # Render
            self.char_render_objects[i].shift_x = position
            self.char_render_objects[i].draw(canvas)
            rendered_char = True
        if not rendered_char and self.current_shift != -self.text_size:
            self.current_shift = -self.text_size
            if not self.repeat:
                self.is_playing = False

    """
    __init_char_render_objects
        Initialisiert die CharRenderObjects, die den Text repräsentieren
    """
    def __init_char_render_objects(self):
        self.char_render_objects = []
        for c in self.text:
            char_render_object = CharRenderObject(ord(c))
            char_render_object.font_size = self.text_size
            self.char_render_objects.append(char_render_object)

"""
ShrinkTextLayer(RenderLayer) Class
    Ein RenderLayer, der einen schrumpfenden Text rendert
"""
class ShrinkTextLayer(RenderLayer):
    def __init__(self, text: str):
        self.repeat = True
        self.text = text
        self.text_pos = 0
        self.char_age = 0.0

        self.is_playing = True
        self.char_render_object = CharRenderObject(65)
        
        self.reset_anim()

    """
    set_text
        Legt den Text fest, der gerendert werden soll

    Args:
        text(str): Der zu rendernde Text
    """
    def set_text(self, text: str):
        self.text = text
        self.reset_anim()

    """
    [OVERRIDE] update
        Updated den ShrinkText

    Args:
        delta_time(float): Die Zeit, die seit dem letzten Aufruf der Prozedur vergangen ist.
    """
    def update(self, delta_time: float):
        if not self.is_playing:
            return

        if len(self.text) == 0:
            self.is_playing = False
            return

        self.char_age += delta_time
        self.char_render_object.font_size -= delta_time

        if self.char_age >= 1.0:
            self.char_age = 0.0
            self.text_pos += 1
            if self.text_pos >= len(self.text):
                self.text_pos = 0
                if not self.repeat:
                    self.is_playing = False
            self.reset_anim()

    """
    reset_anim
        Setzt die Animation zurück
    """
    def reset_anim(self):
        if len(self.text) != 0:
            self.char_render_object = CharRenderObject(ord(self.text[self.text_pos]))
        self.char_render_object.font_size = 1.0
        self.char_age = 0.0

    """
    [OVERRIDE] render
        Rendert den ShrinkText

    Args:
        canvas(Canvas): Das Canvas, auf das gerendert werden soll.
    """
    def render(self, canvas: Canvas):
        self.char_render_object.draw(canvas)