import librosa
import numpy as np

def extract_features(file_path):
    """ استخراج الميزات الصوتية من الملف """
    y, sr = librosa.load(file_path, sr=None, mono=True)

    if len(y) == 0:
        raise ValueError("⚠️ الملف الصوتي فارغ أو لا يحتوي على بيانات كافية")

    mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=32)
    features = np.mean(mfccs, axis=1).reshape(1, -1)
    return features
