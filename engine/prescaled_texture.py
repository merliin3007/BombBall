import json
import os

from engine.canvas import Canvas

"""
Texture: Class
    repräsentiert eine Textur

    Pixelformat: [a, r, g, b]
"""
class PrescaledTexture:
    def __init__(self, pxl_width: int = 0, pxl_height: int = 0):
        self._pxl_width = pxl_width
        self._pxl_height = pxl_height
        self._pixel_array = []
        self._original_pxl_width = pxl_width
        self._original_pxl_height = pxl_height
        self._original_pixel_array = []
        self._relative_size_x = 0.0
        self._relative_size_y = 0.0
        #for i in range(self._pxl_width * self._pxl_height):
        #    self._pixel_array.append([0, 0, 0, 0])

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

        return self._pixel_array[y * self._pxl_width + x]

    """
    __setitem__

    Args:
        index(x,y): x und y Koordinaten des Pixels
        value(list[4]): Neue Farbwerte für den Pixel ([a,r,g,b])
    """
    def __setitem__(self, index, value: list):
        x,y = index
        
        if x >= self._pxl_width or x < 0:
            return
        if y >= self._pxl_height or y < 0:
            return

        if len(value) != 4:
            raise ValueError('Falsches Pixelformat.')

        self._pixel_array[y * self._pxl_width + x] = value

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
    def load_from_file(self, filename: str, canvas: Canvas, relative_size_x: float = 1.0):
        script_dir = os.getcwd() #os.path.dirname(__file__)
        f = open(os.path.join(script_dir, filename), "r")
        json_text: str = f.read()
        self.load_from_json(json_text, canvas, relative_size_x)
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
    def load_from_json(self, json_text: str, canvas: Canvas, relative_size_x: float = 1.0):
        tex = json.loads(json_text)
        self._pxl_width = int(tex["width"])
        self._pxl_height = int(tex["height"])
        self._pixel_array = tex["pixels"]
        # copy to original pixel data
        self._original_pxl_width = self._pxl_width
        self._original_pxl_height = self.pixel_height
        self._original_pixel_array = self._pixel_array # KEINE KOPIE, nur Referenz, um Speicherplatz zu sparen. Beim Skalieren wird dann eine Kopie erstellt
        # set size
        self.set_relative_size(canvas, relative_size_x)
        pass

    """
    set_relative_size
        Legt die Größe der Textur relativ zu einem Canvas fest und skaliert dafür die Pixeldaten.
        Die originalen Pixeldaten bleiben in _original_pixel_array erhalten, 
        da beim Skalieren Informationen verloren gehen können.
        _pixel_array wird ein NEUER Array.
        ->  Sollte nach Möglichkeit NICHT während des laufenden Spiels aufgerufen werden,
            sondern im Ladescreen oder ähnlichem, da recht rechenintensiv

    Args:
        canvas(Canvas): Das Canvas zu dem die Größe relativ sein soll. Hier kann einfach 'GAME.get_empty_canvas()' übergeben werden.
        size_x(float): Die gewünschte Größte der Textur entlang der X-Achse (relativ), Y-Größe wird automatisch ermittelt
    """
    def set_relative_size(self, canvas: Canvas, size_x: float):
        aspect: float = self._original_pxl_height / self._original_pxl_width
        self._pxl_width = canvas.relative_distance_to_pixel_distance(size_x)
        self._pxl_height = int(self._pxl_width * aspect)
        self._pixel_array = list()
        # fill new pixel array
        for i in range(self._pxl_width * self._pxl_height):
            self._pixel_array.append([0, 0, 0, 0])
        # rescale
        rescale_factor: float = self._pxl_width / self._original_pxl_width
        for j in range(self._pxl_width):
            for i in range(self._pxl_height):
                nearest_pixel_x: int = int(j / rescale_factor)
                nearest_pixel_y: int = int(i / rescale_factor)
                self[j, i] = self._get_original_pixel(nearest_pixel_x, nearest_pixel_y)
        # remember relative size
        self._relative_size_x = size_x
        self._relative_size_y = size_x * aspect

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

    @property
    def pixel_width(self):
        return self._pxl_width

    @property
    def pixel_height(self):
        return self._pxl_height


    @property
    def relative_size(self):
        return self._relative_size_x, self._relative_size_y