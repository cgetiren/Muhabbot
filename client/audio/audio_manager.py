import pyaudio
import numpy as np
from PyQt6.QtCore import QObject, pyqtSignal
import threading

class AudioManager(QObject):
    audio_data_ready = pyqtSignal(bytes)  # Ses verisi hazır olduğunda sinyal gönder
    
    def __init__(self):
        super().__init__()
        self.CHUNK = 1024
        self.FORMAT = pyaudio.paFloat32
        self.CHANNELS = 1
        self.RATE = 44100
        
        self.p = pyaudio.PyAudio()
        self.recording = False
        self.playing = False
        
        # Mikrofon ve hoparlör stream'leri
        self.input_stream = None
        self.output_stream = None
        
        # Thread kontrolü için
        self.record_thread = None
        
    def start_recording(self):
        """Mikrofon kaydını başlat"""
        try:
            if not self.recording:
                self.recording = True
                self.input_stream = self.p.open(
                    format=self.FORMAT,
                    channels=self.CHANNELS,
                    rate=self.RATE,
                    input=True,
                    frames_per_buffer=self.CHUNK
                )
                
                # Önceki thread varsa durdur
                if self.record_thread and self.record_thread.is_alive():
                    self.recording = False
                    self.record_thread.join()
                
                # Yeni kayıt thread'i başlat
                self.record_thread = threading.Thread(target=self._record_thread, daemon=True)
                self.record_thread.start()
                print("Mikrofon kaydı başlatıldı")
        except Exception as e:
            print(f"Mikrofon başlatma hatası: {e}")
            self.recording = False
            
    def stop_recording(self):
        """Mikrofon kaydını durdur"""
        try:
            self.recording = False
            if self.record_thread and self.record_thread.is_alive():
                self.record_thread.join(timeout=1.0)
            
            if self.input_stream:
                self.input_stream.stop_stream()
                self.input_stream.close()
                self.input_stream = None
            print("Mikrofon kaydı durduruldu")
        except Exception as e:
            print(f"Mikrofon durdurma hatası: {e}")
            
    def start_playback(self):
        """Ses çalmayı başlat"""
        try:
            if not self.playing:
                self.playing = True
                self.output_stream = self.p.open(
                    format=self.FORMAT,
                    channels=self.CHANNELS,
                    rate=self.RATE,
                    output=True,
                    frames_per_buffer=self.CHUNK
                )
                print("Hoparlör başlatıldı")
        except Exception as e:
            print(f"Hoparlör başlatma hatası: {e}")
            self.playing = False
            
    def stop_playback(self):
        """Ses çalmayı durdur"""
        try:
            self.playing = False
            if self.output_stream:
                self.output_stream.stop_stream()
                self.output_stream.close()
                self.output_stream = None
            print("Hoparlör durduruldu")
        except Exception as e:
            print(f"Hoparlör durdurma hatası: {e}")
            
    def play_audio(self, audio_data):
        """Gelen ses verisini çal"""
        if self.playing and self.output_stream:
            try:
                self.output_stream.write(audio_data)
            except Exception as e:
                print(f"Ses çalma hatası: {e}")
                
    def _record_thread(self):
        """Sürekli mikrofon kaydı yapan thread"""
        print("Kayıt thread'i başladı")
        while self.recording:
            try:
                if self.input_stream:
                    data = self.input_stream.read(self.CHUNK, exception_on_overflow=False)
                    self.audio_data_ready.emit(data)
            except Exception as e:
                print(f"Kayıt hatası: {e}")
                break
        print("Kayıt thread'i sonlandı")
    
    def start_microphone_loopback(self):
        """Mikrofondan gelen sesi direkt olarak hoparlöre yönlendir"""
        if not hasattr(self, 'loopback_stream'):
            def callback(in_data, frame_count, time_info, status):
                return (in_data, pyaudio.paContinue)
            
            self.loopback_stream = self.p.open(
                format=self.FORMAT,
                channels=self.CHANNELS,
                rate=self.RATE,
                input=True,
                output=True,
                stream_callback=callback
            )
        
        self.loopback_stream.start_stream()
    
    def stop_microphone_loopback(self):
        """Mikrofon loopback'ini durdur"""
        if hasattr(self, 'loopback_stream'):
            self.loopback_stream.stop_stream()
            self.loopback_stream.close()
            delattr(self, 'loopback_stream')
    
    def cleanup(self):
        """Kaynakları temizle"""
        self.stop_recording()
        self.stop_playback()
        self.stop_microphone_loopback()  # Loopback'i de temizle
        self.p.terminate()

    def apply_settings(self, settings):
        """Ses ayarlarını uygula"""
        # Mevcut streamleri durdur
        self.stop_recording()
        self.stop_playback()
        
        # Yeni ayarları kaydet
        self.input_device = settings['input_device']
        self.output_device = settings['output_device']
        self.input_volume = settings['mic_volume'] / 100.0
        self.output_volume = settings['speaker_volume'] / 100.0
        
        # Eğer kayıt veya çalma aktifse, yeni ayarlarla tekrar başlat
        if self.recording:
            self.start_recording()
        if self.playing:
            self.start_playback()
