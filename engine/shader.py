from engine.utility import overrides, pure_virtual

"""
blend_pixel
    Blendet zwischen zwei Pixeln

Args:
    pixel_a(list[3]): Der erste Pixel ([r,g,b])
    pixel_b(list[3]): Der zweite Pixel ([r,g,b])
    opacity_b(float): Die Deckkraft des zweiten Pixels (0.0 - 1.0)

Returns:
    pixel(list[3]): Der geblendete Pixel ([r,g,b])
"""
def blend_pixel(pixel_a: list, pixel_b: list, opacity_b: float):
    pixel: list = [0, 0, 0]
    pixel[0] = (pixel_a[0] * (1.0 - opacity_b)) + (pixel_b[0] * opacity_b)
    pixel[1] = (pixel_a[1] * (1.0 - opacity_b)) + (pixel_b[1] * opacity_b)
    pixel[2] = (pixel_a[2] * (1.0 - opacity_b)) + (pixel_b[2] * opacity_b)
    return pixel

"""
addblend_pixel
    Blendet zwischen zwei Pixeln und schreibt den neuen Pixel in den ersten

Args:
    pixel_a(list[3]): Der erste Pixel ([r,g,b])
    pixel_b(list[3]): Der zweite Pixel ([r,g,b])
    opacity_b(float): Die Deckkraft des zweiten Pixels (0.0 - 1.0)
"""
def addblend_pixel(pixel_a: list, pixel_b: list, opacity_b: float):
    #r, g, b = pixel_a[0], pixel_a[1], pixel_a[2]
    pixel_a[0] = (pixel_a[0] * (1.0 - opacity_b)) + (pixel_b[0] * opacity_b)
    pixel_a[1] = (pixel_a[1] * (1.0 - opacity_b)) + (pixel_b[1] * opacity_b)
    pixel_a[2] = (pixel_a[2] * (1.0 - opacity_b)) + (pixel_b[2] * opacity_b)

"""
GlobalShaderSettings Class
"""
class GlobalShaderSettings:
    light_brightness: float = 1.0
    light_color: list = [255, 255, 255]
    fog_strength: float = 0.05
    fog_night_glow: float = 10.0
    fog_begin_z: float = 1.0
    fog_color: list = [128, 200, 255]
    black_color: list = [24, 52, 100]

"""
PixelShader Class
"""
class PixelShader:
    def __init__(self):
        # uniforms
        self.current_z_index: float = 1.0
        self.needs_bounds_uniforms: bool = False
        self.top_pxl: int = 0
        self.bottom_pxl: int = 0
        self.left_pxl: int = 0
        self.right_pxl: int = 0

    def __getitem__(self, index):
        x, y, color = index
        return self.process_pixel(x, y, color)

    #@pure_virtual
    def process_pixel(self, x: int, y: int, color: list) -> list:
        raise NotImplementedError()


"""
NoShader(PixelShader) Class
"""
class NoShader(PixelShader):

    #@overrides(PixelShader)
    def process_pixel(self, x: int, y: int, color: list) -> list:
        return color

"""
StandardShader(PixelShader) Class
"""
class StandardShader(PixelShader):

    @overrides(PixelShader)
    def process_pixel(self, x: int, y: int, color: list) -> list:
        raw_color: list = []
        if len(color) == 3:
            raw_color = color
        elif len(color) == 4:
            raw_color.append(color[1])
            raw_color.append(color[2])
            raw_color.append(color[3])

        # Sun light
        blended_pixel: list = blend_pixel(GlobalShaderSettings.black_color, raw_color, pow(2.0, GlobalShaderSettings.light_brightness) / 2.0)
        # Fog
        fog_night_glow: float = GlobalShaderSettings.fog_night_glow * max(0.0, (1.0 - GlobalShaderSettings.light_brightness))
        fog_blend: float = max(0.0, min(1.0, GlobalShaderSettings.fog_strength * max(0.0, self.current_z_index - GlobalShaderSettings.fog_begin_z) * fog_night_glow))
        blended_pixel: list = blend_pixel(blended_pixel, GlobalShaderSettings.fog_color, fog_blend)
        #addblend_pixel(blended_pixel, GlobalShaderSettings.fog_color, fog_blend)

        return [color[0], blended_pixel[0], blended_pixel[1], blended_pixel[2]] if len(color) == 4 else blended_pixel

"""
SkyShader(PixelShader) Class
"""
class SkyShader(PixelShader):
    def __init__(self):
        super().__init__()
        self.sunset_sky_color = [255, 100, 0]
        self.night_sky_color = [0, 0, 48]
        self.needs_bounds_uniforms = True
    
    @overrides(PixelShader)
    def process_pixel(self, x: int, y: int, color: list) -> list:
        raw_color: list = []
        if len(color) == 3:
            raw_color = color
        elif len(color) == 4:
            raw_color.append(color[1])
            raw_color.append(color[2])
            raw_color.append(color[3])

        top_color = blend_pixel(self.night_sky_color, blend_pixel(color, [255, 255, 255], GlobalShaderSettings.light_brightness * 0.2), GlobalShaderSettings.light_brightness)

        if GlobalShaderSettings.light_brightness < 0.1:
            bottom_color: list = blend_pixel(self.night_sky_color, self.sunset_sky_color, GlobalShaderSettings.light_brightness / 0.1)
        else:
            bottom_color: list = blend_pixel(self.sunset_sky_color, raw_color, (GlobalShaderSettings.light_brightness - 0.1) / 0.9)

        # Farbverlauf
        blended_pixel = blend_pixel(top_color, bottom_color, y / (self.bottom_pxl - self.top_pxl))

        return blended_pixel


"""
LightShader(PixelShader) Class
"""
class LightShader(PixelShader):
    #@overrides(PixelShader)
    def process_pixel(self, x: int, y: int, color: list) -> list:
        return color
        if (len(color) == 4):
            pixel_brightness: float = (color[1] + color[2] + color[3]) / (255.0 * 3.0)
            color[0] = int(color[0] * pixel_brightness)
        return color