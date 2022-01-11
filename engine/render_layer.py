from engine.canvas import Canvas
from engine.lightsource import LightSource
from engine.render_object import Pawn, RenderObject, Terrain
from engine.utility import Bounds
from engine.collision import check_collision
from engine.shader import NoShader, PixelShader, StandardShader

class RenderLayer:
    def __init__(self):
        pass

    def update(self, delta_time: float):
        raise NotImplementedError()
    
    def render(self, canvas: Canvas):
        raise NotImplementedError()


"""
GameLayer(RenderLayer) Class
    Ein RenderLayer, in dem Spielobjekte existieren können.
"""
class GameLayer(RenderLayer):
    def __init__(self, z_index: float = 1.0):
        self._view_translation_x: float = 0.0
        self._view_translation_y: float = 0.0

        self._z_index: float = 1.0

        self.pawns: list = []

        self.render_objects = list()
        self._z_index = z_index
        self.terrain: Terrain = None

        # Shaders
        self._standard_shader: StandardShader = StandardShader()
        self._light_shader: NoShader = NoShader()
        # Shader Uniforms
        self._standard_shader.sun_brightness = 1.0
        self._standard_shader.current_z_index = self._z_index

    """
    add_object
        Fügt ein RenderObject hinzu

    Args:
        object(RenderObject): Das hinzuzufügende Objekt
    """
    def add_object(self, object: RenderObject):
        if object == None:
            return

        self.render_objects.append(object)
        object._z_index = self._z_index
        # Pawns noch zu einer extra liste hinzufügen, da diese physics simulation benötigen
        if type(object) == Pawn or issubclass(type(object), Pawn):
            self.pawns.append(object)
        # Terrain merken, wegen collision
        elif type(object) == Terrain:
            self.terrain = object

        # Layereigenen Shader festlegen, falls das RenderObect keinen eigenen Shader hat
        if object.shader == None:
            if type(object) == LightSource:
                object.shader = self._light_shader
            else:
                object.shader = self._standard_shader
    
    """
    remove_object
        Entfernt ein RenderObject

    Args:
        object(RenderObject): Das zu entfernende Objekt
    """
    def remove_object(self, object: RenderObject):
        if object == None:
            return
        self.render_objects.remove(object)
        # pawn
        if type(object) == Pawn or issubclass(type(object), Pawn):
            self.pawns.remove(object)

    """
    [OVERRIDE] update
        Updated alle RenderObjects. Wird FRAMERATE mal pro Sekunde aufgerufen

    Args:
        delta_time(float): Die Zeit, die seit dem letzten Aufruf der Prozedur vergangen ist.
    """
    def update(self, delta_time: float):
        for x in self.render_objects:
            x.update(delta_time)
            
        self.update_pawn_collision(delta_time) # sollte immer als letztes aufgerufen werden
    
    """
    [OVERRIDE] render
        Rendert den GameLayer auf ein Canvas

    Args:
        canvas(Canvas): Das Canvas, auf das gerendert werden soll
    """
    def render(self, canvas: Canvas):
        # View offset
        canvas.set_view_translation(self._view_translation_x, self._view_translation_y)
        # Render
        for x in self.render_objects:
            x: RenderObject = x
            if x.is_visible:
                # shader uniforms
                x.shader.current_z_index = self._z_index
                # render object
                x.draw(canvas)

    """
    update_pawn_collision
        Updated die Kollision der Pawns mit den anderen Objekten im GameLayer und der Landschaft

    Args:
        delta_time(float): Die vergangene Zeit seit dem letzten Aufruf der Prozedur
    """
    def update_pawn_collision(self, delta_time: float):
        for pawn in self.pawns:
            pawn: Pawn = pawn

            # Terrain collision
            surface_height = 0.4 if self.terrain == None else self.terrain.get_surface_height(pawn.position_x)
            # Wenn der Pawn mit dem Terrain kollidiert...
            if pawn.position_y <= surface_height + (pawn.get_bounds().height / 2.0):
                pawn.position_y = surface_height + (pawn.get_bounds().height / 2.0)
                pawn.is_in_air = False
            else:
                pawn.is_in_air = True
                #pawn.reset_velocity_y()

            # Pawn collison
            for other_pawn in self.pawns:
                other_pawn: Pawn = other_pawn
                if other_pawn == pawn:
                    continue
                if check_collision(pawn, other_pawn):
                    pawn.on_pawn_collision(other_pawn)
                

        # TODO: implement collision with other pawns

    # GETTERS / SETTERS

    """
    set_view_translation
        Verschiebt den Ausschnitt (View), der gerendert wird.

    Args:
        x(float): Die Verschiebung auf der X-Achse
        y(float): Die Verschiebung auf der Y-Achse
    """
    def set_view_translation(self, x: float, y: float):
        self._view_translation_x = x
        self._view_translation_y = y
    
    def get_view_translation(self):
        return self._view_translation_x, self._view_translation_y

    def get_z_index(self) -> float:
        return self._z_index
    
    def set_z_index(self, index: float):
        self._z_index = index
