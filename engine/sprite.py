from re import X
from engine.canvas import Canvas
from engine.render_object import RenderObject
from engine.texture import Texture
from engine.drawing import draw_texture
from engine.utility import Bounds

class Sprite(RenderObject):
    def __init__(self):
        super().__init__()

        self._texture: Texture = None
        self._position_x: float = 0.0
        self._position_y: float = 0.0
        self._is_visible: bool = True
        self._opacity: float = 1.0

    """
    [OVERRIDE] update

    Args:
        delta_time(float): Die Zeit, die seit dem letzten Aufruf der Prozedur vergangen ist.
    """
    def update(self, delta_time: float):
        if self._texture == None:
            return
        self._texture.update(delta_time)

    """
    [OVERRIDE] draw
        Zeichnet die Textur des Sprites auf ein Canvas

    Args:
        canvas(Canvas): Das Canvas, auf das die Textur gezeichnet werden soll
    """
    def draw(self, canvas: Canvas):
        if self._texture == None:
            return
        tex_width_rel, tex_height_rel = self._texture.relative_size
        x, y = canvas.get_pixel_position_undistorted(self._position_x - (tex_width_rel / 2.0), self._position_y + (tex_height_rel / 2.0))
        draw_texture(canvas, x, y, self._texture, self._opacity, self.shader)

    """
    [OVERRIDE] set_position
        Legt die Position des Sprites fest

    Args:
        x(float): Die X-Koordinate des Sprites (Relativ)
        y(float): Die Y-Koordinate des Sprites (Relativ)
    """
    def set_position(self, x: float, y: float):
        self._position_x = x 
        self._position_y = y

    """
    [OVERRIDE] get_bounds
        Gibt die Maße des RenderObjects zurück

    Returns:
        (Bounds): Die Maße des RenderObjects
    """
    def get_bounds(self) -> Bounds:
        width, height = self._texture.relative_size
        return Bounds(width, height, self._position_x, self._position_y)

    # GETTERS / SETTERS

    @property
    def texture(self):
        return self._texture

    @texture.setter
    def texture(self, tex: Texture):
        self._texture = tex


    @property
    def is_visible(self) -> bool:
        return self._is_visible

    @is_visible.setter
    def is_visible(self, value: bool):
        self._is_visible = value

    
    @property
    def opacity(self) -> float:
        return self._opacity

    @opacity.setter
    def opacity(self, value: float):
        self._opacity = max(0.0, min(1.0, value))