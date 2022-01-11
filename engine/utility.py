from math import sqrt

"""
floatcmp
    Überpüft, ob zwei floats auf eine bestimmte Präzision gerundet identisch sind.

Args:
    a(float): Der erste zu vergleichende float
    b(float): Der zweite zu vergleichende float
    precision(float): Die Präsision, mit der die floats verglichen werden

Returns:
    (bool): 'True', falls die gerundeten floats identisch sind, 'False' andernfalls
"""
def floatcmp(a: float, b: float, precision: float = 0.0001) -> bool:
    return abs(a - b) <= precision

"""
overrides (Decorator)
    Nur da, um overrides mit '@overrides(BaseClass)' kennzeichnen zu können.
    https://stackoverflow.com/questions/1167617/in-python-how-do-i-indicate-im-overriding-a-method
    Wirft einen assert-error, falls die Methode in der BaseClass nicht existiert

Args:
    interface_class(Class): Die Base-Class, deren Methode überschreiben werden soll
"""
def overrides(interface_class):
    def overrider(method):
        assert(method.__name__ in dir(interface_class))
        return method
    return overrider

"""
pure virtual (Decorator)
    Nur da, um eine Funktion als virtuell zu markieren.
    Nur für Dokumentation, hat keine funktionellen Nutzen.
    Mit '@pure_virtual' gekennzeichnete Funktionen besitzen keine Implementation in der Base Class
"""
def pure_virtual(func):
    return func

"""
Bounds Class
    Repräsentiert die Maße eines engine.render_object.RenderObjects
"""
class Bounds:
    def __init__(self, width: float = 0.0, height: float = 0.0, position_x: float = 0.0, position_y: float = 0.0):
        self.width: float = width
        self.height: float = height
        self.position_x: float = position_x
        self.position_y: float = position_y

    @property
    def left(self) -> float:
        return self.position_x - (self.width / 2.0)

    @property
    def right(self) -> float:
        return self.position_x + (self.width / 2.0)

    @property
    def top(self) -> float:
        return self.position_y + (self.height / 2.0)

    @property
    def bottom(self) -> float:
        return self.position_y - (self.height / 2.0)


class TerminalColors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def calculate_points_distance(x0: float, y0: float, x1: float, y1: float) -> float:
    return sqrt((x1-x0)*(x1-x0) + (y1-y0)*(y1-y0))