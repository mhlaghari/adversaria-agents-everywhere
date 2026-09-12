"""Bounded audio capture. Live service work never blocks the PortAudio callback."""

from __future__ import annotations

import queue
import tempfile
import threading
import time
import wave
from pathlib import Path

from .config import CliError, private_dir
from .transcription import create_transcriber, speech_key


def devices():
    import sounddevice as sd

    try:
        return [
            {
                "id": i,
                "name": d["name"],
                "inputs": d["max_input_channels"],
                "sample_rate": d["default_samplerate"],
            }
            for i, d in enumerate(sd.query_devices())
            if d["max_input_channels"]
        ]
    except sd.PortAudioError as exc:
        raise CliError(
            "Cannot list audio devices. Check PortAudio and microphone permissions."
        ) from exc


def write_wav(path, data, rate):
    with wave.open(str(path), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(rate)
        wav.writeframes(data)


class Recorder:
    def __init__(self, config, on_caption, on_notice, device=None, system_device=None):
        self.config, self.on_caption, self.on_notice = config, on_caption, on_notice
        self.inputs = [("Me", device)]
        if system_device is not None:
            self.inputs.append(("Them", system_device))
        self.stop_event = threading.Event()
        self.streams, self.writers, self.feeders = [], [], []
        self.paths = {}
        self.errors = []
        self.realtime = {}
        self.transcript = []
        self.directory = Path(
            tempfile.mkdtemp(prefix="capture-", dir=private_dir(config.directory / "recordings"))
        )
        self.started = False

    def start(self):
        import sounddevice as sd

        speech_key(self.config)
        try:
            for source, device in self.inputs:

                def emit(text, boundary="silence", label=source):
                    if text.strip():
                        self.transcript.append((time.monotonic(), f"{label}: {text}"))
                    self.on_caption(text, label, boundary)

                realtime = create_transcriber(self.config, emit)
                realtime.start()
                self.realtime[source] = realtime
                info = sd.query_devices(device, "input")
                rate = round(info["default_samplerate"])
                archive = queue.Queue(maxsize=240)  # 60 seconds of PCM, bounded.
                feed = queue.Queue(maxsize=120)  # 30 seconds before visible live-drop.
                path = self.directory / f"{source.lower()}.wav"
                self.paths[source] = path

                def callback(data, frames, timing, status, q=archive):
                    if status:
                        self.errors.append("Audio input overflow; recording may have gaps.")
                    try:
                        q.put_nowait(bytes(data))
                    except queue.Full:
                        self.errors.append(
                            "Recording buffer overflow; stopping to avoid silent data loss."
                        )
                        self.stop_event.set()

                writer = threading.Thread(
                    target=self._archive, args=(archive, feed, path, rate), daemon=True
                )
                feeder = threading.Thread(target=self._feed, args=(feed, source, rate), daemon=True)
                stream = sd.RawInputStream(
                    device=device,
                    samplerate=rate,
                    channels=1,
                    dtype="int16",
                    blocksize=rate // 4,
                    callback=callback,
                )
                self.streams.append(stream)
                self.writers.append(writer)
                self.feeders.append(feeder)
                writer.start()
                feeder.start()
                stream.start()
            self.started = True
        except (sd.PortAudioError, ValueError, CliError) as exc:
            self.stop()
            for realtime in self.realtime.values():
                realtime.abort()
            if isinstance(exc, CliError):
                raise
            raise CliError(
                "Cannot open microphone/input. Run devices and grant your terminal microphone access."
            ) from exc

    def _archive(self, archive, feed, path, rate):
        try:
            with wave.open(str(path), "wb") as wav:
                wav.setnchannels(1)
                wav.setsampwidth(2)
                wav.setframerate(rate)
                pending = bytearray()
                while not self.stop_event.is_set() or not archive.empty():
                    try:
                        data = archive.get(timeout=0.1)
                    except queue.Empty:
                        continue
                    wav.writeframes(data)
                    pending.extend(data)
                    if len(pending) >= rate // 2:
                        try:
                            feed.put_nowait(bytes(pending))
                        except queue.Full:
                            self.errors.append(
                                "Live captions fell behind; full audio is preserved for transcription."
                            )
                        pending.clear()
                # Flush final speech with silence so the final commitment can be caught.
                feed.put(bytes(pending) + bytes(rate * 3), timeout=35)
        except (OSError, queue.Full) as exc:
            self.errors.append(f"Audio writer failed: {type(exc).__name__}")
        finally:
            # The feeder drains all queued audio before its sentinel.
            try:
                feed.put(None, timeout=35)
            except queue.Full:
                self.errors.append("Live caption queue did not drain.")

    def _feed(self, feed, source, rate):
        realtime = self.realtime[source]
        failed = False
        try:
            while True:
                data = feed.get()
                if data is None:
                    if not failed:
                        realtime.finish()
                    return
                if not failed:
                    try:
                        realtime.send(data, rate)
                    except CliError as exc:
                        self.errors.append(str(exc))
                        self.on_notice(str(exc) + " Full audio is still being recorded.")
                        failed = True
        except CliError as exc:
            self.errors.append(str(exc))
        finally:
            realtime.abort()

    def stop(self):
        for stream in self.streams:
            stream.stop()
            stream.close()
        self.streams.clear()
        self.stop_event.set()
        for writer in self.writers:
            writer.join(timeout=40)
        for feeder in self.feeders:
            feeder.join(timeout=40)
        if any(t.is_alive() for t in self.writers + self.feeders):
            raise CliError(
                f"Caption processing is still finishing. Audio remains at {self.directory}."
            )
        for error in sorted(set(self.errors)):
            self.on_notice(error)
        self.started = False
        return self.paths

    def cleanup(self):
        # Only the exact audio paths created by this instance, after successful transcription.
        for path in self.paths.values():
            path.unlink(missing_ok=True)
        try:
            self.directory.rmdir()
        except OSError:
            pass
