from typing import Dict, Any

import numpy as np
import soundfile as sf
import speech_recognition as sr

from modules.email_analyzer import (
    URGENT_WORDS,
    SECRECY_WORDS,
    FINANCIAL_WORDS,
    IMPERSONATION_WORDS,
    CREDENTIAL_WORDS,
    clean_text,
    count_matches,
)


def safe_float(value, default=0.0):
    try:
        value = float(value)
        if np.isnan(value) or np.isinf(value):
            return default
        return value
    except Exception:
        return default


def load_audio(file_path: str):
    data, sr_value = sf.read(file_path, always_2d=False)

    if data is None or len(data) == 0:
        return np.array([], dtype=np.float32), 0

    data = np.asarray(data, dtype=np.float32)

    if data.ndim > 1:
        data = np.mean(data, axis=1)

    peak = np.max(np.abs(data)) if len(data) > 0 else 0
    if peak > 1.0:
        data = data / peak

    return data, int(sr_value)


def zero_crossing_rate(y: np.ndarray) -> float:
    if len(y) < 2:
        return 0.0
    crossings = np.sum(np.abs(np.diff(np.signbit(y))))
    return safe_float(crossings / len(y))


def frame_signal(y: np.ndarray, frame_length: int, hop_length: int):
    frames = []
    if len(y) < frame_length:
        return [y]

    for start in range(0, len(y) - frame_length + 1, hop_length):
        frames.append(y[start:start + frame_length])

    return frames


