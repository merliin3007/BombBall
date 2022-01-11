import json
import os
from math import ceil

from engine.canvas import Canvas
from engine.utility import pure_virtual

"""
Texture: Class
    repräsentiert eine Textur

    Pixelformat: [a, r, g, b]
"""
class Texture:
    def __init__(self, pxl_width: int = 0, pxl_height: int = 0):
        self._pxl_width = pxl_width
        self._pxl_height = pxl_height
        self._pixel_array = []
        self._original_pxl_width = pxl_width
        self._original_pxl_height = pxl_height
        self._original_pixel_array = []
        self._relative_size_x = 0.0
        self._relative_size_y = 0.0
        
        self._render_canvas = None

    """
    __getitem__

    Args:
        index(x,y): x und y Koordinaten des Pixels

    Returns:
        (list): Die Farbwerte des entsprechenden Pixels ([a,r,g,b])
    """
    def __getitem__(self, index):
        x,y = index

        if x >= self._pxl_width or x < 0 or y >= self._pxl_height or y < 0:
            print(f"[Texture] __getitem__ tried to get at non existing position: {x}, {y}.")
            print(f"    self.pixel_width = {self._pxl_width}, self.pixel_height = {self._pxl_height}")
            return [0, 0, 0, 0]
        
        # Scaling
        nearest_pixel_x: int = int(x / self._rescale_factor)
        nearest_pixel_y: int = int(y / self._rescale_factor)

        return self._get_original_pixel(nearest_pixel_x, nearest_pixel_y)

    """
    update

    Args:
        delta_time(float): Die Zeit, die seit dem letzten Aufruf der Prozedur vergangen ist.
    """
    @pure_virtual
    def update(self, delta_time: float):
        pass

    """
    load_from_file
        lädt eine Textur von einer Datei.
        (Rechenintensiv, sollte daher nur vor beginn des Games aufgerufen werden)

        Args:
            filename(str): Der Dateiname der zu ladenden Textur
            canvas(Canvas): Ein Canvas mit den Abmessungen des Canvases, auf den gezeichnet werden soll
                            Hier kann einfach 'GAME.get_empty_canvas()' übergeben werden
            relative_size_x(float): Die relative Größe des Textur
    """
    def load_from_file(self, filename: str, relative_size_x: float = 1.0):
        script_dir = os.getcwd() #os.path.dirname(__file__)
        f = open(os.path.join(script_dir, filename), "r")
        json_text: str = f.read()
        self.load_from_json(json_text, relative_size_x)
        pass

    """
    load_from_json
        lädt eine Textur von einem Json string
        (Rechenintensiv, sollte daher nur vor beginn des Games aufgerufen werden)

        Args:
            json_text(str): Die zu ladende Textur als json repräsentiert
            canvas(Canvas): Ein Canvas mit den Abmessungen des Canvases, auf den gezeichnet werden soll
                            Hier kann einfach 'GAME.get_empty_canvas()' übergeben werden
            relative_size_x(float): Die relative Größe des Textur
    """
    def load_from_json(self, json_text: str, relative_size_x: float = 1.0):
        tex = json.loads(json_text)
        self._pxl_width = int(tex["width"])
        self._pxl_height = int(tex["height"])
        self._pixel_array = tex["pixels"]
        # copy to original pixel data
        self._original_pxl_width = self._pxl_width
        self._original_pxl_height = self.pixel_height
        self._original_pixel_array = self._pixel_array # KEINE KOPIE, nur Referenz, um Speicherplatz zu sparen. Beim Skalieren wird dann eine Kopie erstellt
        self._aspect: float = self._original_pxl_height / self._original_pxl_width
        # set size
        #self.set_relative_size(canvas, relative_size_x)
        self.size = relative_size_x

    """
    clone
        Gibt eine tiefe Kopie der Textur zurück

    Returns
        tex(Texture): Die tiefe Kopie der Textur
    """
    def clone(self):
        tex = Texture()
        tex._pxl_width = self._pxl_width
        tex._pxl_height = self._pxl_height
        #tex._pixel_array = self._pixel_array
        tex._original_pxl_width = self._original_pxl_width
        tex._original_pxl_height = self._original_pxl_height
        tex._original_pixel_array =  []
        #for pixel in self._original_pixel_array:
        #    tex._original_pixel_array.append(pixel)
        tex._original_pixel_array = [pixel for pixel in self._original_pixel_array]
        tex._aspect = self._aspect
        tex.size = self.size
        return tex

    """
    clone_rescaled
        Gibt eine tiefe Kope der Textur zurück und reskalliert dabei die Pixeldaten

    Args
        new_pixel_width(int): Neue Pixelbreite det Textur

    Returns
        tex(Textur): Der Skallierte Klon der Textur
    """
    def clone_rescaled(self, new_pixel_width: int) -> 'Texture':
        tex = Texture()
        tex._pxl_width = self._pxl_width
        tex._pxl_height = self._pxl_height
        tex._original_pxl_width = new_pixel_width
        tex._original_pxl_height = int(new_pixel_width * self._aspect)
        

        # rescale
        tex._original_pixel_array = [[0, 0, 0] for i in range(tex._original_pxl_width * tex._original_pxl_height)]
        rescale_factor: float = new_pixel_width / self._original_pxl_width
        for j in range(tex._original_pxl_width):
            for i in range(tex._original_pxl_height):
                nearest_x: int = int(j / rescale_factor)
                nearest_y: int = int(i / rescale_factor)
                tex.set_original_pixel(j, i, self._get_original_pixel(nearest_x, nearest_y))
                
        tex._aspect = self._aspect
        tex.size = self.size

        return tex

    """
    calc_render_dimensions
        Berechnet die Pixelmaße der Textur zum rendern.
        Sollte vorm Rendern der Textur aufgerufen werden.

    Args:
        canvas(Canvas): Das Canvas anhand dessen Maße die Rendermaße berechnet werden sollen.
    """
    def calc_render_dimensions(self, canvas: Canvas):
        self._pxl_width = canvas.relative_distance_to_pixel_distance(self._relative_size_x)
        self._pxl_height = int(self._pxl_width * self._aspect)
        self._rescale_factor: float = self._pxl_width / self._original_pxl_width

    """
    set_original_pixel
        Setzt die Farbewerte für einen Pixel
    
    Args:
        x(int): X-Position des Pixels
        y(int): Y-Position des Pixels
        color(list[4]) Die neuen Farbwerte des Pixels ([a,r,g,b])
    """
    def set_original_pixel(self, x: int, y: int, color: list):
        if x >= self._original_pxl_width or y >= self._original_pxl_height or x < 0 or y < 0:
            # Wird manchmal beim LightSource RenderMask zeichnen wegen Rundungsungenauigkeit ausgelöst.
            return
        self._original_pixel_array[y * self._original_pxl_width + x] = color

    """
    _get_original_pixel
        Gibt die Farbwerte eines bestimmten Pixels der ursprünglichen Textur (vor Resize etc...) zurück.

    Args:
        x(int): Die X-Koordinate des Pixels (in Pixeln)
        y(int): Die Y-Koordinate des Pixels (in Pixeln)
    """
    def _get_original_pixel(self, x: int, y: int) -> list:
        return self._original_pixel_array[y * self._original_pxl_width + x]


    # properties

    """
    pixel_width
        Gibt die Breite der Textur in Pixeln zurück
    """
    @property
    def pixel_width(self):
        return self._pxl_width

    """
    pixel_height
        Gibt die Höhe der Textur in Pixeln zurück
    """
    @property
    def pixel_height(self):
        return self._pxl_height

    """
    relative_size
        Gibt die aktuellen relativen Maße der Textur zurück.
    TODO: sollte in 'relative_dimensions' umbenannt werden, um Verwechslung mit 'size' zu vermeiden
    """
    @property
    def relative_size(self):
        return self._relative_size_x, self._relative_size_y

    """
    size
        Gibt die relative Größe der Textur an oder legt diese fest.
    """
    @property
    def size(self):
        return self._relative_size_x

    @size.setter
    def size(self, size_x: float):
        self._relative_size_x = size_x
        self._relative_size_y = size_x * self._aspect
