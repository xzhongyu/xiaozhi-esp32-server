import os
import sys
import types


PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, PROJECT_ROOT)

config_module = types.ModuleType("config")
logger_module = types.ModuleType("config.logger")


class _DummyLogger:
    def bind(self, **kwargs):
        return self

    def debug(self, *args, **kwargs):
        return None

    def info(self, *args, **kwargs):
        return None

    def warning(self, *args, **kwargs):
        return None

    def error(self, *args, **kwargs):
        return None


def setup_logging():
    return _DummyLogger()


logger_module.setup_logging = setup_logging
config_module.logger = logger_module
sys.modules.setdefault("config", config_module)
sys.modules.setdefault("config.logger", logger_module)

from core.providers.asr.utils import lang_tag_filter


def main() -> None:
    tagged = "<|zh|><|SAD|><|Speech|><|withitn|>你好啊，测试测试。"
    result = lang_tag_filter(tagged)
    assert isinstance(result, dict)
    assert result["language"] == "zh"
    assert result["content"] == "你好啊，测试测试。"

    plain = "plain text"
    result = lang_tag_filter(plain)
    assert isinstance(result, str)
    assert result == "plain text"

    parsed = lang_tag_filter(plain)
    content = parsed.get("content", "") if isinstance(parsed, dict) else parsed
    assert content == "plain text"


if __name__ == "__main__":
    main()
