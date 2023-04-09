import pygame


class Piano:
    """
    0 is lowest note on piano
    """

    key_mapping = "awsedftgyhujkolp;'"

    def __init__(self):
        self.octave = 4

    @staticmethod
    def is_white(key):
        return (key % 12) not in (1, 4, 6, 9, 11)

    def keys_pressed(self):
        keys = pygame.key.get_pressed()
        pressed = set()
        for i, key in enumerate(self.key_mapping):
            if keys[ord(key)]:
                key = i + self.octave*12 - 9
                if 0 <= key < 88:
                    pressed.add(key)
        return pressed

    def update(self, surface, events):
        pressed = self.keys_pressed()

        # Draw
        white_width = 1280 / 52
        num_white = 0
        for i in range(88):
            if self.is_white(i):
                x = int(num_white * white_width)
                num_white += 1
                col = 255 if i in pressed else 180
                pygame.draw.rect(surface, (col, col, col), (x, 501, int(white_width - 2), 216))

        num_white = 0
        for i in range(88):
            if self.is_white(i):
                num_white += 1
            else:
                x = int((num_white-0.5) * white_width)
                col = 100 if i in pressed else 50
                pygame.draw.rect(surface, (col, col, col), (x+4, 501, int(white_width-9), 140))

        # Update
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_z:
                    self.octave -= 1
                elif event.key == pygame.K_x:
                    self.octave += 1
        self.octave = max(0, min(8, self.octave))
