"""第1回: 改造版：素のLLMに1回だけ質問し、トークン数と応答時間を計測するスクリプト

使い方:
    uv run python -m app.ask_tat "LoRAとは何ですか？"
    uv run python -m app.ask_tat # 質問を省略すると、講座に固有の質問をする

"""

import argparse
import logging
from pathlib import Path

from google import genai
from google.genai import errors

from app.config import MODEL, MODEL_TEMPERATURE, api_error_message, get_api_key

import readline

import time

# 講座に固有の質問。正しい答えは data/glossary.json の homework-levels にある
DEFAULT_QUESTION = "AIE2026の講座の宿題にある「3レベル」とは何ですか？"

logger = logging.getLogger(__name__)


def ask(context: str) -> tuple[str, int|None, int|None, float]:

    name = MODEL if MODEL.startswith("models/") else f"models/{MODEL}"
    logger.info("Creating Gemini client for model=%s", MODEL)
    client = genai.Client(api_key=get_api_key())

    logger.info("Fetching model metadata: model=%s", name)
    model = client.models.get(model=name)
    temperature = model.temperature if MODEL_TEMPERATURE == None else MODEL_TEMPERATURE
    
    start_time = time.perf_counter()
    logger.info(
        "Sending generate_content request: model=%s, temperature=%s",
        MODEL,
        temperature,
    )
    response = client.models.generate_content(
        model=MODEL,
        contents=context,
        config={"temperature": temperature})
    end_time = time.perf_counter()
    elapsed_time = end_time - start_time

    usage = response.usage_metadata
    input_token_count = usage.prompt_token_count if usage is not None else None
    output_token_count = usage.candidates_token_count if usage is not None else None
    logger.info(
        "Received response: model=%s, input_tokens=%s, output_tokens=%s, "
        "elapsed_seconds=%.3f, has_text=%s",
        MODEL,
        input_token_count,
        output_token_count,
        elapsed_time,
        response.text is not None,
    )

    if response.text is None:
        logger.warning("Model %s returned no response text", MODEL)
        answer = ""
    else:
        answer = response.text

    return answer, input_token_count, output_token_count, elapsed_time

def list_models() -> None:
    client = genai.Client(api_key=get_api_key())
    # print("利用可能なモデル:")
    for model in client.models.list():
        print(f"{model.name}")

def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    parser = argparse.ArgumentParser(description="素のLLMに質問する")
    parser.add_argument("question", nargs="?")
    parser.add_argument(
        "--query-file",
        type=Path,
        help="ファイルから質問を読み込む（長い質問向け）",
    )
    parser.add_argument(
        "--list-models",
        action="store_true",
        help="利用可能なモデル名を表示する",
    )
    args = parser.parse_args()

    try:
        if args.list_models:
            list_models()
            return

        model = MODEL
        if args.query_file is not None and args.question is not None:
            parser.error("質問文と --query-file は同時に指定できません")
        query = (
            args.query_file.read_text(encoding="utf-8")
            if args.query_file is not None
            else args.question or DEFAULT_QUESTION
        )
        logger.info(
            "Loaded query: model=%s, source=%s, characters=%s, utf8_bytes=%s",
            MODEL,
            args.query_file if args.query_file is not None else "command line/default",
            len(query),
            len(query.encode("utf-8")),
        )
        answer, input_token_count, output_token_count, elapsed_time = ask(query)
        
    except (KeyboardInterrupt, EOFError):
        print("\n終了します。")
    except errors.APIError as e:
        logger.exception(
            "Gemini API request failed: model=%s, status=%s, message=%s",
            MODEL,
            e.code,
            e.message,
        )
        print(api_error_message(e.code, e.message)) # pyright: ignore[reportArgumentType]
        raise SystemExit(1)
    
    print(f"{model};{input_token_count};{output_token_count};{elapsed_time}")
    print("#"*60)
    print(answer)


if __name__ == "__main__":
    main()
