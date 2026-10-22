"""Ações no player do Spotify: escolher o dispositivo, tocar e conferir, volume."""
import time


def pick_device(sp):
    devices = sp.devices().get("devices", [])
    active = [device for device in devices if device.get("is_active")]
    chosen = (active or devices or [None])[0]
    return chosen["id"] if chosen else None


def play_and_confirm(sp, device_id, **play_args):
    sp.transfer_playback(device_id=device_id, force_play=False)
    time.sleep(0.5)
    sp.start_playback(device_id=device_id, **play_args)
    time.sleep(1)
    playback = sp.current_playback()
    return bool(playback and playback.get("is_playing"))


def compute_new_volume(current, mode, value):
    """Função pura: calcula o volume novo, sempre entre 0 e 100."""
    if mode == "set":
        new = value
    elif mode == "up":
        new = current + value
    else:
        new = current - value
    return max(0, min(100, new))


def change_spotify_volume(sp, playback, mode, value):
    """Muda o volume do dispositivo do Spotify. Devolve o volume novo, ou None se o dispositivo não permite."""
    device = playback.get("device") or {}
    if not device.get("supports_volume", True) or device.get("volume_percent") is None:
        return None
    new = compute_new_volume(device["volume_percent"], mode, value)
    sp.volume(new, device_id=device.get("id"))
    return new
