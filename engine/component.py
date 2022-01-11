from engine.render_object import Pawn, RenderObject

M = 400.0

class Component:
    def __init__(self):
        pass

    def update(self, delta_time: float):
        raise NotImplementedError()


class PhysicsCompoment(Component):
    _acceleration: float = 3.5 * M
    _drag: float = 0.87
    _gravity: float = 4.0 * M
    _max_falling_speed: float = 15.0 * M

    
    def __init__(self, parent: Pawn):
        self.parent = parent

    def update(self, delta_time: float):
        # Gravity
        self.parent.velocity_y += 50.0 * self._gravity * delta_time