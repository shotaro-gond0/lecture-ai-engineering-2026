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
            - 深層学習とAI Agentの関係を説明して
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
        - 指定ツール search_glossary で検索ヒットしない語のみの組み合わせで、片方のみ講義内容にも関連する語について質問した場合
          - 質問:
            - 深層水と深層学習の関係を説明して
          - 回答:
            - 用語集を検索いたしましたが、「深層学習」および「深層水」に関する定義や関係性についての記載は講座の用語集にはありませんでした。AIエンジニアリングにおける「深層学習（ディープラーニング）」は、多層のニューラルネットワークを用いた機械学習の手法であり、海洋の「深層水」との直接的な科学的関係や共通の概念は、一般的なAI技術の文脈では特に定義されていません。（関係する回：用語集未登録）
          - trace:
            - [tool call]   search_glossary({'query': '深層学習'})
            - [tool return] search_glossary -> 用語集に「深層学習」は見つかりませんでした。…
            - [usage] RunUsage(cost=Decimal('0.0005795'), details={'text_prompt_tokens': 890}, input_text_tokens=890, input_tokens=890, output_tokens=125, requests=2, tool_calls=1)

## 宿題

- 取り組んだレベル：基礎
- やったこと： INSTRUCTIONS の変更
  - 変更前:
    - """\
    あなたはAIエンジニアリング講座（AIE2026）の学習支援エージェントです。
      - 用語や講座に固有のことを答える前に、必ず search_glossary で用語集を確認する。
      - 回の内容を聞かれたら get_lecture_summary を使う。
      - 「第2回の確認問題を出して」のように、復習用の問題を求められたら make_quiz を使う。
      - 用語集に見つからないことは、推測で断定せず「用語集にはない」と伝える。
      - 回答の最後に、関係する回（第N回）を示す。
      - 宿題の答えそのものは書かず、考え方のヒントで導く。
      """
  - 変更後:
    - """\
    あなたはAIエンジニアリング講座（AIE2026）の学習支援エージェントです。
      - **回答には、可能な限り、根拠となる参照論文を併記する。**
      - **講義内容と明示的に無関係な内容について質問された場合には明示的な回答を避け、回答末尾に警告を追記する。例えば、「ハンバーグの作り方を教えてください。」という質問に対しては、「警告: 無関係な概念の質問 -- キーワード: ハンバーグ / カテゴリ: 料理」という警告文を末尾に追記する。**
      - 用語や講座に固有のことを答える場合には、**必要に応じて** search_glossary で用語集を確認する。
      - 回の内容を聞かれたら get_lecture_summary を使う。
      - 「第2回の確認問題を出して」のように、復習用の問題を求められたら make_quiz を使う。
      - 用語集に見つからないことは、推測で断定せず「用語集にはない」と伝える。
      - 回答の最後に、関係する回（第N回）を示す。
      - 宿題の答えそのものは書かず、考え方のヒントで導く。
      """
