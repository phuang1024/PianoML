import pygame


class Sequencer:
    """
    Draws y = 51 to 500
    Range 0 to 10 seconds
    """

    def __init__(self):
        # List of (note, start, end)
        self.messages = []
        self.pointer = 0

    @staticmethod
    def ch_to_y(ch):
        return int(ch / 88 * 450 + 51)

    @staticmethod
    def t_to_x(t):
        return int(t / 10 * 1280)

    def update(self, surface, events):
        mouse_pos = pygame.mouse.get_pos()
        mouse_press = pygame.mouse.get_pressed()
        key_press = pygame.key.get_pressed()

        # Draw
        # Pointer
        x = int(1280 * self.pointer)
        pygame.draw.line(surface, (255, 60, 60), (x, 51), (x, 500), 2)

        # Gridlines
        for ch in range(3, 89, 12):
            y = self.ch_to_y(ch)
            pygame.draw.line(surface, (100, 100, 100), (0, y), (1280, y), 1)
        for t in range(11):
            x = self.t_to_x(t)
            pygame.draw.line(surface, (100, 100, 100), (x, 51), (x, 500), 1)

        # Messages
        for msg in self.messages:
            y = self.ch_to_y(msg[0])
            start = self.t_to_x(msg[1])
            end = self.t_to_x(msg[2])
            pygame.draw.rect(surface, (60, 255, 60), (x, y, end-start, 6))

        # Update
        # Pointer
        if mouse_press[0]:
            self.pointer = mouse_pos[0] / 1280
