import pygame

TILE_SIZE = 64
ASSET_PATH = "Assets/"


class GameObject:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.moveable = False
        self.blocks_light = False
        self.blocks_movement = False

    @property
    def rect(self):
        return pygame.Rect(self.x, self.y, TILE_SIZE, TILE_SIZE)


class Mirror(GameObject):
    def __init__(self, x, y, angle=0):
        super().__init__(x, y)
        self.moveable = True
        self.angle = angle
        self.active_surface = 0
        self.img = pygame.transform.scale(
            pygame.image.load(ASSET_PATH + "Mirror.png").convert_alpha(),
            (TILE_SIZE, TILE_SIZE)
        )

    def draw(self, screen):
        rotated = pygame.transform.rotate(self.img, -self.angle)
        rect = rotated.get_rect(center=(self.x + TILE_SIZE // 2, self.y + TILE_SIZE // 2))
        screen.blit(rotated, rect)


class Glass(GameObject):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.moveable = True
        self.blocks_light = False
        self.img = pygame.transform.scale(
            pygame.image.load(ASSET_PATH + "Glass.png").convert_alpha(),
            (TILE_SIZE, TILE_SIZE)
        )

    def draw(self, screen):
        screen.blit(self.img, (self.x, self.y))


class ConvexLens(GameObject):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.broken = False
        self.moveable = True
        self.power_bonus = 2


class ConcaveLens(GameObject):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.broken = False
        self.moveable = True
        self.split_count = 3


class Beam:
    def __init__(self, x, y, direction, strength=12):
        self.x = x
        self.y = y
        self.direction = direction
        self.max_strength = strength
        self.strength = strength

    def draw(self, screen, walls, glass_objects=None, mirrors=None):
        if glass_objects is None:
            glass_objects = []
        if mirrors is None:
            mirrors = []

        # Direction vectors for all 8 directions
        dir_map = {
            "right": (1, 0),
            "left": (-1, 0),
            "up": (0, -1),
            "down": (0, 1),
            "up-right": (1, -1),
            "up-left": (-1, -1),
            "down-right": (1, 1),
            "down-left": (-1, 1)
        }
        if self.direction not in dir_map:
            return []

        dx, dy = dir_map[self.direction]
        current_strength = self.max_strength
        child_beams = []
        boosted_tiles = set()

        # Start from the emitter's tile and draw through its center
        tile_x = self.x
        tile_y = self.y
        steps = 0
        max_steps = 1000

        while current_strength > 0 and steps < max_steps:
            beam_rect = pygame.Rect(tile_x, tile_y, TILE_SIZE, TILE_SIZE)

            # ----- WALL COLLISION -----
            blocked = False
            for wall in walls:
                if beam_rect.colliderect(wall.rect):
                    blocked = True
                    break
            if blocked:
                break

            # ----- MIRROR CHECK -----
            mirror_hit = False
            for mirror in mirrors:
                if beam_rect.colliderect(mirror.rect):
                    new_direction = reflect_direction(self.direction, mirror.angle)
                    # Create child beam at THIS tile's position
                    child_beams.append(Beam(tile_x, tile_y, new_direction, current_strength))
                    mirror_hit = True
                    break
            if mirror_hit:
                break

            # ----- GLASS CHECK (amplify strength) -----
            for glass in glass_objects:
                if beam_rect.colliderect(glass.rect):
                    tile_key = (tile_x, tile_y)
                    if tile_key not in boosted_tiles:
                        current_strength += 1
                        boosted_tiles.add(tile_key)
                    break

            # ----- DRAW SEGMENT -----
            alpha = max(255 - steps * 20, 0)
            
            # Draw beam through the CENTER of each tile
            if dx != 0 and dy != 0:  # diagonal
                # Draw diagonal line through tile center
                center_x = tile_x + TILE_SIZE // 2
                center_y = tile_y + TILE_SIZE // 2
                
                # Calculate line endpoints (corner to corner through center)
                if dx == 1 and dy == -1:  # up-right
                    start_pos = (tile_x, tile_y + TILE_SIZE)
                    end_pos = (tile_x + TILE_SIZE, tile_y)
                elif dx == -1 and dy == -1:  # up-left
                    start_pos = (tile_x + TILE_SIZE, tile_y + TILE_SIZE)
                    end_pos = (tile_x, tile_y)
                elif dx == 1 and dy == 1:  # down-right
                    start_pos = (tile_x, tile_y)
                    end_pos = (tile_x + TILE_SIZE, tile_y + TILE_SIZE)
                elif dx == -1 and dy == 1:  # down-left
                    start_pos = (tile_x + TILE_SIZE, tile_y)
                    end_pos = (tile_x, tile_y + TILE_SIZE)
                
                pygame.draw.line(screen, (180, 0, 255, alpha), start_pos, end_pos, 8)
                
            else:  # cardinal
                # Draw line through the CENTER of the tile
                if dx != 0:  # horizontal
                    pygame.draw.line(screen, (180, 0, 255, alpha),
                                   (tile_x, tile_y + TILE_SIZE // 2),
                                   (tile_x + TILE_SIZE, tile_y + TILE_SIZE // 2), 8)
                else:  # vertical
                    pygame.draw.line(screen, (180, 0, 255, alpha),
                                   (tile_x + TILE_SIZE // 2, tile_y),
                                   (tile_x + TILE_SIZE // 2, tile_y + TILE_SIZE), 8)

            # Move to next tile
            tile_x += dx * TILE_SIZE
            tile_y += dy * TILE_SIZE
            current_strength -= 1
            steps += 1

        return child_beams
    
    def __init__(self, x, y, direction, strength=12):
        self.x = x
        self.y = y
        self.direction = direction
        self.max_strength = strength
        self.strength = strength

    def draw(self, screen, walls, glass_objects=None, mirrors=None):
        if glass_objects is None:
            glass_objects = []
        if mirrors is None:
            mirrors = []

        # Direction vectors for all 8 directions
        dir_map = {
            "right": (1, 0),
            "left": (-1, 0),
            "up": (0, -1),
            "down": (0, 1),
            "up-right": (1, -1),
            "up-left": (-1, -1),
            "down-right": (1, 1),
            "down-left": (-1, 1)
        }
        if self.direction not in dir_map:
            return []

        dx, dy = dir_map[self.direction]
        current_strength = self.max_strength
        child_beams = []
        boosted_tiles = set()

        # Start from center of beam's origin tile
        start_px = self.x + TILE_SIZE // 2
        start_py = self.y + TILE_SIZE // 2
        
        # Current tile coordinates
        tile_x = self.x
        tile_y = self.y
        steps = 0
        max_steps = 1000

        while current_strength > 0 and steps < max_steps:
            beam_rect = pygame.Rect(tile_x, tile_y, TILE_SIZE, TILE_SIZE)

            # ----- WALL COLLISION -----
            blocked = False
            for wall in walls:
                if beam_rect.colliderect(wall.rect):
                    blocked = True
                    break
            if blocked:
                break

            # ----- MIRROR CHECK -----
            mirror_hit = False
            for mirror in mirrors:
                if beam_rect.colliderect(mirror.rect):
                    new_direction = reflect_direction(self.direction, mirror.angle)
                    # Create child beam at THIS tile's position
                    child_beams.append(Beam(tile_x, tile_y, new_direction, current_strength))
                    mirror_hit = True
                    break
            if mirror_hit:
                break

            # ----- GLASS CHECK (amplify strength) -----
            for glass in glass_objects:
                if beam_rect.colliderect(glass.rect):
                    tile_key = (tile_x, tile_y)
                    if tile_key not in boosted_tiles:
                        current_strength += 1
                        boosted_tiles.add(tile_key)
                    break

            # ----- DRAW SEGMENT -----
            # Calculate pixel positions
            current_center_x = tile_x + TILE_SIZE // 2
            current_center_y = tile_y + TILE_SIZE // 2
            
            if steps == 0:
                # First segment: from emitter center to first tile center
                prev_center_x = start_px
                prev_center_y = start_py
            else:
                # From previous tile center to current tile center
                prev_center_x = current_center_x - dx * TILE_SIZE
                prev_center_y = current_center_y - dy * TILE_SIZE
            
            alpha = max(255 - steps * 20, 0)
            # Draw the beam line segment
            pygame.draw.line(screen, (180, 0, 255, alpha),
                           (prev_center_x, prev_center_y),
                           (current_center_x, current_center_y), 8)

            # Move to next tile
            tile_x += dx * TILE_SIZE
            tile_y += dy * TILE_SIZE
            current_strength -= 1
            steps += 1

        return child_beams
    def __init__(self, x, y, direction, strength=12):
        self.x = x
        self.y = y
        self.direction = direction
        self.max_strength = strength
        self.strength = strength

    def draw(self, screen, walls, glass_objects=None, mirrors=None):
        if glass_objects is None:
            glass_objects = []
        if mirrors is None:
            mirrors = []

        # Direction vectors for all 8 directions
        dir_map = {
            "right": (1, 0),
            "left": (-1, 0),
            "up": (0, -1),
            "down": (0, 1),
            "up-right": (1, -1),
            "up-left": (-1, -1),
            "down-right": (1, 1),
            "down-left": (-1, 1)
        }
        if self.direction not in dir_map:
            return []   # unknown direction, skip

        dx, dy = dir_map[self.direction]
        current_strength = self.max_strength
        child_beams = []
        boosted_tiles = set()

        # Start one tile away from emitter (same as original logic)
        tile_x = self.x + dx * TILE_SIZE
        tile_y = self.y + dy * TILE_SIZE
        steps = 0
        max_steps = 1000  # safety limit to prevent infinite loops

        while current_strength > 0 and steps < max_steps:
            beam_rect = pygame.Rect(tile_x, tile_y, TILE_SIZE, TILE_SIZE)

            # ----- WALL COLLISION -----
            blocked = False
            for wall in walls:
                if beam_rect.colliderect(wall.rect):
                    blocked = True
                    break
            if blocked:
                break

            # ----- MIRROR CHECK -----
            mirror_hit = False
            for mirror in mirrors:
                if beam_rect.colliderect(mirror.rect):
                    new_direction = reflect_direction(self.direction, mirror.angle)
                    child_beams.append(Beam(tile_x, tile_y, new_direction, current_strength))
                    mirror_hit = True
                    break
            if mirror_hit:
                break

            # ----- GLASS CHECK (amplify strength) -----
            for glass in glass_objects:
                if beam_rect.colliderect(glass.rect):
                    tile_key = (tile_x, tile_y)
                    if tile_key not in boosted_tiles:
                        current_strength += 1   # glass adds 1 to remaining strength
                        boosted_tiles.add(tile_key)
                    break

            # ----- DRAW SEGMENT -----
            alpha = max(255 - steps * 20, 0)   # fade with distance
            beam_surface = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)

            if dx != 0 and dy != 0:   # diagonal
                if dx == 1 and dy == -1:        # up-right
                    pygame.draw.line(beam_surface, (180, 0, 255, alpha),
                                     (0, TILE_SIZE), (TILE_SIZE, 0), 8)
                elif dx == -1 and dy == -1:     # up-left
                    pygame.draw.line(beam_surface, (180, 0, 255, alpha),
                                     (TILE_SIZE, TILE_SIZE), (0, 0), 8)
                elif dx == 1 and dy == 1:       # down-right
                    pygame.draw.line(beam_surface, (180, 0, 255, alpha),
                                     (0, 0), (TILE_SIZE, TILE_SIZE), 8)
                elif dx == -1 and dy == 1:      # down-left
                    pygame.draw.line(beam_surface, (180, 0, 255, alpha),
                                     (TILE_SIZE, 0), (0, TILE_SIZE), 8)
            else:   # cardinal
                if dx != 0:   # horizontal
                    pygame.draw.line(beam_surface, (180, 0, 255, alpha),
                                     (0, TILE_SIZE // 2), (TILE_SIZE, TILE_SIZE // 2), 8)
                else:         # vertical
                    pygame.draw.line(beam_surface, (180, 0, 255, alpha),
                                     (TILE_SIZE // 2, 0), (TILE_SIZE // 2, TILE_SIZE), 8)

            screen.blit(beam_surface, (tile_x, tile_y))

            # Move to next tile
            tile_x += dx * TILE_SIZE
            tile_y += dy * TILE_SIZE
            current_strength -= 1   # one tile consumes 1 strength
            steps += 1

        return child_beams

class Receiver(GameObject):
    def __init__(self, x, y, receiver_id=0):
        super().__init__(x, y)
        self.moveable = False
        self.powered = False
        self.receiver_id = receiver_id
        self.img = pygame.transform.scale(
            pygame.image.load(ASSET_PATH + "Receiver.png").convert_alpha(),
            (TILE_SIZE, TILE_SIZE)
        )
        # Create a yellow box surface for the powered indicator
        self.powered_box = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        pygame.draw.rect(self.powered_box, (255, 255, 0, 180), self.powered_box.get_rect(), 4)
        
        # Create unpowered indicator
        self.unpowered_box = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        pygame.draw.rect(self.unpowered_box, (100, 100, 100, 100), self.unpowered_box.get_rect(), 2)

    def draw(self, screen):
        screen.blit(self.img, (self.x, self.y))
        if self.powered:
            screen.blit(self.powered_box, (self.x, self.y))
        else:
            screen.blit(self.unpowered_box, (self.x, self.y))


class Emitter(GameObject):
    def __init__(self, x, y, direction="up", emitter_id=0, starts_powered=False):
        super().__init__(x, y)
        self.width = 64
        self.height = 64
        self.direction = direction
        self.moveable = False
        self.powered = starts_powered  # Can be toggled on/off
        self.emitter_id = emitter_id
        self.starts_powered = starts_powered  # Remember initial state
        self.img = pygame.transform.scale(
            pygame.image.load(ASSET_PATH + "Emitter.png").convert_alpha(),
            (64, 64)
        )
        # Create powered/unpowered indicators
        self.powered_overlay = pygame.Surface((64, 64), pygame.SRCALPHA)
        pygame.draw.rect(self.powered_overlay, (0, 255, 0, 100), self.powered_overlay.get_rect(), 3)
        
        self.unpowered_overlay = pygame.Surface((64, 64), pygame.SRCALPHA)
        pygame.draw.rect(self.unpowered_overlay, (100, 100, 100, 100), self.unpowered_overlay.get_rect(), 3)

    def draw(self, screen):
        direction_map = {"right": 1, "down": 2, "left": 3, "up": 0}
        angle = direction_map.get(self.direction, 0) * -90
        rotated = pygame.transform.rotate(self.img, angle)
        screen.blit(rotated, (self.x, self.y))
        
        # Show powered status
        if self.powered:
            screen.blit(self.powered_overlay, (self.x, self.y))
        else:
            screen.blit(self.unpowered_overlay, (self.x, self.y))

    @property
    def center(self):
        return (self.x + self.width // 2, self.y + self.height // 2)


class Door(GameObject):
    def __init__(self, x, y, locked=True):
        super().__init__(x, y)
        self.locked = locked


class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 64
        self.height = 64
        self.speed = 4
        self.vx = 0
        self.vy = 0

        asset_path = ASSET_PATH
        self.frames = [
            pygame.transform.scale(pygame.image.load(asset_path + "Player1.png").convert_alpha(), (64, 64)),
            pygame.transform.scale(pygame.image.load(asset_path + "Player2.png").convert_alpha(), (64, 64)),
            pygame.transform.scale(pygame.image.load(asset_path + "Player3.png").convert_alpha(), (64, 64)),
            pygame.transform.scale(pygame.image.load(asset_path + "Player4.png").convert_alpha(), (64, 64)),
            pygame.transform.scale(pygame.image.load(asset_path + "Player3.png").convert_alpha(), (64, 64)),
            pygame.transform.scale(pygame.image.load(asset_path + "Player2.png").convert_alpha(), (64, 64)),
        ]
        self.frame_index = 0
        self.animation_timer = 0
        self.animation_speed = 8

    @property
    def rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def update(self, walls=None, mirrors=None, glasses=None, emitters=None, receivers=None):
        """Update player position with collision detection"""
        if walls is None:
            walls = []
        if mirrors is None:
            mirrors = []
        if glasses is None:
            glasses = []
        if emitters is None:
            emitters = []
        if receivers is None:
            receivers = []
        
        keys = pygame.key.get_pressed()
        self.vx = 0
        self.vy = 0

        if keys[pygame.K_a]:
            self.vx = -self.speed
        if keys[pygame.K_d]:
            self.vx = self.speed
        if keys[pygame.K_w]:
            self.vy = -self.speed
        if keys[pygame.K_s]:
            self.vy = self.speed

        # Try moving horizontally
        new_x = self.x + self.vx
        player_rect_x = pygame.Rect(new_x, self.y, self.width, self.height)
        
        can_move_x = True
        # Check walls
        for wall in walls:
            if wall.blocks_movement and player_rect_x.colliderect(wall.rect):
                can_move_x = False
                break
        
        # Check mirrors (only if they block movement)
        if can_move_x:
            for mirror in mirrors:
                if mirror.blocks_movement and player_rect_x.colliderect(mirror.rect):
                    can_move_x = False
                    break
        
        # Check glasses
        if can_move_x:
            for glass in glasses:
                if glass.blocks_movement and player_rect_x.colliderect(glass.rect):
                    can_move_x = False
                    break
        
        # Check emitters
        if can_move_x:
            for emitter in emitters:
                if emitter.blocks_movement and player_rect_x.colliderect(emitter.rect):
                    can_move_x = False
                    break
        
        # Check receivers
        if can_move_x:
            for receiver in receivers:
                if receiver.blocks_movement and player_rect_x.colliderect(receiver.rect):
                    can_move_x = False
                    break
        
        if can_move_x:
            self.x = new_x

        # Try moving vertically
        new_y = self.y + self.vy
        player_rect_y = pygame.Rect(self.x, new_y, self.width, self.height)
        
        can_move_y = True
        # Check walls
        for wall in walls:
            if wall.blocks_movement and player_rect_y.colliderect(wall.rect):
                can_move_y = False
                break
        
        # Check mirrors
        if can_move_y:
            for mirror in mirrors:
                if mirror.blocks_movement and player_rect_y.colliderect(mirror.rect):
                    can_move_y = False
                    break
        
        # Check glasses
        if can_move_y:
            for glass in glasses:
                if glass.blocks_movement and player_rect_y.colliderect(glass.rect):
                    can_move_y = False
                    break
        
        # Check emitters
        if can_move_y:
            for emitter in emitters:
                if emitter.blocks_movement and player_rect_y.colliderect(emitter.rect):
                    can_move_y = False
                    break
        
        # Check receivers
        if can_move_y:
            for receiver in receivers:
                if receiver.blocks_movement and player_rect_y.colliderect(receiver.rect):
                    can_move_y = False
                    break
        
        if can_move_y:
            self.y = new_y

        # Animation
        if self.vx != 0 or self.vy != 0:
            self.animation_timer += 1
            if self.animation_timer >= self.animation_speed:
                self.animation_timer = 0
                self.frame_index = (self.frame_index + 1) % len(self.frames)
        else:
            self.frame_index = 0

    def draw(self, screen):
        screen.blit(self.frames[self.frame_index], (self.x, self.y))


class Room:
    def __init__(self, width=10, height=10):
        self.objects = []
        self.emitters = []
        self.receivers = []
        self.doors = []
        self.floors = []

        for y in range(height):
            for x in range(width):
                self.floors.append(Floor(x * TILE_SIZE, y * TILE_SIZE))


class Floor(GameObject):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.img = pygame.transform.scale(
            pygame.image.load(ASSET_PATH + "Floor.png").convert_alpha(),
            (TILE_SIZE, TILE_SIZE)
        )

    def draw(self, screen):
        screen.blit(self.img, (self.x, self.y))


class Wall(GameObject):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.blocks_light = True
        self.blocks_movement = True
        self.img = pygame.transform.scale(
            pygame.image.load(ASSET_PATH + "Wall.png").convert_alpha(),
            (TILE_SIZE, TILE_SIZE)
        )

    def draw(self, screen):
        screen.blit(self.img, (self.x, self.y))


def object_near_player(player, obj):
    distance = abs(player.x - obj.x) + abs(player.y - obj.y)
    return distance <= TILE_SIZE + 16


def move_object(player, obj, walls):
    if not obj.moveable:
        return

    dx = obj.x - player.x
    dy = obj.y - player.y
    move_x = 0
    move_y = 0

    if abs(dx) > abs(dy):
        move_x = TILE_SIZE if dx > 0 else -TILE_SIZE
    else:
        move_y = TILE_SIZE if dy > 0 else -TILE_SIZE

    new_x = obj.x + move_x
    new_y = obj.y + move_y

    for wall in walls:
        if wall.x == new_x and wall.y == new_y:
            return

    obj.x = new_x
    obj.y = new_y


import math

def reflect_direction(direction, mirror_angle):
    """
    Reflect beam based on mirror rotation.
    Supports all 8 directions and returns a valid direction string.
    """
    # Normalise mirror angle (orientation repeats every 180°)
    angle = mirror_angle % 180

    # ---- retro-reflection (back to source) ----
    retro = {
        "right": "left",   "left": "right",
        "up": "down",      "down": "up",
        "up-right": "down-left",   "down-left": "up-right",
        "up-left": "down-right",   "down-right": "up-left",
    }

    # ---- mirror at ~45° (y = -x) : 90° turn one way ----
    turn_a = {
        "right": "up",     "left": "down",
        "up": "right",     "down": "left",
        "up-right": "down-left",   "down-left": "up-right",
        "up-left": "down-right",   "down-right": "up-left",
    }

    # ---- mirror at ~135° (y = x) : 90° turn the other way ----
    turn_b = {
        "right": "down",   "left": "up",
        "up": "left",      "down": "right",
        "up-right": "down-left",   "down-left": "up-right",
        "up-left": "down-right",   "down-right": "up-left",
    }

    # Choose mapping based on angle range
    if 30 <= angle <= 60:
        return turn_a.get(direction, direction)
    elif 120 <= angle <= 150:
        return turn_b.get(direction, direction)
    else:
        return retro.get(direction, direction)
def check_receiver_powered(receiver, beams, walls, glasses, mirrors):
    """
    Check if any beam hits this receiver.
    Returns True if the receiver is powered.
    """
    for beam in beams:
        if beam_hits_receiver(beam, receiver, walls, glasses, mirrors):
            return True
    return False


def beam_hits_receiver(beam, receiver, walls, glasses, mirrors, depth=0):
    """
    Recursively check if a beam (or its reflections) hits a receiver.
    """
    if depth > 10:  # Safety limit
        return False
    
    # Direction mapping
    dir_map = {
        "right": (1, 0),
        "left": (-1, 0),
        "up": (0, -1),
        "down": (0, 1),
        "up-right": (1, -1),
        "up-left": (-1, -1),
        "down-right": (1, 1),
        "down-left": (-1, 1)
    }
    if beam.direction not in dir_map:
        return False
    
    dx, dy = dir_map[beam.direction]
    current_strength = beam.strength if hasattr(beam, 'strength') else beam.max_strength
    boosted_tiles = set()
    
    tile_x = beam.x + dx * TILE_SIZE
    tile_y = beam.y + dy * TILE_SIZE
    steps = 0
    
    while current_strength > 0 and steps < 100:
        beam_rect = pygame.Rect(tile_x, tile_y, TILE_SIZE, TILE_SIZE)
        
        # Check if this tile hits the receiver
        if beam_rect.colliderect(receiver.rect):
            return True
        
        # Wall collision
        blocked = False
        for wall in walls:
            if beam_rect.colliderect(wall.rect):
                blocked = True
                break
        if blocked:
            break
        
        # Mirror check - create child beams and check them
        for mirror in mirrors:
            if beam_rect.colliderect(mirror.rect):
                new_direction = reflect_direction(beam.direction, mirror.angle)
                child_beam = Beam(tile_x, tile_y, new_direction, current_strength)
                if beam_hits_receiver(child_beam, receiver, walls, glasses, mirrors, depth + 1):
                    return True
                return False  # Beam stops at mirror
        
        # Glass check (boost strength)
        for glass in glasses:
            if beam_rect.colliderect(glass.rect):
                tile_key = (tile_x, tile_y)
                if tile_key not in boosted_tiles:
                    current_strength += 1
                    boosted_tiles.add(tile_key)
                break
        
        tile_x += dx * TILE_SIZE
        tile_y += dy * TILE_SIZE
        current_strength -= 1
        steps += 1
    
    return False

def pull_object(player, obj, walls):
        """Pull an object toward the player (opposite of push)"""
        if not obj.moveable:
            return

        dx = obj.x - player.x
        dy = obj.y - player.y
        move_x = 0
        move_y = 0

        # Pull toward player (reverse of push direction)
        if abs(dx) > abs(dy):
            move_x = -TILE_SIZE if dx > 0 else TILE_SIZE
        else:
            move_y = -TILE_SIZE if dy > 0 else TILE_SIZE

        new_x = obj.x + move_x
        new_y = obj.y + move_y

        # Check if new position overlaps any wall
        for wall in walls:
            if wall.x == new_x and wall.y == new_y:
                return

        # Check bounds
        if new_x < 0 or new_y < 0:
            return

        obj.x = new_x
        obj.y = new_y

def find_connected_emitter(receiver, emitters):
    """
    Find an emitter that's adjacent (within 1 tile) to this receiver.
    Returns the emitter if found, None otherwise.
    """
    receiver_rect = receiver.rect
    
    for emitter in emitters:
        # Skip emitters that start powered (they're always on)
        if emitter.starts_powered:
            continue
            
        # Check if emitter is adjacent (1 tile away in any direction)
        emitter_rect = emitter.rect
        
        # Check if emitter is within 1 tile distance
        dx = abs(receiver_rect.centerx - emitter_rect.centerx)
        dy = abs(receiver_rect.centery - emitter_rect.centery)
        
        # Adjacent if within TILE_SIZE in one direction and aligned in the other
        if (dx <= TILE_SIZE * 1.5 and dy <= TILE_SIZE * 0.5) or \
           (dy <= TILE_SIZE * 1.5 and dx <= TILE_SIZE * 0.5):
            return emitter
    
    return None


def update_emitter_power(emitters, receivers, beams, walls, glasses, mirrors):
    """
    Update which emitters are powered based on receiver states.
    Returns list of beams that should be active.
    """
    # First, check which receivers are powered
    for receiver in receivers:
        receiver.powered = check_receiver_powered(receiver, beams, walls, glasses, mirrors)
    
    # Then, update emitters based on their connected receivers
    for emitter in emitters:
        if emitter.starts_powered:
            # Default-on emitters stay on
            emitter.powered = True
        else:
            # Check if any connected receiver is powered
            emitter.powered = False
            for receiver in receivers:
                if receiver.powered:
                    connected_emitter = find_connected_emitter(receiver, emitters)
                    if connected_emitter == emitter:
                        emitter.powered = True
                        break
    
    # Create/update beams for powered emitters
    active_beams = []
    for emitter in emitters:
        if emitter.powered:
            # Find existing beam or create new one
            beam = Beam(
                (emitter.x // TILE_SIZE) * TILE_SIZE,
                (emitter.y // TILE_SIZE) * TILE_SIZE,
                emitter.direction,
                strength=12
            )
            active_beams.append(beam)
    
    return active_beams