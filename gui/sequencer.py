import os
import sys
import time
from subprocess import run

import pygame

ROOT = os.path.dirname(os.path.abspath(__file__))

AUDIO = [pygame.mixer.Sound(os.path.join(ROOT, "audio", f"{i}.mp3")) for i in range(88)]


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
        # Initialized when starting playing/recording
        self.audio_played = []
        self.pointer = 0
        # This is True in both playing and recording
        self.playing = False
        self.recording = False
        self.play_start_time = 0
        self.play_start_ptr = 0

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
                pygame.mixer.music.stop()
        else:
            if (rec := self.buttons.record.is_clicked(events)) or self.buttons.play.is_clicked(events):
                if rec:
                    self.recording = True
                    self.pending_messages = {}
                self.playing = True
                self.play_start_time = time.time()
                self.play_start_ptr = self.pointer
                self.audio_played = [False] * len(self.messages)

        # Set ptr for playing
        if self.playing:
            timestamp = time.time() - self.play_start_time
            pointer = self.play_start_ptr + timestamp / 10
            if pointer > 1:
                self.playing = False
                self.recording = False
                pointer = 1
            self.pointer = pointer

        # Check for playing audio
        if self.playing:
            for i in range(len(self.audio_played)):
                t = self.messages[i][1]
                if 10*self.play_start_ptr <= t and t <= 10*self.pointer:
                    if not self.audio_played[i]:
                        pygame.mixer.Sound.play(AUDIO[self.messages[i][0]])
                        self.audio_played[i] = True

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
                    pygame.mixer.Sound.play(AUDIO[p])

        # Autocomplete
        if not self.playing and self.buttons.complete.is_clicked(events):
            # Serialize messages to file
            with open(os.path.join(ROOT, "in.txt"), "w") as f:
                for msg in self.messages:
                    f.write(f"{msg[0]} {msg[1]} {msg[2]}")

            # Call completion
            proc = run([sys.executable, os.path.join(ROOT, "client.py"), os.path.join(ROOT, "in.txt"), os.path.join(ROOT, "out.txt")])
            if proc.returncode != 0:
                print("Error in calling completion.")
            else:
                last_time = max([msg[2] for msg in self.messages]) if self.messages else 0
                with open(os.path.join(ROOT, "out.txt")) as f:
                    for line in f.read().strip().split("\n"):
                        parts = line.split(" ")
                        msg = (int(parts[0]), float(parts[1])+last_time, float(parts[2])+last_time)
                        if 0 <= msg[1] and msg[2] <= 10 and 0 <= msg[0] < 88:
                            self.messages.append(msg)
