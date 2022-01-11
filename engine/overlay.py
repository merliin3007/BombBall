from engine.drawing import draw_circle, draw_line, draw_rectangle
from engine.render_layer import RenderLayer
from engine.render_object import RenderObject, Pawn
from engine.canvas import Canvas
from engine.utility import overrides

class OverlayLayer(RenderLayer):
    def __init__(self):
        self._render_objects: list = []

    def add_object(self, object: RenderObject):
        self._render_objects.append(object)

    @overrides(RenderLayer)
    def update(self, delta_time: float):
        for render_object in self._render_objects:
            render_object: RenderObject = render_object
            render_object.update(delta_time)

    @overrides(RenderLayer)
    def render(self, canvas: Canvas):
        for render_object in self._render_objects:
            render_object: RenderObject = render_object
            render_object.draw(canvas)

class HealthBar(RenderObject):
    def __init__(self):
        self._pawn: Pawn = None
        self._height = 0.1
        self._position_y = 0.0
        self._health: float = 0.0

    @overrides(RenderObject)
    def update(self, delta_time: float):
        if self._pawn == None:
            return
        self._health = self._pawn.health / self._pawn._max_health

    @overrides(RenderObject)
    def draw(self, canvas: Canvas):
        x, pixel_position_y = canvas.get_pixel_position_undistorted(0.0, self._position_y)
        pixel_height: int = canvas.relative_distance_to_pixel_distance(self._height)
        pixel_width: int = canvas.pixel_width
        health_pixel_width: int = int(canvas.pixel_width * self._health)
        
        # draw bar
        draw_rectangle(canvas, 0, pixel_position_y - pixel_height, pixel_width, pixel_height, [25, 0, 0])
        # draw health
        draw_rectangle(canvas, 0, pixel_position_y - pixel_height, health_pixel_width, pixel_height, [255, 0, 0])

    # properties

    '''
    pawn
        Der Pawn, dessen Health angezeigt werden soll.
    '''
    @property
    def pawn(self) -> Pawn:
        return self._pawn

    @pawn.setter
    def pawn(self, pawn: Pawn):
        self._pawn = pawn