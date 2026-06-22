from __future__ import annotations

import base64
import threading
import time
from pathlib import Path
from typing import Iterable

from google import genai
from google.genai import types


IMAGE_MODELS_FALLBACK: tuple[str, ...] = (
    "imagen-4.0-generate-001",
    "imagen-4.0-fast-generate-001",
    "imagen-4.0-ultra-generate-001",
)
GEMINI_IMAGE_MODELS_FALLBACK: tuple[str, ...] = (
    "gemini-2.0-flash-exp",
    "gemini-2.5-flash-preview-04-17",
)


def _safe_png_name(filename: str) -> str:
    p = Path(filename.strip() or "generated_image.png")
    if p.suffix.lower() not in {".png", ".jpg", ".jpeg", ".webp"}:
        p = p.with_suffix(".png")
    return str(p)


def _extract_image_bytes(response: object) -> bytes | None:
    """
    Best-effort parser for multiple google-genai response shapes.
    """
    # Shape A: response.generated_images[].image.image_bytes
    generated_images = getattr(response, "generated_images", None)
    if generated_images:
        for item in generated_images:
            image_obj = getattr(item, "image", None)
            if image_obj and getattr(image_obj, "image_bytes", None):
                return image_obj.image_bytes

    # Shape B: response.candidates[].content.parts[].inline_data.data (base64 or bytes)
    candidates = getattr(response, "candidates", None)
    if candidates:
        for cand in candidates:
            content = getattr(cand, "content", None)
            parts = getattr(content, "parts", None) if content else None
            if not parts:
                continue
            for part in parts:
                inline_data = getattr(part, "inline_data", None)
                if not inline_data:
                    continue
                raw = getattr(inline_data, "data", None)
                if isinstance(raw, bytes):
                    return raw
                if isinstance(raw, str):
                    try:
                        return base64.b64decode(raw)
                    except Exception:
                        continue
    return None


def generate_image_with_fallback(
    api_key: str,
    prompt: str,
    filename: str,
    model_fallback: Iterable[str] | None = None,
    show_preview: bool = True,
    auto_close_seconds: int = 6,
) -> str:
    models = tuple(model_fallback) if model_fallback else IMAGE_MODELS_FALLBACK
    target_file = _safe_png_name(filename)
    client = genai.Client(api_key=api_key)
    errors: list[str] = []

    for model_name in models:
        try:
            response = client.models.generate_images(
                model=model_name,
                prompt=prompt,
            )
            image_bytes = _extract_image_bytes(response)
            if not image_bytes:
                errors.append(f"{model_name}: no image bytes in response")
                continue

            Path(target_file).write_bytes(image_bytes)
            preview_msg = ""
            if show_preview:
                preview_msg = " " + show_image_preview_and_close(
                    target_file,
                    auto_close_seconds=auto_close_seconds,
                )
            return (
                f"Image generated successfully using {model_name} and saved to {target_file}.{preview_msg}"
            )
        except Exception as exc:
            msg = _compact_error(str(exc))
            errors.append(f"{model_name}: {msg}")
            # Paid-plan block: skip remaining Imagen models and try Gemini-image route.
            if "only available on paid plans" in msg.lower():
                break

    for model_name in GEMINI_IMAGE_MODELS_FALLBACK:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_modalities=["IMAGE"],
                ),
            )
            image_bytes = _extract_image_bytes(response)
            if not image_bytes:
                errors.append(f"{model_name}: no image bytes in response")
                continue

            Path(target_file).write_bytes(image_bytes)
            preview_msg = ""
            if show_preview:
                preview_msg = " " + show_image_preview_and_close(
                    target_file,
                    auto_close_seconds=auto_close_seconds,
                )
            return (
                f"Image generated successfully using {model_name} and saved to {target_file}.{preview_msg}"
            )
        except Exception as exc:
            msg = _compact_error(str(exc))
            errors.append(f"{model_name}: {msg}")
            if "resource_exhausted" in msg.lower() or "quota exceeded" in msg.lower() or "429" in msg:
                import time
                time.sleep(3)  # Wait before trying next model on rate limit
                continue

    return "Image generation failed on all fallback models.\n" + "\n".join(errors)


def show_image_preview_and_close(path: str, auto_close_seconds: int = 6) -> str:
    """
    Show the generated image in a small popup and close automatically.
    """
    try:
        from tkinter import Tk, Label
        from PIL import Image, ImageTk
    except Exception as exc:
        return f"Preview skipped (missing GUI deps: {exc})."

    image_path = Path(path)
    if not image_path.exists():
        return "Preview skipped (file missing)."

    seconds = max(2, min(30, int(auto_close_seconds)))
    done = threading.Event()
    result_holder: dict[str, str] = {"msg": "Preview skipped."}

    def _run() -> None:
        try:
            root = Tk()
            root.title("Generated Image Preview")
            root.attributes("-topmost", True)

            img = Image.open(image_path)
            max_w, max_h = 900, 650
            img.thumbnail((max_w, max_h))
            tk_img = ImageTk.PhotoImage(img)

            label = Label(root, image=tk_img)
            label.image = tk_img
            label.pack()

            root.after(seconds * 1000, root.destroy)
            result_holder["msg"] = f"Preview shown and auto-closed in {seconds}s."
            root.mainloop()
        except Exception as exc:
            result_holder["msg"] = f"Preview failed: {exc}"
        finally:
            done.set()

    t = threading.Thread(target=_run, daemon=True)
    t.start()
    # Wait enough for window to close, but do not hang forever.
    done.wait(timeout=seconds + 5)
    if not done.is_set():
        return f"Preview started, close timeout after {seconds + 5}s."
    return result_holder["msg"]


def _compact_error(message: str) -> str:
    m = " ".join(message.split())
    # Keep the most useful part to avoid huge tool-response payloads.
    if len(m) > 380:
        m = m[:380] + "..."
    return m
