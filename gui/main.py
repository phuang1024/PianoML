import time

import pygame
pygame.init()

from buttons import Buttons
from piano import Piano
from sequencer import Sequencer


def main():
    buttons = Buttons()
    piano = Piano()
    sequencer = Sequencer()

    surface = pygame.display.set_mode((1280, 720))
    pygame.display.set_caption("Piano ML")
    run = True
    while run:
        time.sleep(1 / 60)
        pygame.display.update()
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                run = False

        surface.fill((0, 0, 0))
        buttons.update(surface, events)
        piano.update(surface, events)
        sequencer.update(surface, events)

        # Area separators
        pygame.draw.line(surface, (150, 150, 150), (0, 50), (1280, 50), 3)
        pygame.draw.line(surface, (150, 150, 150), (0, 500), (1280, 500), 3)


if __name__ == "__main__":
    main()
