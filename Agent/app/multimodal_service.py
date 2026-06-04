from __future__ import annotations

import base64
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import httpx

try:
    from openai import OpenAI
except Exception:  # pragma: no cover
    OpenAI = None


@dataclass
class SttResult:
    text: str
    provider: str
    note: str = ""


@dataclass
class TtsResult:
    audio_base64: str
    provider: str
    format: str = "wav"
    note: str = ""


@dataclass
class OcrResult:
    text: str
    provider: str
    note: str = ""


class MultimodalService:
    def __init__(
        self,
        *,
        openai_api_key: str,
        stt_model: str,
        tts_model: str,
        tts_voice: str,
        vision_model: str,
        deepgram_api_key: str,
        deepgram_model: str,
        assemblyai_api_key: str,
        elevenlabs_api_key: str,
        elevenlabs_voice_id: str,
        elevenlabs_model_id: str,
        ocr_space_api_key: str,
    ) -> None:
        self._stt_model = stt_model
        self._tts_model = tts_model
        self._tts_voice = tts_voice
        self._vision_model = vision_model

        self._deepgram_api_key = deepgram_api_key.strip()
        self._deepgram_model = deepgram_model.strip() or "nova-2"
        self._assemblyai_api_key = assemblyai_api_key.strip()

        self._elevenlabs_api_key = elevenlabs_api_key.strip()
        self._elevenlabs_voice_id = elevenlabs_voice_id.strip()
        self._elevenlabs_model_id = elevenlabs_model_id.strip() or "eleven_multilingual_v2"

        self._ocr_space_api_key = ocr_space_api_key.strip()

        self._client = None
        if openai_api_key and OpenAI is not None:
            self._client = OpenAI(api_key=openai_api_key)

    @property
    def has_openai(self) -> bool:
        return self._client is not None

    @property
    def provider_availability(self) -> dict[str, bool]:
        return {
            "openai": self._client is not None,
            "deepgram": bool(self._deepgram_api_key),
            "assemblyai": bool(self._assemblyai_api_key),
            "elevenlabs": bool(self._elevenlabs_api_key and self._elevenlabs_voice_id),
            "ocr_space": bool(self._ocr_space_api_key),
        }

    def transcribe(
        self,
        *,
        audio_base64: str,
        mime_type: str = "audio/wav",
        language: str = "ko",
        provider: str = "auto",
    ) -> SttResult:
        payload = self._decode_base64(audio_base64)
        selected = (provider or "auto").strip().lower()

        if selected == "auto":
            pipeline = ["openai", "deepgram", "assemblyai"]
        else:
            pipeline = [selected]

        errors: list[str] = []
        for step in pipeline:
            try:
                if step == "openai":
                    return self._stt_openai(payload=payload, mime_type=mime_type, language=language)
                if step == "deepgram":
                    return self._stt_deepgram(payload=payload, mime_type=mime_type, language=language)
                if step == "assemblyai":
                    return self._stt_assemblyai(payload=payload, language=language)
            except Exception as exc:
                errors.append(f"{step}:{exc}")

        raise ValueError(
            "STT provider unavailable. Configure at least one real provider API key because mock fallback was removed. Details: "
            + " | ".join(errors)
        )

    def synthesize(
        self,
        *,
        text: str,
        voice: str | None = None,
        provider: str = "auto",
        audio_format: str = "wav",
    ) -> TtsResult:
        clean_text = text.strip()
        if not clean_text:
            raise ValueError("text is required")

        selected = (provider or "auto").strip().lower()
        if selected == "auto":
            pipeline = ["openai", "elevenlabs"]
        else:
            pipeline = [selected]

        errors: list[str] = []
        for step in pipeline:
            try:
                if step == "openai":
                    return self._tts_openai(text=clean_text, voice=voice, audio_format=audio_format)
                if step == "elevenlabs":
                    return self._tts_elevenlabs(text=clean_text, voice=voice, audio_format=audio_format)
            except Exception as exc:
                errors.append(f"{step}:{exc}")

        raise ValueError(
            "TTS provider unavailable. Configure at least one real provider API key because mock fallback was removed. Details: "
            + " | ".join(errors)
        )

    def ocr(
        self,
        *,
        image_base64: str,
        mime_type: str = "image/png",
        prompt: str = "이미지 안 텍스트를 OCR 결과로 정리해 주세요.",
        provider: str = "auto",
    ) -> OcrResult:
        payload = self._decode_base64(image_base64)
        selected = (provider or "auto").strip().lower()
        if selected == "auto":
            pipeline = ["openai", "ocr_space"]
        else:
            pipeline = [selected]

        errors: list[str] = []
        for step in pipeline:
            try:
                if step == "openai":
                    return self._ocr_openai(payload=payload, mime_type=mime_type, prompt=prompt)
                if step == "ocr_space":
                    return self._ocr_ocr_space(payload=payload, mime_type=mime_type)
            except Exception as exc:
                errors.append(f"{step}:{exc}")

        raise ValueError(
            "OCR provider unavailable. Configure at least one real provider API key because mock fallback was removed. Details: "
            + " | ".join(errors)
        )

    def _stt_openai(self, *, payload: bytes, mime_type: str, language: str) -> SttResult:
        if self._client is None:
            raise RuntimeError("OPENAI_API_KEY is missing")
        suffix = self._mime_to_suffix(mime_type)
        with tempfile.NamedTemporaryFile(suffix=suffix) as tmp:
            tmp.write(payload)
            tmp.flush()
            with Path(tmp.name).open("rb") as fp:
                response = self._client.audio.transcriptions.create(
                    model=self._stt_model,
                    file=fp,
                    language=language,
                )
        text = str(getattr(response, "text", "")).strip()
        if not text:
            raise RuntimeError("empty transcript")
        return SttResult(text=text, provider="openai")

    def _stt_deepgram(self, *, payload: bytes, mime_type: str, language: str) -> SttResult:
        if not self._deepgram_api_key:
            raise RuntimeError("DEEPGRAM_API_KEY is missing")

        params = {
            "model": self._deepgram_model,
            "language": language,
            "smart_format": "true",
        }
        headers = {
            "Authorization": f"Token {self._deepgram_api_key}",
            "Content-Type": mime_type or "audio/wav",
        }
        with httpx.Client(timeout=35.0) as client:
            resp = client.post("https://api.deepgram.com/v1/listen", params=params, headers=headers, content=payload)
            resp.raise_for_status()
            data = resp.json()

        text = (
            data.get("results", {})
            .get("channels", [{}])[0]
            .get("alternatives", [{}])[0]
            .get("transcript", "")
        )
        text = str(text).strip()
        if not text:
            raise RuntimeError("empty transcript")
        return SttResult(text=text, provider="deepgram")

    def _stt_assemblyai(self, *, payload: bytes, language: str) -> SttResult:
        if not self._assemblyai_api_key:
            raise RuntimeError("ASSEMBLYAI_API_KEY is missing")

        headers = {"Authorization": self._assemblyai_api_key}
        with httpx.Client(timeout=35.0) as client:
            upload = client.post("https://api.assemblyai.com/v2/upload", headers=headers, content=payload)
            upload.raise_for_status()
            upload_url = str(upload.json().get("upload_url", "")).strip()
            if not upload_url:
                raise RuntimeError("upload_url missing")

            transcript_payload: dict[str, Any] = {"audio_url": upload_url}
            if language:
                transcript_payload["language_code"] = language

            created = client.post(
                "https://api.assemblyai.com/v2/transcript",
                headers={"Authorization": self._assemblyai_api_key, "Content-Type": "application/json"},
                json=transcript_payload,
            )
            created.raise_for_status()
            transcript_id = str(created.json().get("id", "")).strip()
            if not transcript_id:
                raise RuntimeError("transcript id missing")

            for _ in range(20):
                poll = client.get(
                    f"https://api.assemblyai.com/v2/transcript/{transcript_id}",
                    headers={"Authorization": self._assemblyai_api_key},
                )
                poll.raise_for_status()
                data = poll.json()
                status = str(data.get("status", "")).lower()
                if status == "completed":
                    text = str(data.get("text", "")).strip()
                    if not text:
                        raise RuntimeError("empty transcript")
                    return SttResult(text=text, provider="assemblyai")
                if status == "error":
                    raise RuntimeError(str(data.get("error", "assemblyai transcription failed")))
                time.sleep(1.5)

        raise RuntimeError("assemblyai transcription timeout")

    def _tts_openai(self, *, text: str, voice: str | None, audio_format: str) -> TtsResult:
        if self._client is None:
            raise RuntimeError("OPENAI_API_KEY is missing")

        selected_voice = (voice or self._tts_voice).strip() or self._tts_voice
        fmt = (audio_format or "wav").strip().lower()
        response = self._client.audio.speech.create(
            model=self._tts_model,
            voice=selected_voice,
            input=text,
            format=fmt,
        )
        if hasattr(response, "read"):
            audio_bytes = response.read()
        elif hasattr(response, "content"):
            audio_bytes = response.content
        else:
            audio_bytes = bytes(response)
        return TtsResult(audio_base64=base64.b64encode(audio_bytes).decode("utf-8"), provider="openai", format=fmt)

    def _tts_elevenlabs(self, *, text: str, voice: str | None, audio_format: str) -> TtsResult:
        if not self._elevenlabs_api_key or not self._elevenlabs_voice_id:
            raise RuntimeError("ELEVENLABS_API_KEY or ELEVENLABS_VOICE_ID missing")

        voice_id = (voice or self._elevenlabs_voice_id).strip() or self._elevenlabs_voice_id
        headers = {
            "xi-api-key": self._elevenlabs_api_key,
            "Content-Type": "application/json",
            "Accept": "audio/mpeg",
        }
        payload = {
            "text": text,
            "model_id": self._elevenlabs_model_id,
            "voice_settings": {"stability": 0.45, "similarity_boost": 0.75},
        }
        with httpx.Client(timeout=45.0) as client:
            resp = client.post(
                f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
                headers=headers,
                json=payload,
            )
            resp.raise_for_status()
            audio_bytes = resp.content

        requested = (audio_format or "mp3").strip().lower()
        actual_fmt = "mp3"
        note = "elevenlabs response is mp3"
        if requested == "mp3":
            note = ""
        return TtsResult(
            audio_base64=base64.b64encode(audio_bytes).decode("utf-8"),
            provider="elevenlabs",
            format=actual_fmt,
            note=note,
        )

    def _ocr_openai(self, *, payload: bytes, mime_type: str, prompt: str) -> OcrResult:
        if self._client is None:
            raise RuntimeError("OPENAI_API_KEY is missing")

        encoded = base64.b64encode(payload).decode("utf-8")
        data_url = f"data:{mime_type};base64,{encoded}"
        response = self._client.chat.completions.create(
            model=self._vision_model,
            temperature=0,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": data_url}},
                    ],
                }
            ],
        )
        text = str(response.choices[0].message.content or "").strip()
        if not text:
            raise RuntimeError("empty ocr text")
        return OcrResult(text=text, provider="openai")

    def _ocr_ocr_space(self, *, payload: bytes, mime_type: str) -> OcrResult:
        if not self._ocr_space_api_key:
            raise RuntimeError("OCR_SPACE_API_KEY is missing")

        encoded = base64.b64encode(payload).decode("utf-8")
        body = {
            "base64Image": f"data:{mime_type};base64,{encoded}",
            "language": "kor",
            "isOverlayRequired": "false",
            "OCREngine": "2",
        }
        with httpx.Client(timeout=35.0) as client:
            resp = client.post(
                "https://api.ocr.space/parse/image",
                headers={"apikey": self._ocr_space_api_key},
                data=body,
            )
            resp.raise_for_status()
            data = resp.json()

        if data.get("IsErroredOnProcessing"):
            err = data.get("ErrorMessage") or data.get("ErrorDetails") or "ocr.space processing error"
            raise RuntimeError(str(err))

        texts: list[str] = []
        for row in data.get("ParsedResults", []) or []:
            parsed = str(row.get("ParsedText", "")).strip()
            if parsed:
                texts.append(parsed)
        final = "\n".join(texts).strip()
        if not final:
            raise RuntimeError("empty ocr text")
        return OcrResult(text=final, provider="ocr_space")

    @staticmethod
    def _decode_base64(data: str) -> bytes:
        raw = (data or "").strip()
        if not raw:
            raise ValueError("base64 payload is required")
        if "," in raw and raw.split(",", 1)[0].startswith("data:"):
            raw = raw.split(",", 1)[1]
        try:
            return base64.b64decode(raw)
        except Exception as exc:
            raise ValueError("invalid base64 payload") from exc

    @staticmethod
    def _mime_to_suffix(mime_type: str) -> str:
        mime = (mime_type or "").lower()
        if "wav" in mime:
            return ".wav"
        if "mp3" in mime:
            return ".mp3"
        if "m4a" in mime:
            return ".m4a"
        if "ogg" in mime:
            return ".ogg"
        return ".bin"
