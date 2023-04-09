import pygame

FONT = pygame.font.SysFont("Arial", 24)


class TextButton:
    def __init__(self, x, y, text):
        self.text = FONT.render(text, True, (180, 180, 180))
        self.rect = (x - self.text.get_width()//2, y - self.text.get_height()//2)
        self.pos = (x, y)

    def is_hovered(self):
        mouse_pos = pygame.mouse.get_pos()
        return self.rect[0] < mouse_pos[0] < self.rect[0] + self.text.get_width() and \
               self.rect[1] < mouse_pos[1] < self.rect[1] + self.text.get_height()

    def is_clicked(self, events):
        mouse_pos = pygame.mouse.get_pos()
        if self.is_hovered():
            for event in events:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    return True
        return False

    def draw(self, surface, events):
        if self.is_hovered() or self.is_clicked(events):
            col = 80 if self.is_clicked(events) else 40
            border = 8
            pygame.draw.rect(surface, (col, col, col), (
                self.pos[0]-self.text.get_width()//2 - border,
                self.pos[1]-self.text.get_height()//2 - border,
                self.text.get_width() + 2*border,
                self.text.get_height() + 2*border
            ), border_radius=10)
        surface.blit(self.text, self.rect)


class Buttons:
    def __init__(self):
        self.play = TextButton(213, 25, "Play")
        self.record = TextButton(427, 25, "Record")
        self.stop = TextButton(640, 25, "Stop")
        self.complete = TextButton(853, 25, "Autocomplete")
        self.clear = TextButton(1067, 25, "Clear")

    def update(self, surface, events):
        self.play.draw(surface, events)
        self.record.draw(surface, events)
        self.stop.draw(surface, events)
        self.complete.draw(surface, events)
        self.clear.draw(surface, events)
