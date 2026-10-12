"""Backend choice for the signed-in CLI streaming packages.

Loads pages/ai/stream.py without importing biblemateweb, so the test does not
merge new keys into ~/biblemate/biblemateweb.config.
"""
import importlib.util
import inspect
import re
import sys
import types
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STREAM_PATH = ROOT / "package" / "biblemateweb" / "pages" / "ai" / "stream.py"
INIT_PATH = ROOT / "package" / "biblemateweb" / "__init__.py"


def _ensure(name):
    if name not in sys.modules:
        sys.modules[name] = types.ModuleType(name)
    return sys.modules[name]


def _load_stream():
    agentmake = _ensure("agentmake")
    agentmake.agentmake = None
    agentmake.DEFAULT_AI_BACKEND = "googleai"
    agentmake.unpack_instruction_content = lambda text: text
    agentmake.unpack_system_content = lambda text: text
    _ensure("agentmake.utils")
    text_wrapper = _ensure("agentmake.utils.text_wrapper")
    text_wrapper.get_stream_event_text = lambda *args, **kwargs: ""
    reader = _ensure("agentmake.utils.read_assistant_response")
    reader.is_openai_style = lambda *args, **kwargs: False

    nicegui = _ensure("nicegui")
    nicegui.ui = types.SimpleNamespace()
    nicegui.app = types.SimpleNamespace(storage=types.SimpleNamespace(user={}))
    nicegui.run = types.SimpleNamespace()

    biblemateweb = _ensure("biblemateweb")
    biblemateweb.config = types.SimpleNamespace()
    biblemateweb.get_translation = lambda text: text
    biblemateweb.DEFAULT_MESSAGES = []

    spec = importlib.util.spec_from_file_location("bm_stream_under_test", STREAM_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


STREAM = _load_stream()


class ChooseSubscriptionBackendTests(unittest.TestCase):
    def flags(self, **overrides):
        base = {name: False for _backend, show, use, _package, _prefixes in STREAM._SUBSCRIPTION_BACKENDS for name in (show, use)}
        base.update(overrides)
        return base

    def test_explicit_choice_requires_show_flag(self):
        flags = self.flags(show_claude_code=True, show_antigravity=True)
        self.assertEqual(STREAM.choose_subscription_backend("claude", "", "googleai", flags), "claude")
        self.assertEqual(STREAM.choose_subscription_backend("antigravity", "secret", "", flags), "antigravity")
        hidden = self.flags()
        self.assertIsNone(STREAM.choose_subscription_backend("claude", "secret", "googleai", hidden))
        self.assertIsNone(STREAM.choose_subscription_backend("grok", "", "googleai", hidden))

    def test_default_uses_first_enabled_subscription(self):
        self.assertEqual(
            STREAM.choose_subscription_backend("default", "", "", self.flags(use_grok_build_for_default=True, use_claude_code_for_default=True)),
            "grok",
        )
        self.assertEqual(
            STREAM.choose_subscription_backend("", "", "googleai", self.flags(use_claude_code_for_default=True, use_antigravity_for_default=True)),
            "claude",
        )
        self.assertEqual(
            STREAM.choose_subscription_backend("default", "secret", "openai", self.flags(use_antigravity_for_default=True)),
            "antigravity",
        )

    def test_api_key_on_another_backend_stays_with_agentmake(self):
        flags = self.flags(show_grok_build=True, use_claude_code_for_default=True)
        self.assertIsNone(STREAM.choose_subscription_backend("openai", "secret", "claude", flags))
        self.assertEqual(STREAM.choose_subscription_backend("grok", "secret", "openai", flags), "grok")

    def test_server_backend_is_the_fallback(self):
        flags = self.flags()
        self.assertEqual(STREAM.choose_subscription_backend("default", "", "claude", flags), "claude")
        self.assertEqual(STREAM.choose_subscription_backend("default", "", "antigravity", flags), "antigravity")
        self.assertEqual(STREAM.choose_subscription_backend("default", "", "grok", flags), "grok")
        self.assertIsNone(STREAM.choose_subscription_backend("default", "", "googleai", flags))
        self.assertIsNone(STREAM.choose_subscription_backend("default", "", "", flags))

    def test_model_must_match_the_backend(self):
        self.assertEqual(STREAM.subscription_model("grok", "grok-4.7"), "grok-4.7")
        self.assertEqual(STREAM.subscription_model("grok", "Grok-4.7"), "Grok-4.7")
        self.assertIsNone(STREAM.subscription_model("grok", "sonnet"))
        self.assertEqual(STREAM.subscription_model("claude", "sonnet"), "sonnet")
        self.assertEqual(STREAM.subscription_model("claude", "Opus"), "Opus")
        self.assertEqual(STREAM.subscription_model("claude", "haiku"), "haiku")
        self.assertEqual(STREAM.subscription_model("claude", "claude-sonnet-4-5"), "claude-sonnet-4-5")
        self.assertIsNone(STREAM.subscription_model("claude", "grok-4.7"))
        self.assertIsNone(STREAM.subscription_model("claude", ""))
        self.assertEqual(STREAM.subscription_model("antigravity", "gemini-3.8-flash-high"), "gemini-3.8-flash-high")
        self.assertEqual(STREAM.subscription_model("antigravity", "Gemini 3.8 Flash (High)"), "Gemini 3.8 Flash (High)")
        self.assertIsNone(STREAM.subscription_model("antigravity", "sonnet"))

    def test_config_and_docs_list_every_flag(self):
        init_src = INIT_PATH.read_text()
        main_src = (ROOT / "package" / "biblemateweb" / "main.py").read_text()
        docs = (ROOT / "docs" / "configuration.md").read_text()
        match = re.search(r"default_config = '''(.*?)'''", init_src, re.S)
        self.assertIsNotNone(match)
        keys = []
        for item in match.group(1)[7:].split("\nconfig."):
            keys.append(item.split("=", 1)[0])
        for backend, show, use, package, _prefixes in STREAM._SUBSCRIPTION_BACKENDS:
            self.assertIn(show, keys)
            self.assertIn(use, keys)
            self.assertIn(f"config.{show}", init_src)
            self.assertIn(f"config.{use}", init_src)
            self.assertIn(f"#### `config.{show}`", docs)
            self.assertIn(f"#### `config.{use}`", docs)
            self.assertIn(package, STREAM_PATH.read_text())
            self.assertIn(backend, main_src)


class StreamTextSignatureTests(unittest.TestCase):
    def test_packages_accept_the_stream_call(self):
        packages = [item[3] for item in STREAM._SUBSCRIPTION_BACKENDS]
        for package in packages:
            module = importlib.import_module(package)
            signature = inspect.signature(module.stream_text)
            for name in ("messages", "follow_up", "system", "model", "cancel_event"):
                self.assertIn(name, signature.parameters, package)


if __name__ == "__main__":
    unittest.main()
