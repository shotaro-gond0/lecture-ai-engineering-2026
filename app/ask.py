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

import readline

# 講座に固有の質問。正しい答えは data/glossary.json の homework-levels にある
DEFAULT_QUESTION = "AIE2026の講座の宿題にある「3レベル」とは何ですか？"


def ask(context: str) -> str:

    name = MODEL if MODEL.startswith("models/") else f"models/{MODEL}"
    input_context = context
    client = genai.Client(api_key=get_api_key())

    model = client.models.get(model=name)
    temperature = model.temperature if MODEL_TEMPERATURE == None else MODEL_TEMPERATURE

    response = client.models.generate_content(
        model=MODEL,
        contents=input_context,
        config={"temperature": temperature})

    # TODO(第1回 演習): response.usage_metadata から
    #   入力トークン数と出力トークン数を表示してみよう（Copilotに頼んでよい）
    usage = response.usage_metadata
    if usage is not None:
        print("#" * 60)
        print(f"[usage] 入力トークン数: {usage.prompt_token_count}")
        print(f"[usage] 出力トークン数: {usage.candidates_token_count}")
        print("#" * 60)

    if response.text is None:
        print(
            f"Warning: {MODEL} did not return valid response text for the context: \n{context}")
        answer = ""
    else:
        answer = response.text

    return answer


def compaction(context: str) -> str:
    
    name = MODEL if MODEL.startswith("models/") else f"models/{MODEL}"
    input_context = context
    client = genai.Client(api_key=get_api_key())

    model = client.models.get(model=name)
    input_token_limit = model.input_token_limit
    compaction_trigger = input_token_limit - \
        (input_token_limit // 5) if input_token_limit is not None else 0

    input_token_count = client.models.count_tokens(
        model=MODEL,
        contents=context
    ).total_tokens

    if input_token_limit is None:
        print("*" * 60)
        print(
            f"Warning: No input_token_limit info provided for {MODEL} -- No compaction for long context.")
        print("*" * 60)
    elif input_token_count is None:
        print("*" * 60)
        print(
            f"Warning: No input_token_count info provided for {MODEL} -- No compaction for long context.")
        print("*" * 60)
    elif input_token_count > compaction_trigger:

        response = client.models.generate_content(
            model=MODEL,
            contents=f"以下の内容を要約し、3分の1程度の長さにしてください。短くした要約内容のみを出力し、それ以外は一切内容を追加してはいけません。¥n {input_context}",
            config={"temperature": 0.0})

        usage = response.usage_metadata
        if usage is not None:
            print("*" * 60)
            print("Compaction: コンテクストが長すぎるので要約します。")
            print(f"[usage] コンテクスト入力トークン数: {usage.prompt_token_count}")
            print(f"[usage] 要約出力トークン数: {usage.candidates_token_count}")
            print("*" * 60)

        if response.text is None:
            print(
                f"Warning: {MODEL} が有効なレスポンスを返さなかったためコンテクストの要約ができません。")
        else:
            input_context = response.text
    
    return input_context


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
    parser.add_argument(
        "--non-interactive",
        action="store_true",
        help="質問に1回回答したら終了する",
    )
    args = parser.parse_args()
    context = ""

    try:
        if args.list_models:
            list_models()
            return

        print(f"[model]: {MODEL}")
        query = args.question
        while query not in ("quit", "exit"):
            if query == "dump":
                print(context)
            else:
                context += f"[User]:\n{query}\n"
                context = compaction(context)
                answer = ask(context)
                answer = "[System]:\n" + answer + \
                    "\n" if not answer.startswith(
                        "[System]") else answer + "\n"
                context += answer
                print(answer)
            if args.non_interactive:
                break
            query = input("[User]:\n").strip()

        print("終了します。")
    except (KeyboardInterrupt, EOFError):
        print("\n終了します。")
    except errors.APIError as e:
        print(api_error_message(e.code, e.message))
        raise SystemExit(1)


if __name__ == "__main__":
    main()
