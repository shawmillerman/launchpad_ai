import os
import mimetypes
from google import genai
from google.genai import types

class ImageIngestionPipeline:
    def __init__(self, provider="gemini"):
        self.provider = provider
        # The modern client automatically picks up GEMINI_API_KEY from your environment
        self.client = genai.Client()

    def _call_vision_api(self, image_path: str, extraction_warnings: list) -> str:
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"File not found at {image_path}")

        # Dynamically infer the image MIME type
        mime_type, _ = mimetypes.guess_type(image_path)
        if not mime_type:
            mime_type = "image/jpeg"
            extraction_warnings.append("MIME type could not be inferred; defaulting to image/jpeg.")

        # Quick validation guard
        supported_types = ["image/jpeg", "image/png", "image/webp", "image/heic", "image/heif"]
        if mime_type not in supported_types:
            extraction_warnings.append(f"Unsupported MIME type '{mime_type}'. Processing may fail.")

        try:
            with open(image_path, "rb") as f:
                image_bytes = f.read()

            if not image_bytes:
                extraction_warnings.append("Empty file binary processed.")
                return ""

            # Clean modern google-genai client syntax
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[
                    types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
                    "Transcribe all text from this image exactly. Return only the transcribed text with no commentary."
                ]
            )

            if not response.text:
                extraction_warnings.append("API returned an empty text string response.")
                return ""

            return response.text

        except Exception as e:
            extraction_warnings.append(f"Gemini API Exception occurred: {str(e)}")
            raise e

    def extract_text(self, image_path: str) -> dict:
        extraction_warnings = []
        raw_text = ""
        
        try:
            raw_text = self._call_vision_api(image_path, extraction_warnings)
        except Exception:
            # Let the pipeline structure return gracefully with the warning caught
            pass

        return {
            "source_file": image_path,
            "content": raw_text,
            "metadata": {
                "quality_signals": {
                    "extraction_warnings": extraction_warnings
                }
            }
        }