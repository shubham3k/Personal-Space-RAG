"""Optional vision description generation."""

import base64
from pathlib import Path

from config.settings import settings


class VisionDescriber:
    def describe(self, image_path: Path) -> dict:
        if not settings.vision_enabled:
            return {"description": "", "provider": "", "error": "Vision disabled"}
        try:
            if settings.vision_provider.lower() == "gemini":
                return self._describe_with_gemini(image_path)
            if settings.vision_provider.lower() == "groq":
                return self._describe_with_groq(image_path)
            return {"description": "", "provider": "", "error": f"Unsupported vision provider: {settings.vision_provider}"}
        except Exception as exc:
            return {"description": "", "provider": settings.vision_provider, "error": str(exc)}

    def _describe_with_gemini(self, image_path: Path) -> dict:
        if not settings.google_api_key:
            return {"description": "", "provider": "gemini", "error": "GOOGLE_API_KEY is not configured"}
        from google import genai
        from PIL import Image

        client = genai.Client(api_key=settings.google_api_key)
        with Image.open(image_path) as image:
            response = client.models.generate_content(
                model=settings.vision_model,
                contents=["Describe this image for a personal knowledge base. Include visible text, objects, people, and context.", image],
                config={"max_output_tokens": settings.vision_max_tokens},
            )
        return {"description": response.text or "", "provider": "gemini"}

    def _describe_with_groq(self, image_path: Path) -> dict:
        if not settings.groq_api_key:
            return {"description": "", "provider": "groq", "error": "GROQ_API_KEY is not configured"}
        from groq import Groq

        encoded = base64.b64encode(image_path.read_bytes()).decode("ascii")
        mime = "image/jpeg" if image_path.suffix.lower() in {".jpg", ".jpeg"} else "image/png"
        client = Groq(api_key=settings.groq_api_key)
        response = client.chat.completions.create(
            model=settings.vision_model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Describe this image for retrieval in a personal knowledge base."},
                        {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{encoded}"}},
                    ],
                }
            ],
            max_tokens=settings.vision_max_tokens,
        )
        return {"description": response.choices[0].message.content or "", "provider": "groq"}
