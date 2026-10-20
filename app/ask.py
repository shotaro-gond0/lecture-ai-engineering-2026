"""第1回: 素のLLMに1回だけ質問するスクリプト。

使い方:
    uv run python -m app.ask "LoRAとは何ですか？"
    uv run python -m app.ask            # 質問を省略すると、講座に固有の質問をする

ツールも会話履歴も持たない「素の」呼び出し。
講座に固有のことを聞くと、「分からない」と答えるか、一般論でもっともらしく答える
（講座の実際とは違う）ことを確かめよう。
（第3回で、用語集を検索できるエージェントにして改善する）
"""

import argparse

from google import genai
from google.genai import errors

from app.config import MODEL, MODEL_TEMPERATURE, api_error_message, get_api_key

# 講座に固有の質問。正しい答えは data/glossary.json の homework-levels にある
DEFAULT_QUESTION = "AIE2026の講座の宿題にある「3レベル」とは何ですか？"


def ask(context: str) -> str | None:
    
    name = MODEL if MODEL.startswith("models/") else f"models/{MODEL}"
    
    client = genai.Client(api_key=get_api_key())
        
    model = client.models.get(model=name)
    temperature = model.temperature if MODEL_TEMPERATURE == None else MODEL_TEMPERATURE
    
    response = client.models.generate_content(
        model=MODEL,
        contents=context,
        config={"temperature": temperature})

    # TODO(第1回 演習): response.usage_metadata から
    #   入力トークン数と出力トークン数を表示してみよう（Copilotに頼んでよい）
    usage = response.usage_metadata
    if usage is not None:
        print(f"[usage] 入力トークン数: {usage.prompt_token_count}")
        print(f"[usage] 出力トークン数: {usage.candidates_token_count}")

    return response.text


def list_models() -> None:
    client = genai.Client(api_key=get_api_key())
    # print("利用可能なモデル:")
    for model in client.models.list():
        print(f"{model.name}")


def main() -> None:
    parser = argparse.ArgumentParser(description="素のLLMに質問する")
    parser.add_argument("question", nargs="?", default=DEFAULT_QUESTION)
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

        print(f"[model] {MODEL}")
        print(f"[質問] {args.question}\n")
        print(ask(args.question))
    except errors.APIError as e:
        print(api_error_message(e.code, e.message))
        raise SystemExit(1)


if __name__ == "__main__":
    main()
