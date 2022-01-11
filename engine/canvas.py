from pyghthouse import Pyghthouse
import numpy as np
from engine.shader import PixelShader, SkyShader
from engine.utility import Bounds

from engine.settings import BLOOM_OFFRAME_RENDER_TRESHOLD

"""
Canvas Class
    Repräsentiert die Leinwand, auf die beim Rendern gezeichnet wird.
"""
class Canvas:
    def __init__(self, pixel_width: int, pixel_height: int, supersampling: int, aspect: float, background_color: list = [0, 0, 0], sky_shader: PixelShader = SkyShader()):
        self._view_translation_x: float = 0.0
        self._view_translation_y: float = 0.0
        self.pixel_width = pixel_width * supersampling
        self.pixel_height = int(pixel_height * float(supersampling) * aspect)
        self.supersampling = supersampling
        self.aspect = aspect
        self.brightness = 1.0
        
        self._background_color = background_color
        self._sky_shader: PixelShader = sky_shader

        self.zoom: float = 1.0 # relative breite (1.0 = kein zoom, < 1.0 = weitwinkel, > 1.0 = tele)
        self.reset()

    """
    reset
        Setzt das Canvas zurück
    """
    def reset(self):
        if self._sky_shader.needs_bounds_uniforms:
            self._sky_shader.left_pxl = 0
            self._sky_shader.right_pxl = self.pixel_width
            self._sky_shader.top_pxl = 0
            self._sky_shader.bottom_pxl = self.pixel_height
        self.grid: list = [self._sky_shader.process_pixel(i % self.pixel_width, i / self.pixel_width, self._background_color) for i in range(self.pixel_width * self.pixel_height)]

        from engine.lightsource import LightSource
        self._lightsources: list = []
        self.currently_is_drawing_lightsource: bool = False

    """
    __getitem__
        Gibt die Farbdaten für einen bestimmten Pixel zurück

    Args:
        index(x,y): Die x und y Koordinaten des Pixels (in Pixeln)

    Returns:
        (list[3]): Die Farbdaten des Pixels ([r,g,b])
    """
    def __getitem__(self, index):
        x,y = index

        if x >= self.pixel_width or x < 0 or y >= self.pixel_height or y < 0:
            return [0, 0, 0]

        return self.grid[y * self.pixel_width + x]

    """
    __setitem__
        Legt die Farbdaten für einen Pixel fest.

    Args:
        index(x,y): Die x und y Koordinaten des Pixels (in Pixeln)
        value(list[3]): Die neuen Farbdaten ([r,g,b])
    """
    def __setitem__(self, index, value: list):
        x,y = index
        
        if x >= self.pixel_width or x < 0:
            return
        if y >= self.pixel_height or y < 0:
            return

        if len(value) != 3:
            raise ValueError('Falsches Pixelformat.')

        self.grid[y * self.pixel_width + x] = value

        # Mask on lightsources
        self.mask_lightsource(x, y)
        
    def mask_lightsource(self, x, y):
        if self.currently_is_drawing_lightsource:
            return
        for lightsource in self._lightsources:
            from engine.lightsource import LightSource
            lightsource: LightSource = lightsource
            # es muss keine maske gezeichnet werden, wenn die lightsource garnicht leuchtet
            if lightsource.brightness == 0.0: return
            # Es muss keine Maske gezeichnet werdne, wenn die lightsource außerhalb des Canvas ist.
            if x >= lightsource.left_pixel and x <= lightsource.right_pixel and y >= lightsource.top_pixel and y <= lightsource.bottom_pixel:
                lightsource.mask_out_pixel(x - lightsource.left_pixel, y - lightsource.top_pixel)


    """
    fill
        Füllt das gesamte Canvas mit einer Farbe

    Args:
        r(int): Der Wert des Rot-Kanals
        g(int): Der Wert des Grün-Kanals
        b(int): Der Wert des Blau-Kanals
    """
    def fill(self, r: int, g: int, b: int):
        for i in range(self.pixel_width * self.pixel_height):
            self.grid[i] = [r,g,b]

    """
    get_pixel_position
        Wandelt eine relative Position zu eine Pixel-Koordinate um,
        wobei der Relative Punkt (1.0 | 1.0) oben rechts ist,
        und (0.0 | 0.0) unten links.
        Dadurch entsteht eine Verzerrung, falls das Canvas nicht Quadratisch ist.

    Args:
        x(float): Die relative X-Koordinate
        y(float): Die relative Y-Koordinate

    Returns:
        (int, int): Die entsprechenden Pixel-Koordinaten
    """
    def get_pixel_position(self, x: float, y: float):
        return int(x * self.pixel_width), int((1.0-y) * self.pixel_height)
    
    """
    get_pixel_position_undistorted
        Wie 'get_pixel_position', aber ohne Verzerrung
    
    Args:
        x(float): Die relative X-Koordinate
        y(float): Die relative Y-Koordinate

    Returns:
        (int, int): Die entsprechenden Pixel-Koordinaten
    """
    def get_pixel_position_undistorted(self, x: float, y: float):
        x -= self._view_translation_x
        y -= self._view_translation_y
        return int(x * self.pixel_width * self.zoom), int(self.pixel_height - (y * self.pixel_width * self.zoom))

    """
    form_pixel_position_undistorted
        Gibt zu der Position eines Pixels die entsprechende relative Position zurück.
        (Ohne Verzerrung, d.h y=1.0 ist nur dann ganz oben, wenn das Canvas Quadratisch ist.)

    Args:  
        x(int): Die X-Koordinate des Pixels (in Pixeln)
        y(int): Die Y-Koordinate des Pixels (in Pixeln)
    """
    def from_pixel_position_undistorted(self, x: int, y: int):
        return (x / self.pixel_width / self.zoom) + self._view_translation_x, (((self.pixel_height / self.pixel_width / self.zoom)-y) / self.pixel_height) + self._view_translation_y

    """
    relative_distance_to_pixel_distance
        Rechnet eine relative Strecke in Pixel um.

    Args:
        distance(float): Die Länge der Strecke (relativ)

    Returns:
        (int): Die Länge in Pixeln
    """
    def relative_distance_to_pixel_distance(self, distance: float) -> int:
        return int(distance * self.pixel_width * self.zoom)

    """
    to_array
        Wandelt die Pixeldaten des Canvas in einen Array im passenden Format für Pyghthouse um.
        Verzerrungen werden hier rausgerechnet und das Bild downgesampled (falls SUPERSAMPLING != 1)
    """
    def to_array(self):
        img_downsampled = Pyghthouse.empty_image()
        # downsamling
        for i in range(len(img_downsampled)):
            for j in range(len(img_downsampled[0])):
                red_sum = 0
                green_sum = 0
                blue_sum = 0

                for x in range(int(self.supersampling)):
                    for y in range(int(self.supersampling * self.aspect)):
                        red_sum += self[j * self.supersampling + x, int(i * self.supersampling*self.aspect) + y][0]
                        green_sum += self[j * self.supersampling + x, int(i * self.supersampling*self.aspect) + y][1]
                        blue_sum += self[j * self.supersampling + x, int(i * self.supersampling*self.aspect) + y][2]

                img_downsampled[i][j][0] = (red_sum / (int(float(self.supersampling)*self.aspect) * self.supersampling)) * self.brightness
                img_downsampled[i][j][1] = (green_sum / (int(float(self.supersampling)*self.aspect) * self.supersampling)) * self.brightness
                img_downsampled[i][j][2] = (blue_sum / (int(float(self.supersampling)*self.aspect) * self.supersampling)) * self.brightness
        return img_downsampled

    """
    set_view_translation
        Legt den zu rendernden Ausschnitt fest

    Args:
        x(float): X-Koordinate des Ausschnitts (relativ)
        y(float): Y-Koordinate des Ausschnitss (relativ)
    """
    def set_view_translation(self, x: float, y: float):
        self._view_translation_x = x
        self._view_translation_y = y

    """
    reset_view_translation
        Setzt den zu rendernden Ausschnitt auf (0.0 | 0.0) zurück
    """
    def reset_view_translation(self):
        self._view_translation_x = 0.0
        self._view_translation_y = 0.0

    """
    get_view_translation
        Gibt die relativen Koordinaten des akutellen Renderausschnitts zurück.

    Returns:
        (float, float): Die relativen Koordinaten des momentanen Renderausschnitts.
    """
    def get_view_translation(self):
        return self._view_translation_x, self._view_translation_y

    """
    register_lightsource
        Eine Lichtquelle muss registriert werden, um eine Pixelmask zu zeichnen

    Args
        lightsource(LighSource): Die zu registierende Lichtquelle
    """
    def register_lightsource(self, lightsource):
        from engine.lightsource import LightSource
        lightsource: LightSource = lightsource

        # Bounds in Pixeln berechnen (Zum zeichnen der Pixel maske für bloom)
        view_translation_x = self._view_translation_x
        view_translation_y = self._view_translation_y
        self.reset_view_translation()
        bounds: Bounds = lightsource.get_bounds()
        lightsource.left_pixel, lightsource.top_pixel = self.get_pixel_position_undistorted(bounds.left, bounds.top)
        lightsource.right_pixel, lightsource.bottom_pixel = self.get_pixel_position_undistorted(bounds.right, bounds.bottom)
        self._view_translation_x = view_translation_x
        self._view_translation_y = view_translation_y

        # lightsource merken (wenn im bild)
        tolerance: float = self.pixel_width * BLOOM_OFFRAME_RENDER_TRESHOLD
        if lightsource.left_pixel < self.pixel_width + tolerance and lightsource.right_pixel > 0 - tolerance and lightsource.bottom_pixel + tolerance > 0 and lightsource.top_pixel - tolerance < self.pixel_height:
            self._lightsources.append(lightsource)

    """
    lightsources
        Eine Liste mit allen registrierten Lichtquellen
    """
    @property
    def lightsources(self) -> list:
        return self._lightsources