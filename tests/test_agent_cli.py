"""CLI tests for the Pydantic AI agent's interactive conversation."""

from pydantic_ai.models.test import TestModel

from app import agent as agent_module


# 対話モード（会話履歴の引き継ぎ）は upstream マージで変更されたため、テスト対象から除外中。
# 復旧するには、以下のコメントを外す（かつ app/agent.py に対話ループと message_history を戻す）。
# def test_interactive_mode_passes_history_between_questions(monkeypatch):
#     monkeypatch.setattr("sys.argv", ["app.agent", "最初の質問"])
#     model = TestModel(call_tools=[])
#     monkeypatch.setattr(agent_module, "build_model", lambda: model)
#
#     calls = []
#     results = []
#     real_agent = agent_module.agent
#
#     class RecordingAgent:
#         def run_sync(self, user_prompt, *, model, message_history):
#             calls.append((user_prompt, message_history))
#             result = real_agent.run_sync(
#                 user_prompt,
#                 model=model,
#                 message_history=message_history,
#             )
#             results.append(result)
#             return result
#
#     monkeypatch.setattr(agent_module, "agent", RecordingAgent())
#     inputs = iter(["続きの質問", "exit"])
#     monkeypatch.setattr("builtins.input", lambda prompt: next(inputs))
#
#     agent_module.main()
#
#     assert [prompt for prompt, _ in calls] == ["最初の質問", "続きの質問"]
#     assert calls[0][1] is None
#     assert calls[1][1] == results[0].all_messages()

# --non-interactive は upstream マージで廃止されたため、テスト対象から除外中。
# 復旧するには、以下のコメントを外す（かつ app/agent.py に同オプションを戻す）。
# def test_non_interactive_mode_runs_once(monkeypatch):
#     monkeypatch.setattr(
#         "sys.argv",
#         ["app.agent", "--non-interactive", "質問"],
#     )
#     model = TestModel(call_tools=[])
#     monkeypatch.setattr(agent_module, "build_model", lambda: model)
#     calls = []
#     real_agent = agent_module.agent
#
#     class RecordingAgent:
#         def run_sync(self, user_prompt, *, model, message_history):
#             calls.append(user_prompt)
#             return real_agent.run_sync(
#                 user_prompt,
#                 model=model,
#                 message_history=message_history,
#             )
#
#     monkeypatch.setattr(agent_module, "agent", RecordingAgent())
#
#     def unexpected_input(prompt):
#         raise AssertionError("input should not be called")
#
#     monkeypatch.setattr("builtins.input", unexpected_input)
#     agent_module.main()
#
#     assert calls == ["質問"]