- 結果：
  - AI Agentとは何ですか？
    - 回答:
      ```AIエージェント（AI Agent）とは、大規模言語モデル（LLM）を中核に据え、**「モデルが自分で判断してツールを呼び出し、その結果を見てさらに次の行動を決める」という自律的なループを回すことで、与えられた目的を達成するシステム**のことです。
      
      基本構造は主に以下の3つで構成されます。
      1. **モデル（LLM）**: 状況を理解し、次に何をすべきかを判断する頭脳。
      2. **ループ**: 思考・行動・観察を繰り返す仕組み。
      3. **ツール**: Web検索や計算機、外部APIなど、モデルが外部環境とやり取りするために使う手段。

      ### 参照論文・参考情報
      AIエージェントの自律的なタスク遂行に関する代表的な研究として、以下の論文が挙げられます。
      * **ReAct (Reasoning and Acting)**: LLMに「思考（Reason）」と「行動（Act）」を交互に行わせることで、複雑なタスクや推論を正確に行わせるフレームワーク。
      * *文献*: Yao, S., et al. (2022). "ReAct: Synergizing Reasoning and Acting in Language Models." arXiv preprint arXiv:2210.03629.

      関係する回: 第3回
    - trace:
      - [tool call]   search_glossary({'query': 'AI Agent'})
      - [tool return] search_glossary -> [{"term": "AIエージェント", "lecture": 3, "definition": "LLMが自分で判断してツールを呼び出し、その結果を見てさらに次の行動を決める、というループで目的を達成するシステム。基本構造は「モデル＋ル…
      - [usage] RunUsage(cost=Decimal('0.0011049'), details={'text_prompt_tokens': 1158}, input_text_tokens=1158, input_tokens=1158, output_tokens=303, requests=2, tool_calls=1)
  - 深層学習とは何ですか？
    - 回答:
      ```用語集には「深層学習」の直接的な定義はありませんでしたが、深層学習（ディープラーニング）は、多層のニューラルネットワークを用いてデータから特徴量を自動的に学習し、高精度な予測や分類を行う機械学習の手法の一つです。
      
      伝統的な機械学習では人間が特徴量を設計する必要がありましたが、深層学習では多層構造（深いネットワーク）により、データの持つ複雑な表現をエンドツーエンドで学習できる点が特徴です。
      
      【根拠となる代表的な論文】
      * LeCun, Y., Bengio, Y., & Hinton, G. (2015). "Deep learning." *Nature*, 521(7553), 436-444.（多層のニューラルネットワークによる表現学習の仕組みと、コンピュータビジョンや音声認識などへの応用を総括した代表的な論文です。）
      
      関係する回: 第1回、第2回
    - trace:
      - [tool call]   search_glossary({'query': '深層学習'})
      - [tool return] search_glossary -> 用語集に「深層学習」は見つかりませんでした。…
      - [usage] RunUsage(cost=Decimal('0.0008894'), details={'text_prompt_tokens': 1098}, input_text_tokens=1098, input_tokens=1098, output_tokens=224, requests=2, tool_calls=1)
  - 深層水とは何ですか？
    - 回答:
      ```深層水とは一般に、太陽光が届かない水深200m以深の海洋深層水を指すことが多いですが、AIエンジニアリングや本講座（AIE2026）の文脈においては、講義内容や公式の用語集に登録されていない概念です。
      
      そのため、講座の内容とは明示的に無関係な質問となります。
      
      関係する回: 該当なし
      
      ---
      警告: 無関係な概念の質問 -- キーワード: 深層水 / カテゴリ: 海洋科学・自然科学
    - trace:
      - [usage] RunUsage(cost=Decimal('0.0004450'), details={'text_prompt_tokens': 525}, input_text_tokens=525, input_tokens=525, output_tokens=115, requests=1)
  - 深層学習とAI Agentの関係を説明して
    - 回答:
      ```深層学習（Deep Learning）とAIエージェント（AI Agent）は、現代のAI技術において密接に結びついています。一言で言えば、**深層学習はAIエージェントの「頭脳」や「知覚・言語能力」を支える基盤技術**であり、AIエージェントはその深層学習（特に大規模言語モデルなど）を中核に据えて**「自律的に目的を達成するシステム」**として発展したものです。
      
      それぞれの関係を整理すると、以下のようになります。
      
      1. **基盤としての深層学習（頭脳と認識）**
      AIエージェントの中核には、多くの場合、大規模言語モデル（LLM）などの深層学習モデルが使われています。深層学習が持つ高度な自然言語処理能力やパターン認識、推論能力があるからこそ、エージェントはユーザーの複雑な指示を理解し、次にどのような行動をとるべきかを判断できます。
      
      2. **自律的なループ機構（AIエージェントとしての仕組み）**
      AIエージェントは、単に深層学習モデルが一度テキストを出力するだけでなく、「モデル＋ループ＋ツール」という構造を持ちます。深層学習モデルが自分で考え、外部ツール（Web検索やAPIなど）を呼び出し、その結果を再び深層学習モデルに入力して次の行動を決めるという**自律的なループ**を回すことで、一連のタスクを遂行します（第3回）。
      
      ### 参考文献・根拠
      - レック, J. et al. (2023). *Foundation Models for Generalist Agents*. arXiv preprint arXiv:2310.xxxxx. （※一般的なAIエージェントと基盤モデルの関係に関するサーベイ論文）
      - 講座内用語集: 第3回「AIエージェント」
      
      関連する回：第3回
    - trace:
      - [tool call]   search_glossary({'query': 'AI Agent'})
      - [tool return] search_glossary -> [{"term": "AIエージェント", "lecture": 3, "definition": "LLMが自分で判断してツールを呼び出し、その結果を見てさらに次の行動を決める、というループで目的を達成するシステム。基本構造は「モデル＋ル…
      - [tool call]   search_glossary({'query': '深層学習'})
      - [tool return] search_glossary -> 用語集に「深層学習」は見つかりませんでした。…
      - [usage] RunUsage(cost=Decimal('0.0016606'), details={'text_prompt_tokens': 1852}, input_text_tokens=1852, input_tokens=1852, output_tokens=442, requests=3, tool_calls=2)
  - 深層水とAI Agentの関係を説明して
    - 回答:
    ```「深層水」（海洋深層水など）とAI Agent（AIエージェント）の直接的な関係性について、本講座の講義内容やAIエンジニアリングの用語集には該当する定義や関係性は含まれておりません。
    
    AIエージェントは、LLM（大規模言語モデル）等を基盤とし、自律的に思考・計画・ツールの利用を行ってタスクを遂行するシステムを指します（参考: AIE2026 関連講義）。一方で「深層水」は海洋学や環境科学、あるいは冷却技術などの分野の用語であり、AIエンジニアリングの標準的なカリキュラムや用語集の範囲外となります。
    
    もし「深層水」ではなく、AIの学習・運用におけるデータセンターの冷却（海洋深層水を利用した省電力データセンターなど）といった文脈についてお知りになりたい場合は、講義内の関連トピックとして改めてご質問ください。
    
    ---
    警告: 無関係な概念の質問 -- キーワード: 深層水 / カテゴリ: 海洋学・環境科学
    
    関連する回: 対象外（講義内容と無関係なため）
    - trace:
      - [usage] RunUsage(cost=Decimal('0.0007759'), details={'text_prompt_tokens': 528}, input_text_tokens=528, input_tokens=528, output_tokens=247, requests=1)
  - 深層水と深層学習の関係を説明して
    - 回答:
    ```深層水（海洋深層水）と深層学習（ディープラーニング）の間には、科学的な関連性や講座内で直接扱われるような直接的なつながりはありません。
    
    「深層（Deep）」という言葉が共通しているため混同されやすいですが、深層水は海洋学や環境科学の分野で扱われる水資源や環境要因であり、深層学習は人工知能（AI）や機械学習における多層ニューラルネットワークを用いた学習手法を指します。
    
    関連回: 該当なし
    
    警告: 無関係な概念の質問 -- キーワード: 深層水 / カテゴリ: 海洋科学・自然科学
    - trace:
      - [usage] RunUsage(cost=Decimal('0.0005037'), details={'text_prompt_tokens': 529}, input_text_tokens=529, input_tokens=529, output_tokens=138, requests=1)
  - 気づき・疑問：
    - INSTRUCTIONS で指定したシステムプロンプトの指示に忠実に従い、順序と形式におちて定型的な回答をする。
    - 講義内容と関連するか否かと、 search_glossary でヒットするか否かをそれぞれ区別して
    - 講義と無関係な概念には明示的に回答せず警告を表示するように指示し、ツール利用を「必ず」ではなく「必要に応じて」とすると、search_glossary でヒットする語が質問文に含まれていても無関係な概念が質問文に含まれていると search_glossary ツールを呼ばないで事前学習知識のみによって概要を説明した上で講義と無関係である旨と警告を回答し、別途指示している論文の参照も回答に含まれない。つまり、回答を禁止するシステムプロンプト指示を回答に情報を含める指示よりも優先している傾向がみてとれる。