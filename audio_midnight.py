import pygame
import os

class AudioMidnight:
    """gerenciador centralizado de músicas e efeitos sonoros."""
    def __init__(self):
        pygame.mixer.init()

#volumes padrão
        self.music_volume = 0.25
        self.sfx_volume = 0.4

#caminho dos audios
        self.sfx = {}
        self.load_sfx("passo", "footstep_soft.wav", volume=0.2)
        self.load_sfx("folha", "paper_grab.wav", volume=0.4)
        self.load_sfx("piso_barulho", "wood_cerak.wav", volume=0.5)
        self.load_sfx("shh", "whisper_shh.wav", volume=0.6)
        self.load_sfx("easter_egg", "gear_click.wav", volume=0.3)

    def load_sfx(self, key, filename, volume=0.4):
        path = os.path.join(self.sfx_dir, filename)
        if os.path.exists(path):
            sound = pygame.mixer.Sound(path)
            sound.set_volume(volume)
            self.sfx[key] = sound
        else:
            print(f"[Aviso Audio] Arquivo de SFX não encontrado: {path}")

    def play_sfx(self, key):
        """Toca um efeito sonoro curto"""
        if key in self.sfx:
            self.sfx[key].play()

    def play_music(self, filename, loop=-1):
        """Carrega e toca uma música de fundo em loop"""
        path = os.path.join(self.sfx_dir, filename)
        if self.current_track == filename:
            return

        if os.path.exists(path):
            pygame.mixer.music.stop()
            pygame.mixer.music.load(path)
            pygame.mixer.music.set_volume(self.music_volume)
            pygame.mixer.music.play(loops=loop)
            self.current_track = filename
        else:
            print(f"[Aviso Audio] Trilha sonora não encontrada: {path}")

    def stop_music(self):
        pygame.mixer.music.stop()
        self.current_track = None