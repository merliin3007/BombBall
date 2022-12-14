from engine.render_object import Pawn


"""
check_collision
    Gibt 'Wahr' zurück, falls eine Kollision vorliegt.

Args:
    pawn_a(Pawn): Der erste Pawn
    pawn_b(Pawn): Der zweite Pawn

Returns:
    (bool): 'Wahr', falls eine Kollision vorliegt, 'Falsch' andernfalls
"""
def check_collision(pawn_a: Pawn, pawn_b: Pawn) -> bool:
    # TODO: differenciate between box-box, box-circle, circle-circle... collision
    return check_box_collion(pawn_a, pawn_b)

"""
check_box_collision
    Gibt 'Wahr' zurück, falls eine Box-zu-Box Kollision vorliegt.

Args:
    pawn_a(Pawn): Der erste Pawn
    pawn_b(Pawn): Der zweite Pawn

Returns:
    (bool): 'Wahr', falls eine Kollision vorliegt, 'Falsch' andernfalls
"""
def check_box_collion(pawn_a: Pawn, pawn_b: Pawn) -> bool:
    # x-achsen Kollision
    collision_x: bool = pawn_a.get_bounds().right >= pawn_b.get_bounds().left
    collision_x = collision_x and pawn_b.get_bounds().right >= pawn_a.get_bounds().left
    # y-achsen Kollision
    collision_y: bool = pawn_a.get_bounds().top >= pawn_b.get_bounds().bottom
    collision_y = collision_y and pawn_b.get_bounds().top >= pawn_a.get_bounds().bottom
    # Kollision anzeigen, wenn beide Axen überlappen
    return collision_x and collision_y