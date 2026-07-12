
from flask import Flask, jsonify
import torch
import torchaudio
import librosa
import numpy as np
import os
from torch.utils.data import Dataset

app = Flask(__name__)

def extract_singing_features(audio_path, sample_rate=44100):
    waveform, sr = torchaudio.load(audio_path)
    if sr!= sample_rate:
        resampler = torchaudio.transforms.Resample(sr, sample_rate)
        waveform = resampler(waveform)
    y = waveform.numpy().squeeze()
    mel_spec = librosa.feature.melspectrogram(y=y, sr=sample_rate, n_fft=2048, hop_length=512, n_mels=80)
    log_mel_spec = librosa.power_to_db(mel_spec, ref=np.max)
    f0, voiced_flag, voiced_probs = librosa.pyin(y, fmin=librosa.note_to_hz('C2'), fmax=librosa.note_to_hz('C6'), sr=sample_rate, hop_length=512)
    f0 = np.nan_to_num(f0)
    return torch.tensor(log_mel_spec), torch.tensor(f0)

class SingingDataset(Dataset):
    def __init__(self, data_dir):
        self.wav_dir = os.path.join(data_dir, "wavs")
        self.txt_dir = os.path.join(data_dir, "transcripts")
        self.midi_dir = os.path.join(data_dir, "midis")
        self.files = [f.replace(".wav","") for f in os.listdir(self.wav_dir)]
    def __len__(self):
        return len(self.files)
    def __getitem__(self, idx):
        name = self.files[idx]
        wav_path = os.path.join(self.wav_dir, name + ".wav")
        target_mel, target_pitch = extract_singing_features(wav_path)
        with open(os.path.join(self.txt_dir, name + ".txt"), "r") as f:
            transcript = f.read().strip()
        midi_path = os.path.join(self.midi_dir, name + ".mid")
        return {"mel": target_mel, "pitch": target_pitch, "text": transcript, "midi": midi_path}

@app.route('/')
def home():
    return "ZSD Brain is live with Voice Cloning"

if __name__ == '__main__':
    app.run()
