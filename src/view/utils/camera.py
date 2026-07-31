class Camera:
    """
    Gère le zoom, le pan et la projection monde → écran.
    Ne dépend d'aucune autre classe.
    """

    def __init__(self, zoom_min=0.15, zoom_max=5.0):
        self.zoom = 1.0
        self.pan_x = 0.0
        self.pan_y = 0.0

        self.zoom_min = zoom_min
        self.zoom_max = zoom_max

        # Pour le drag
        self._drag_start = None

    # ───────────────────────────────────────────────
    # Projection monde → écran
    # ───────────────────────────────────────────────
    def world_to_screen(self, world_x, world_y, screen_w, screen_h):
        """
        Convertit des coordonnées monde en coordonnées écran (pixels).

        Le pipeline est :
            1. On applique le zoom → agrandit/réduit le monde.
            2. On ajoute le pan → déplacement manuel de la caméra.
            3. On recentre le monde sur le milieu de l'écran.

        Formule :
            screen_x = world_x * zoom + (screen_w / 2) + pan_x
            screen_y = world_y * zoom + (screen_h / 2) + pan_y
        """
        screen_x = world_x * self.zoom + screen_w / 2 + self.pan_x
        screen_y = world_y * self.zoom + screen_h / 2 + self.pan_y
        return int(screen_x), int(screen_y)

    def screen_to_world(self, screen_x, screen_y, screen_w, screen_h):
        """
        Convertit des pixels écran en coordonnées monde.

        Utile pour :
            - zoom centré sur la souris
            - sélectionner un hub avec la souris
            - calculer des trajectoires dans le monde

        Pipeline inverse :
            1. On enlève le centrage écran.
            2. On enlève le pan.
            3. On divise par le zoom.

        Formule :
            world_x = (screen_x - screen_w/2 - pan_x) / zoom
            world_y = (screen_y - screen_h/2 - pan_y) / zoom
        """
        world_x = (screen_x - screen_w / 2 - self.pan_x) / self.zoom
        world_y = (screen_y - screen_h / 2 - self.pan_y) / self.zoom
        return world_x, world_y

    # ───────────────────────────────────────────────
    # Zoom centré sur la souris
    # ───────────────────────────────────────────────
    def apply_zoom(self, mouse_x, mouse_y, screen_w, screen_h, factor):
        """
        Applique un zoom centré sur la souris.
        factor > 1 : zoom avant
        factor < 1 : zoom arrière
        """

        # Position monde avant zoom
        world_x, world_y = self.screen_to_world(mouse_x, mouse_y,
                                                screen_w, screen_h)

        # Appliquer le zoom
        new_zoom = self.zoom * factor
        new_zoom = max(self.zoom_min, min(self.zoom_max, new_zoom))

        # Recalcul du pan pour garder le point monde sous la souris
        self.pan_x = mouse_x - screen_w / 2 - world_x * new_zoom
        self.pan_y = mouse_y - screen_h / 2 - world_y * new_zoom

        self.zoom = new_zoom

    # ───────────────────────────────────────────────
    # Pan (drag)
    # ───────────────────────────────────────────────
    def start_drag(self, mouse_x, mouse_y):
        self._drag_start = (mouse_x, mouse_y, self.pan_x, self.pan_y)

    def drag(self, mouse_x, mouse_y):
        if not self._drag_start:
            return

        sx, sy, pan_start_x, pan_start_y = self._drag_start
        self.pan_x = pan_start_x + (mouse_x - sx)
        self.pan_y = pan_start_y + (mouse_y - sy)

    def end_drag(self):
        self._drag_start = None

    # ───────────────────────────────────────────────
    # Reset
    # ───────────────────────────────────────────────
    def reset(self):
        self.zoom = 1.0
        self.pan_x = 0.0
        self.pan_y = 0.0