def estimate_pitch_stats(y: np.ndarray, sr_value: int) -> tuple[float, float]:
    if len(y) == 0 or sr_value <= 0:
        return 0.0, 0.0

    frame_length = min(int(0.04 * sr_value), len(y))
    hop_length = max(int(0.02 * sr_value), 1)

    frames = frame_signal(y, frame_length, hop_length)
    pitch_values = []

    min_freq = 75
    max_freq = 350

    min_lag = max(int(sr_value / max_freq), 1)
    max_lag = max(int(sr_value / min_freq), min_lag + 1)

    for frame in frames:
        frame = np.asarray(frame, dtype=np.float32)

        if len(frame) < max_lag + 1:
            continue

        if np.sqrt(np.mean(frame ** 2)) < 0.01:
            continue

        frame = frame - np.mean(frame)
        corr = np.correlate(frame, frame, mode="full")
        corr = corr[len(corr) // 2:]

        search_region = corr[min_lag:max_lag]
        if len(search_region) == 0:
            continue

        best_lag = np.argmax(search_region) + min_lag
        if best_lag > 0:
            pitch = sr_value / best_lag
            if min_freq <= pitch <= max_freq:
                pitch_values.append(pitch)

    if len(pitch_values) == 0:
        return 0.0, 0.0

    pitch_values = np.asarray(pitch_values, dtype=np.float32)
    return safe_float(np.mean(pitch_values)), safe_float(np.std(pitch_values))


def compute_energy_stats(y: np.ndarray, sr_value: int) -> tuple[float, float]:
    if len(y) == 0 or sr_value <= 0:
        return 0.0, 0.0

    frame_length = min(int(0.03 * sr_value), len(y))
    hop_length = max(int(0.015 * sr_value), 1)

    frames = frame_signal(y, frame_length, hop_length)
    energies = []

    for frame in frames:
        frame = np.asarray(frame, dtype=np.float32)
        energies.append(np.sqrt(np.mean(frame ** 2)))

    if len(energies) == 0:
        return 0.0, 0.0

    energies = np.asarray(energies, dtype=np.float32)
    return safe_float(np.mean(energies)), safe_float(np.std(energies))


def compute_spectral_stats(y: np.ndarray, sr_value: int) -> tuple[float, float]:
    if len(y) == 0 or sr_value <= 0:
        return 0.0, 0.0

    frame_length = min(int(0.03 * sr_value), len(y))
    hop_length = max(int(0.015 * sr_value), 1)

    frames = frame_signal(y, frame_length, hop_length)
    centroids = []

    for frame in frames:
        frame = np.asarray(frame, dtype=np.float32)
        if len(frame) == 0:
            continue

        windowed = frame * np.hanning(len(frame))
        spectrum = np.abs(np.fft.rfft(windowed))
        freqs = np.fft.rfftfreq(len(windowed), d=1.0 / sr_value)

        mag_sum = np.sum(spectrum)
        if mag_sum <= 1e-10:
            continue

        centroid = np.sum(freqs * spectrum) / mag_sum
        centroids.append(centroid)

    if len(centroids) == 0:
        return 0.0, 0.0

    centroids = np.asarray(centroids, dtype=np.float32)
    return safe_float(np.mean(centroids)), safe_float(np.std(centroids))


def compute_signal_regularity(y: np.ndarray, sr_value: int) -> float:
    if len(y) == 0 or sr_value <= 0:
        return 0.0

    frame_length = min(int(0.03 * sr_value), len(y))
    hop_length = max(int(0.015 * sr_value), 1)

    frames = frame_signal(y, frame_length, hop_length)
    sims = []

    prev = None
    for frame in frames:
        frame = np.asarray(frame, dtype=np.float32)
        if len(frame) == 0:
            continue

        norm = np.linalg.norm(frame)
        if norm > 0:
            frame = frame / norm

        if prev is not None and len(prev) == len(frame):
            sim = float(np.dot(prev, frame))
            sims.append(sim)

        prev = frame

    if len(sims) == 0:
        return 0.0

    return safe_float(np.mean(sims))


def transcribe_audio(file_path: str) -> tuple[str, str]:
    recognizer = sr.Recognizer()

    try:
        with sr.AudioFile(file_path) as source:
            audio = recognizer.record(source)

        transcript = recognizer.recognize_google(audio)
        return transcript, "Transcription successful"
    except sr.UnknownValueError:
        return "", "Speech was not clearly understood"
    except sr.RequestError:
        return "", "Speech recognition service unavailable"
    except Exception as e:
        return "", f"Transcription error: {e}"


def analyze_transcript_text(transcript: str) -> Dict[str, Any]:
    cleaned = clean_text(transcript)

    score = 0
    triggered = []

    urgent_hits = count_matches(cleaned, URGENT_WORDS)
    secrecy_hits = count_matches(cleaned, SECRECY_WORDS)
    financial_hits = count_matches(cleaned, FINANCIAL_WORDS)
    impersonation_hits = count_matches(cleaned, IMPERSONATION_WORDS)
    credential_hits = count_matches(cleaned, CREDENTIAL_WORDS)

    suspicious_phrases = [
        "send money",
        "send it",
        "send it now",
        "send it to me",
        "i need the money",
        "i need money now",
        "transfer the money",
        "transfer funds",
        "transfer funds now",
        "urgent transfer",
        "make payment",
        "make payment now",
        "make the payment urgently",
        "bank transfer",
        "send the funds",
        "i need the funds",
        "i need the funds now",
        "send it immediately",
        "make the transfer immediately",
        "buy gift cards",
        "send gift cards",
        "this is the ceo",
        "i am the ceo",
        "keep this confidential",
        "do not tell anyone",
        "don't let anyone know",
        "don't tell anyone",
        "handle this urgently",
    ]
    phrase_hits = count_matches(cleaned, suspicious_phrases)

    if urgent_hits:
        score += 20
        triggered.append(f"Urgency language detected in transcript: {', '.join(urgent_hits[:4])}")

    if secrecy_hits:
        score += 15
        triggered.append(f"Secrecy language detected in transcript: {', '.join(secrecy_hits[:4])}")

    if financial_hits:
        score += 25
        triggered.append(f"Financial request indicators detected in transcript: {', '.join(financial_hits[:4])}")

    if impersonation_hits:
        score += 20
        triggered.append(f"Authority or impersonation language detected in transcript: {', '.join(impersonation_hits[:4])}")

    if credential_hits:
        score += 20
        triggered.append(f"Credential related indicators detected in transcript: {', '.join(credential_hits[:4])}")

    if phrase_hits:
        score += 20
        triggered.append(f"Scam style phrases detected in transcript: {', '.join(phrase_hits[:4])}")

    if len(cleaned.split()) < 4 and len(cleaned) > 0:
        score += 5
        triggered.append("Very short spoken message detected, which may hide context or intent.")

    if (
        "money" in cleaned
        or "fund" in cleaned
        or "funds" in cleaned
        or "payment" in cleaned
        or "transfer" in cleaned
        or "bank" in cleaned
        or "send it to me" in cleaned
    ):
        score += 20
        triggered.append("Direct financial intent detected in spoken content.")

    has_urgency = bool(urgent_hits)
    has_secrecy = bool(secrecy_hits)
    has_financial = bool(financial_hits)
    has_impersonation = bool(impersonation_hits)
    has_credentials = bool(credential_hits)
    has_phrase = bool(phrase_hits)

    if has_urgency and has_financial:
        score += 20
        triggered.append("Critical fraud pattern detected: urgency combined with financial request.")

    if has_impersonation and has_financial:
        score += 25
        triggered.append("Critical fraud pattern detected: impersonation combined with financial request.")

    if has_urgency and has_impersonation:
        score += 15
        triggered.append("High-pressure authority pattern detected: urgency combined with impersonation.")

    if has_secrecy and has_financial:
        score += 18
        triggered.append("Concealed transaction pattern detected: secrecy combined with financial request.")

    if has_credentials and has_urgency:
        score += 18
        triggered.append("Credential theft pressure pattern detected: urgency combined with credential request.")

    if has_phrase and has_financial:
        score += 15
        triggered.append("Scam phrase plus financial request pattern detected.")

    if has_urgency and has_impersonation and (has_financial or has_phrase):
        score += 35
        triggered.append("Severe scam signature detected: urgency + impersonation + financial intent.")

    return {
        "score": min(score, 100),
        "triggered_indicators": triggered,
    }


def analyze_voice_file(file_path: str) -> Dict[str, Any]:
    y, sr_value = load_audio(file_path)

    if len(y) == 0 or sr_value <= 0:
        features = {
            "Duration (s)": 0,
            "Pitch Mean (Hz)": 0,
            "Pitch Variation": 0,
            "Energy Mean": 0,
            "Energy Variation": 0,
            "Spectral Mean": 0,
            "Spectral Variation": 0,
            "Zero Crossing Rate": 0,
            "Signal Regularity": 0,
            "Sample Rate": 0,
        }
        return {
            "score": 0,
            "acoustic_score": 0,
            "content_score": 0,
            "classification_hint": "Genuine",
            "triggered_indicators": ["Audio file appears empty, unsupported, or unreadable."],
            "features": features,
            "transcript": "",
            "transcription_status": "Audio unreadable",
        }

    duration = safe_float(len(y) / sr_value)
    pitch_mean, pitch_std = estimate_pitch_stats(y, sr_value)
    energy_mean, energy_std = compute_energy_stats(y, sr_value)
    spectral_mean, spectral_std = compute_spectral_stats(y, sr_value)
    zcr = zero_crossing_rate(y)
    regularity = compute_signal_regularity(y, sr_value)

    acoustic_score = 0
    acoustic_triggers = []

    if duration < 2.0:
        acoustic_score += 10
        acoustic_triggers.append("Audio is very short, which may reduce natural speech variability.")

    if 0 < pitch_std < 8:
        acoustic_score += 18
        acoustic_triggers.append("Very low pitch variation detected, suggesting monotonic or synthetic-like speech.")
    elif 8 <= pitch_std < 15:
        acoustic_score += 10
        acoustic_triggers.append("Low pitch variation detected in the voice sample.")

    if energy_std < 0.015:
        acoustic_score += 15
        acoustic_triggers.append("Low energy variation detected, suggesting unusually stable vocal intensity.")
    elif energy_std < 0.03:
        acoustic_score += 8
        acoustic_triggers.append("Moderately low energy variation detected in the audio sample.")

    if spectral_std < 180:
        acoustic_score += 12
        acoustic_triggers.append("Low spectral variation detected, which may reflect reduced natural vocal texture.")
    elif spectral_std < 300:
        acoustic_score += 6
        acoustic_triggers.append("Moderately low spectral variation detected in the audio sample.")

    if regularity > 0.92:
        acoustic_score += 15
        acoustic_triggers.append("High frame-to-frame regularity detected, suggesting possible robotic speech consistency.")
    elif regularity > 0.85:
        acoustic_score += 8
        acoustic_triggers.append("Moderately high signal regularity detected in the voice sample.")

    if zcr < 0.02:
        acoustic_score += 8
        acoustic_triggers.append("Low zero-crossing rate detected, indicating unusually stable signal transitions.")

    transcript, transcription_status = transcribe_audio(file_path)

    if transcript:
        content_result = analyze_transcript_text(transcript)
    else:
        content_result = {"score": 0, "triggered_indicators": []}

    content_score = content_result["score"]
    combined_score = min(int(round(acoustic_score * 0.30 + content_score * 0.70)), 100)

    all_triggers = []
    all_triggers.extend(acoustic_triggers)
    all_triggers.extend(content_result.get("triggered_indicators", []))

    if combined_score >= 60:
        classification_hint = "Likely Scam"
    elif combined_score >= 30:
        classification_hint = "Suspicious"
    else:
        classification_hint = "Genuine"

    features = {
        "Duration (s)": round(duration, 2) if duration else 0,
        "Pitch Mean (Hz)": round(pitch_mean, 2) if pitch_mean else 0,
        "Pitch Variation": round(pitch_std, 2) if pitch_std else 0,
        "Energy Mean": round(energy_mean, 4) if energy_mean else 0,
        "Energy Variation": round(energy_std, 4) if energy_std else 0,
        "Spectral Mean": round(spectral_mean, 2) if spectral_mean else 0,
        "Spectral Variation": round(spectral_std, 2) if spectral_std else 0,
        "Zero Crossing Rate": round(zcr, 4) if zcr else 0,
        "Signal Regularity": round(regularity, 4) if regularity else 0,
        "Sample Rate": sr_value if sr_value else 0,
    }

    return {
        "score": combined_score,
        "acoustic_score": min(acoustic_score, 100),
        "content_score": min(content_score, 100),
        "classification_hint": classification_hint,
        "triggered_indicators": all_triggers,
        "features": features,
        "transcript": transcript,
        "transcription_status": transcription_status,
    }