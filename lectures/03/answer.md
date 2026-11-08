# 第3回 解答

## 演習

- 第1回（素のLLM）とエージェントの回答の違い：
  - 第3回でのツールを利用するエージェントは、第1回の素のLLMとは異なり、pydantic_ai.Agent オブジェクトの初期化時に instruction パラメータの値として文字列で与えたシステムプロンプトで指示されたツールを利用し、可能な限りの範囲に対して指定されたデータを適用して回答を返した。さらに、指定されたデータに情報がない場合は、LLM自身が事前学習で習得していたものと考えられる知識を指定データが適用できなかった範囲のみ適用して回答した。
  - `--trace` で見えたツール呼び出し（ツール名と引数）：
    - ツール名: search_glossary
    - 引数: 質問文において問題対象として自然言語指定した語
    - 1つの質問での LLM 呼び出し回数（`requests`）：
      - search_glossary が呼び出された回数 + 1
    - 追加したツールと、docstring に書いた説明：
      - 追加したツール:
        - 
        ```python 
        # agent.py
        INSTRUCTIONS = """\
        あなたはAIエンジニアリング講座（AIE2026）の学習支援エージェントです。
        - 用語や講座に固有のことを答える前に、必ず search_glossary で用語集を確認する。
        - 回の内容を聞かれたら get_lecture_summary を使う。
        - 「第2回の確認問題を出して」のように、復習用の問題を求められたら make_quiz を使う。
        - 用語集に見つからないことは、推測で断定せず「用語集にはない」と伝える。
        - 回答の最後に、関係する回（第N回）を示す。
        - 宿題の答えそのものは書かず、考え方のヒントで導く。
        """
        agent.tool_plain(tools.make_quiz)


        # tools.py
        import random
        def make_quiz(lecture: int) -> str:
          """
          指定した回の用語から1問を選び、確認問題と答えを返す。

         「第2回の確認問題を出して」のように、復習用の問題を求められたときに使う。
          """
          items = [item for item in load_glossary() if item["lecture"] == lecture]
          if not items:
            return f"第{lecture}回の講義は存在しません。"

            term = random.choice(items)
            return json.dumps(
                {
                    "question": f"「{term['term']}」の意味は？",
                    "answer": str(term["definition"]),
                },
                ensure_ascii=False,
            )
        ```
    - 講義内容との関連有無、及び、 search_glossary でのヒット有無による動作の違い:
        - 指定ツール search_glossary で検索ヒットする語について質問した場合
          - 質問:
            - AI Agentとは何ですか？
          - 回答:
            - AIエージェントとは、大規模言語モデル（LLM）が自ら判断してツールを呼び出し、その実行結果を見てさらに次の行動を決定するというループ（循環）を通じて、与えられた目的を達成するシステムのことを指します。その基本構造は**「モデル ＋ ループ ＋ ツール」**で構成されており、人間のように自律的に考えてタスクを遂行できる点が特徴です。（第3回）
          - trace:
            - [tool call]   search_glossary({'query': 'AI Agent'})
            - [tool return] search_glossary -> [{"term": "AIエージェント", "lecture": 3, "definition": "LLMが自分で判断してツールを呼び出し、その結果を見てさらに次の行動を決める、というループで目的を達成するシステム。基本構造は「モデル＋ル…
            - [usage] RunUsage(cost=Decimal('0.0005651'), details={'text_prompt_tokens': 942}, input_text_tokens=942, input_tokens=942, output_tokens=113, requests=2, tool_calls=1)
        - 指定ツール search_glossary で検索ヒットしないが、講義内容に関連する語について質問した場合
          - 質問:
            - 深層学習とは何ですか？
          - 回答:
            - 用語集には「深層学習」という用語は見つかりませんでした。一般的に深層学習（ディープラーニング）は、多層のニューラルネットワークを用いた機械学習の手法の一つであり、コンピュータがデータから自動的に特徴量を抽出し、複雑なパターンや関係性を学習する技術を指します。関連する回：第1回、第2回
          - trace:
            - [tool call]   search_glossary({'query': '深層学習'})
            - [tool return] search_glossary -> 用語集に「深層学習」は見つかりませんでした。…
            - [usage] RunUsage(cost=Decimal('0.0005096'), details={'text_prompt_tokens': 882}, input_text_tokens=882, input_tokens=882, output_tokens=98, requests=2, tool_calls=1)
        - 指定ツール search_glossary で検索ヒットせず、講義内容にも関連しない語について質問した場合
          - 質問:
            - 深層水とは何ですか？
          - 回答:
            - 「深層水」について用語集を検索いたしましたが、このAIエンジニアリング講座（AIE2026）の用語集には登録されていません。一般的に「深層水（海洋深層水など）」は海洋学や環境科学の用語として知られていますが、本講座のAIエンジニアリングの文脈においては特定の定義や扱いを持つ用語として含まれていないようです。（関連する回：該当なし）
          - trace:
            - [tool call]   search_glossary({'query': '深層水'})
            - [tool return] search_glossary -> 用語集に「深層水」は見つかりませんでした。…
            - [usage] RunUsage(cost=Decimal('0.0005471'), details={'text_prompt_tokens': 882}, input_text_tokens=882, input_tokens=882, output_tokens=113, requests=2, tool_calls=1)
        - 指定ツール search_glossary で検索ヒットする語としない語の組み合わせで、どちらも講義内容にも関連する語について質問した場合
          - 質問:
            - 深層学習とAI Agentの関係を説明して」
          - 回答:
            - 講座の用語集には「深層学習」の登録がありませんでした。一方で、AIエージェントについては第3回（および第1回）で扱われています。用語集における「AIエージェント」の定義は、**LLM（大規模言語モデル）が自分で判断してツールを呼び出し、その結果を見てさらに次の行動を決める、というループで目的を達成するシステム**（基本構造は「モデル＋ループ＋ツール」）とされています。深層学習はAI（人工知能）やLLMを支える基盤技術（ニューラルネットワークを用いた学習手法）であり、AIエージェントの頭脳として機能するLLMの実現に不可欠な役割を担っています。関連する回：第3回（AIエージェント）、第1回（コーディングエージェント）
          - trace:
            - [tool call]   search_glossary({'query': '深層学習'})
            - [tool call]   search_glossary({'query': 'AI Agent'})
            - [tool return] search_glossary -> 用語集に「深層学習」は見つかりませんでした。…
            - [tool return] search_glossary -> [{"term": "AIエージェント", "lecture": 3, "definition": "LLMが自分で判断してツールを呼び出し、その結果を見てさらに次の行動を決める、というループで目的を達成するシステム。基本構造は「モデル＋ル…
            - [tool call]   search_glossary({'query': 'エージェント'})
            - [tool return] search_glossary -> [{"term": "AIエージェント", "lecture": 3, "definition": "LLMが自分で判断してツールを呼び出し、その結果を見てさらに次の行動を決める、というループで目的を達成するシステム。基本構造は「モデル＋ル…
            - [usage] RunUsage(cost=Decimal('0.0011432'), details={'text_prompt_tokens': 1869}, input_text_tokens=1869, input_tokens=1869, output_tokens=233, requests=3, tool_calls=3)
        - 指定ツール search_glossary で検索ヒットする語としない語の組み合わせで、片方のみ講義内容にも関連する語について質問した場合
          - 質問:
            - 深層水とAI Agentの関係を説明して
          - 回答:
            - 「深層水」という用語は、本講座の用語集には登録されていないようです。そのため、AIエンジニアリングや本講座の範囲において、深層水と「AI Agent（AIエージェント）」を直接結びつける特定の技術的関係性は定義されていません。（※もし一般的な海洋深層水の冷却技術をデータセンターの省電力化に用いる文脈などを指している場合はAIインフラ側の話題になりますが、講座内のAI Agent構造とは直接関連しないため、用語集には含まれていません。）もし講座内で別の用語との組み合わせについて意図されていた場合は、お気軽にもう一度お知らせください。関連する回：第3回（AIエージェントの基礎）
        - trace:
            - [tool call]   search_glossary({'query': 'AI Agent'})
            - [tool return] search_glossary -> [{"term": "AIエージェント", "lecture": 3, "definition": "LLMが自分で判断してツールを呼び出し、その結果を見てさらに次の行動を決める、というループで目的を達成するシステム。基本構造は「モデル＋ル…
            - [tool call]   search_glossary({'query': '深層水'})
            - [tool return] search_glossary -> 用語集に「深層水」は見つかりませんでした。…
            - [usage] RunUsage(cost=Decimal('0.0009259'), details={'text_prompt_tokens': 1528}, input_text_tokens=1528, input_tokens=1528, output_tokens=187, requests=3, tool_calls=2)
        - 指定ツール search_glossary で検索ヒットしない語のみの組み合わせで、片方のみ講義内容にも関連する語について質問した場合「深層水と深層学習の関係を説明して」
        - 回答:
            - 用語集を検索いたしましたが、「深層学習」および「深層水」に関する定義や関係性についての記載は講座の用語集にはありませんでした。AIエンジニアリングにおける「深層学習（ディープラーニング）」は、多層のニューラルネットワークを用いた機械学習の手法であり、海洋の「深層水」との直接的な科学的関係や共通の概念は、一般的なAI技術の文脈では特に定義されていません。（関係する回：用語集未登録）関連する回：第1回、第2回

## 宿題

- 取り組んだレベル：基礎
- やったこと：
- 結果：
- 気づき・疑問：

- 取り組んだレベル：基礎 / 実装 / 発展
- やったこと：
- 結果：
- 気づき・疑問：
