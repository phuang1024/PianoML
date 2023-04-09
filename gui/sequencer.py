import time

import pygame


class Sequencer:
    """
    Draws y = 51 to 500
    Range 0 to 10 seconds
    """

    def __init__(self, buttons, piano):
        self.buttons = buttons
        self.piano = piano

        # List of (note, start, end)
        self.messages = []
        # For recording
        self.pending_messages = {}
        self.pointer = 0
        # This is True in both playing and recording
        self.playing = False
        self.recording = False
        self.record_start_time = 0
        self.record_start_ptr = 0

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
            y = 500 - self.ch_to_y(msg[0])
            start = self.t_to_x(msg[1])
            end = self.t_to_x(msg[2])
            pygame.draw.rect(surface, (60, 255, 60), (start, y, end-start, 6))

        # Play/rec notifier
        if self.playing or self.recording:
            col = (255, 60, 60) if self.recording else (60, 60, 255)
            pygame.draw.circle(surface, col, (20, 70), 10)

        # Update
        # Pointer
        if mouse_press[0] and 51 <= mouse_pos[1] <= 500 and not self.playing:
            self.pointer = mouse_pos[0] / 1280

        # Recording start/stop
        if self.playing:
            if self.buttons.stop.is_clicked(events):
                self.playing = False
                self.recording = False
        else:
            if (rec := self.buttons.record.is_clicked(events)) or self.buttons.play.is_clicked(events):
                if rec:
                    self.recording = True
                    self.pending_messages = {}
                self.playing = True
                self.record_start_time = time.time()
                self.record_start_ptr = self.pointer

        # Set ptr for playing
        if self.playing:
            timestamp = time.time() - self.record_start_time
            pointer = self.record_start_ptr + timestamp / 10
            if pointer > 1:
                self.playing = False
                self.recording = False
                pointer = 1
            self.pointer = pointer

        # Recording
        if self.recording:
            pressed = self.piano.keys_pressed()

            to_del = []
            for k, v in self.pending_messages.items():
                if k not in pressed:
                    self.messages.append((k, v*10, self.pointer*10))
                    to_del.append(k)
            for k in to_del:
                del self.pending_messages[k]

            for p in pressed:
                if p not in self.pending_messages:
                    self.pending_messages[p] = self.pointer
