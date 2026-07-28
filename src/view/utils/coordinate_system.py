class CoordinateSystem:
    """
    Gère la transformation des coordonnées logiques (x, y)
    en coordonnées monde centrées autour de (0, 0).
    """

    def __init__(self, cell_size: int = 400):
        self.cell_size = cell_size
        self.world_positions = {}  # {zone_name: (world_x, world_y)}

    def compute(self, zones):
        """
        Calcule les coordonnées monde de chaque zone.
        zones : iterable d'objets ayant .name, .x, .y
        """
        zones = list(zones)
        if not zones:
            return {}

        # Calcul du centre géométrique
        min_x = min(z.x for z in zones)
        max_x = max(z.x for z in zones)
        min_y = min(z.y for z in zones)
        max_y = max(z.y for z in zones)

        center_x = (min_x + max_x) / 2
        center_y = (min_y + max_y) / 2

        # Transformation en coordonnées monde
        self.world_positions = {
            z.name: (
                (z.x - center_x) * self.cell_size,
                (z.y - center_y) * self.cell_size,
            )
            for z in zones
        }

        return self.world_positions

    def get(self, zone_name):
        """Retourne la position monde d'un hub."""
        return self.world_positions.get(zone_name)
