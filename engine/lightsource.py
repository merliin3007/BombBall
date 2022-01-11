from engine.render_object import RenderObject
from engine.shader import LightShader
from engine.texture import Texture
from engine.canvas import Canvas
from engine.sprite import Sprite
from engine.utility import Bounds, overrides

"""
LightSource Class
    Repräsentiert eine Lichtquelle
"""
class LightSource(RenderObject):
    def __init__(self):
        super().__init__()
        self._texture: Texture = None
        self._mask_texture: Texture = None
        self._sprite = Sprite()
        self._bloom_sprite = Sprite()
        self._brightness: float = 1.0 # 0.0 - 1.0, Helligkeit der Lichtquelle
        self._shader = LightShader()


        # für bloom render
        self.left_pixel: int = 0
        self.right_pixel: int = 0
        self.top_pixel: int = 0
        self.bottom_pixel: int = 0
    
    """
    update

    Args:
        delta_time(float): Die Zeit, die seit dem letzten Aufruf der Prozedur vergangen ist.
    """
    @overrides(RenderObject)
    def update(self, delta_time: float):
        pass
    
    """
    draw
        Zeichnet die Lichtquelle

    Args:
        canvas(Canvas): Das Canvas, auf das gezeichnet werden soll
    """
    @overrides(RenderObject)
    def draw(self, canvas: Canvas):
        if self._texture == None:
            return
        canvas.currently_is_drawing_lightsource = True
        mask_texture_pixel_width: int = canvas.relative_distance_to_pixel_distance(self._texture.size)
        self._mask_texture = self._texture.clone_rescaled(mask_texture_pixel_width)
        canvas.register_lightsource(self)
        self._sprite.draw(canvas)
        canvas.currently_is_drawing_lightsource = False

    """
    draw_bloom
        Zeichnet einen Bloom für die Lichtquelle

    Args:
        canvas(Canvas): Das Canvas, auf das der Bloom gezeichnet werden soll.
    """
    def draw_bloom(self, canvas: Canvas, bloom_size: float = 3.375, bloom_quality: int = 3):
        canvas.currently_is_drawing_lightsource = True
        self._bloom_sprite.opacity = self._brightness
        self._bloom_sprite.texture = self._mask_texture
        self._bloom_sprite.set_position(self._sprite._position_x, self._sprite._position_y)
        for i in range(3):
            self._mask_texture.size *= 1.5
            self._bloom_sprite.opacity /= 2.0
            self._bloom_sprite.shader = self._shader
            self._bloom_sprite.draw(canvas)
        canvas.currently_is_drawing_lightsource = False

    """
    mask_out_pixel
        Maskiert einen Pixel aus, setzt diesen also vor die Lichtquelle,
        sodass die Lichtquelle im Punkt des Pixels blockiert ist.

    Args:
        x(int): Die X-Achsen Position des Pixels (in Pixeln)
        y(int): Die Y-Achsen Position des Pixels (in Pixeln)
        alpha(int): Die Deckkraft des Pixels
    """
    def mask_out_pixel(self, x: int, y: int, alpha: int = 0):
        self._mask_texture.set_original_pixel(x, y, [0, 0, 0, alpha])

    """
    set_position
        Legt die Position der Lichtquelle fest.

    Args:
        x(float): Die X-Achsen Position (relativ)
        y(float): Die Y-Achsen Position (relativ)
    """
    @overrides(RenderObject)
    def set_position(self, x: float, y: float):
        self._sprite.set_position(x, y)
        self._bloom_sprite.set_position(x, y)

    """
    get_bounds
        Gibt die Maße der Lichtquelle zurück

    Returns:
        self._sprite.get_bounds(Bounds): Die Maße des Lichtquelle
    """
    def get_bounds(self) -> Bounds:
        return self._sprite.get_bounds()

    # properties

    """
    textur
        Ruft die Textur ab, als die die Lichtquelle gerendert wird, oder legt diese fest.
    """
    @property
    def texture(self) -> Texture:
        return self._texture

    @texture.setter
    def texture(self, value: Texture):
        self._texture = value
        self._sprite.texture = self._texture

    """
    is_visible
        Gibt an, ob die Lichtquelle sichtbar ist (immer 'Wahr')
    """
    @property
    def is_visible(self) -> bool:
        return True

    """
    brightness
        Gibt die Helligkeit der Lichtquelle an, oder legt diese Fest
        Wert muss zwischen '0.0' (= Ganz Dunkel) und '1.0' (= Ganz Hell) liegen.
    """
    @property
    def brightness(self) -> float:
        return self._brightness

    @brightness.setter
    def brightness(self, value: float):
        self._brightness = max(0.0, min(1.0, value))