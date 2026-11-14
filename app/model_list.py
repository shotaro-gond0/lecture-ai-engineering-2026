"""List Gemini models available for content generation.

Usage:
    uv run python -m app.model_list
"""

from google import genai

from app.config import get_api_key


def main() -> None:
    client = genai.Client(api_key=get_api_key())
    for model in client.models.list():
        if "generateContent" not in (model.supported_actions or []):
            continue
        if model.name:
            print(model.name.removeprefix("models/"))


if __name__ == "__main__":
    main()
