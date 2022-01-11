from dataclasses import dataclass

@dataclass
class std_font:
    capital_letters_only: bool = True
    chars = {
        # Zahlen
        # 5
        53: [
            [[0.1, 1.0], [0.9, 1.0]],
            [[0.1, 1.0], [0.1, 0.5]],
            [[0.1, 0.0], [1.2, -0.2], [1.2, 0.7], [0.1, 0.5]]
        ],


        # Leerzeichen
        32 : [],
#       # Punkt
        46 : [
            [[0.5, 0.0]]
        ],
        # Ausrufezeichen
        33 : [
            [[0.5, 0.3], [0.5, 1.0]],
            [[0.5, 0.0]]
        ],
        # Komma
        46 : [
            [[0.4, 0.1], [0.5, 0.0]]
        ],
        # Semikolon
        59 : [
            [[0.4, 0.1], [0.5, 0.0]],
            [[0.5, 0.5]]
        ],

        # Großbuchstaben
        # A
        65 : [
            [[0.0, 0.0], [0.5, 1.0]],       # Schräger Strich links
            [[0.5, 1.0], [1.0, 0.0]],       # Schräger Strich rechts
            [[0.25, 0.45], [0.75, 0.45]]    # Querstrich
        ],
        # B
        66: [
            [[0.1, 0.0], [0.1, 1.0]],                           # Senkrechter Strich
            [[0.1, 0.0], [1.2, -0.2], [1.2, 0.7], [0.1, 0.5]],  # Unterer Bogen
            [[0.1, 0.5], [1.2, 0.5], [1.0, 1.0], [0.1, 1.0]]    # Oberer Bogen
        ],
        # C
        67: [
            [[0.9, 0.0], [-0.2, -0.2], [-0.2, 1.2], [0.9, 1.0]]   # Bogen
        ],
        # D
        68 : [
            [[0.1, 0.0], [0.1, 1.0]],                           # Senkrechter Strich
            [[0.1, 0.0], [1.2, -0.2], [1.2, 1.2], [0.1, 1.0]]   # Bogen
        ],
        # E
        69 : [
            [[0.1, 0.0], [0.1, 1.0]],   # Senkrechter Strich
            [[0.1, 0.0], [0.9, 0.0]],   # Querstrich unten
            [[0.1, 1.0], [0.9, 1.0]],   # Querstrich oben
            [[0.1, 0.5], [0.7, 0.5]],   # Querstrich mitte
            # Serife:
            [[0.9, 0.0], [0.9, 0.1]],
            [[0.9, 1.0], [0.9, 0.9]],
            [[0.7, 0.4], [0.7, 0.6]]
        ],
        # F
        70 : [
            [[0.1, 0.0], [0.1, 1.0]],   # Senkrechter Strich
            [[0.1, 1.0], [0.9, 1.0]],   # Querstrich oben
            [[0.1, 0.5], [0.7, 0.5]]    # Querstrich mitte
        ],
        # G
        71 : [
            [[0.9, 0.0], [-0.2, -0.2], [-0.2, 1.2], [0.9, 1.0]],   # Bogen
            [[0.9, 0.0], [0.9, 0.45]],
            [[0.9, 0.45], [0.45, 0.45]]
        ],
        # H
        72 : [
            [[0.1, 0.0], [0.1, 1.0]],   # Semkrecht links
            [[0.9, 0.0], [0.9, 1.0]],   # Senkrecht rechts
            [[0.1, 0.5], [0.9, 0.5]]    # Wagerechte mittellinie
        ],
        # I
        73 : [
            [[0.5, 0.0], [0.5, 1.0]],   # Senkrechter Strich
            [[0.4, 0.0], [0.6, 0.0]],   # Serif unten
            [[0.4, 1.0], [0.6, 1.0]]    # Serif oben
        ],
        # J
        74 : [
            [[0.7, 0.3], [0.7, 1.0]],   # Senkrechter Strich, nicht ganz bis nach unten wegen Bogen
            [[0.3, 1.0], [0.7, 1.0]],   # Serif Oben
            [[0.7, 0.3], [0.7, -0.1], [0.3, -0.1], [0.3, 0.3]]   # Bogen Unten
        ],
        # K
        75 : [
            [[0.1, 0.0], [0.1, 1.0]],   # Senkrechter Strich
            [[0.1, 0.5], [0.9, 1.0]],   # Diagonal nach oben
            [[0.1, 0.5], [0.9, 0.0]]    # Diagonal nach unten
        ],
        # L
        76 : [
            [[0.1, 0.0], [0.1, 1.0]],   # Senkrechter Strich
            [[0.1, 0.0], [0.9, 0.0]]    # Wagrechter Strich unten
        ],
        # M
        77 : [ 
            [[0.1, 0.0], [0.1, 1.0]],   # Senkrechter Strich Links
            [[0.1, 1.0], [0.5, 0.0]],   # Diagonal nach unten
            [[0.5, 0.0], [0.9, 1.0]],   # Diagonal nach oben
            [[0.9, 0.0], [0.9, 1.0]]    # Senkrechter Strich Rechts
        ],
        # N
        78: [ 
            [[0.1, 0.0], [0.1, 1.0]],   # Senkrechter Strich Links
            [[0.1, 1.0], [0.9, 0.0]],   # Diagonal nach unten
            [[0.9, 0.0], [0.9, 1.0]]    # Senkrechter Strich Rechts
        ],
        # O
        79 : [
            [[0.5, 0.0], [-0.2, -0.2], [-0.2, 1.2], [0.5, 1.0]],  # Bogen Links
            [[0.5, 0.0], [1.2, -0.2], [1.2, 1.2], [0.5, 1.0]]   # Bogen Rechts
        ],
        # P
        80 : [ 
            [[0.1, 0.0], [0.1, 1.0]],   # Senkrechter Strich
            [[0.1, 0.5], [1.2, 0.3], [1.2, 1,2], [0.1, 1.0]]    # Bogen
        ],
        # Q
        81 : [ 
            [[0.5, 0.0], [-0.2, -0.2], [-0.2, 1.2], [0.5, 1.0]],  # Bogen Links
            [[0.5, 0.0], [1.2, -0.2], [1.2, 1.2], [0.5, 1.0]],   # Bogen Rechts
            [[0.6, 0.4], [1.0, 0.0]]
        ],
        # R
        82 : [ 
            [[0.1, 0.0], [0.1, 1.0]],   # Senkrechter Strich
            [[0.1, 0.5], [1.2, 0.3], [1.2, 1,2], [0.1, 1.0]],    # Bogen
            [[0.1, 0.5], [0.9, 0.0]]    # Diagonal nach unten
        ],
        # S
        83 : [ 
            #[[0.9, 1.0], [-0.2, 1.2], [-0.2, 0.7], [0.1, 0.5]], # Oberer Bogen
            [[0.1, 0.5], [-0.2, 0.7], [-0.2, 1.2], [0.9, 1.0]], # Oberer Bogen
            [[0.1, 0.0], [1.2, -0.2], [1.2, 0.7], [0.1, 0.5]]   # Unterer Bogen
        ],
        # T
        84 : [ 
            [[0.5, 0.0], [0.5, 1.0]],   # Senkrechter Strich
            [[0.1, 1.0], [0.9, 1.0]],   # Querstrich
            [[0.1, 1.0], [0.1, 0.9]],   # Serif links
            [[0.9, 1.0], [0.9, 0.9]]    # Serif rechts
        ],
        # U
        85 : [
            [[0.1, 0.3], [0.1, 1.0]],   # Senkrechter Strich Links
            [[0.1, 0.3], [0.1, 0.0], [0.9, 0.0], [0.9, 0.3]],   # Bogen
            [[0.9, 0.3], [0.9, 1.0]]    # Senkrechtre Strich Rechts
        ],
        # V
        86 : [
            [[0.1, 1.0], [0.5, 0.0]],
            [[0.5, 0.0], [0.9, 1.0]]
        ],
        # W
        87 : [
            [[0.1, 1.0], [0.25, 0.0]],
            [[0.25, 0.0], [0.5, 0.8]],
            [[0.5, 0.8], [0.75, 0.0]],
            [[0.75, 0.0], [0.9, 1.0]]
        ],
        # X
        88 : [
            [[0.1, 1.0], [0.9, 0.0]],
            [[0.1, 0.0], [0.9, 1.0]],
            # Serife:
            [[0.0, 0.0], [0.2, 0.0]],
            [[0.8, 0.0], [1.0, 0.0]],
            [[0.0, 1.0], [0.2, 1.0]],
            [[0.8, 1.0], [1.0, 1.0]]
        ],
        # Y
        89: [
            [[0.1, 1.0], [0.5, 0.5]],
            [[0.1, 0.0], [0.9, 1.0]],
            # Serife:
            [[0.0, 0.0], [0.2, 0.0]],
            [[0.0, 1.0], [0.2, 1.0]],
            [[0.8, 1.0], [1.0, 1.0]]
        ],
        # Z
        90 : [ 
            [[0.1, 1.0], [0.9, 1.0]],
            [[0.9, 1.0], [0.1, 0.0]],
            [[0.1, 0.0], [0.9, 0.0]],
            # Serife:
            [[0.1, 1.0], [0.1, 0.9]],
            [[0.9, 0.0], [0.9, 0.1]]
        ],


        # Kleinbuchstaben
        # b
        98: [
            [[0.1, 0.0], [0.1, 1.0]],
            [[0.1, 0.0], [1.2, -0.2], [1.2, 0.7], [0.1, 0.5]]
        ]
    }
