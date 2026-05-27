# promptci

> **Test suite for LLM prompts. Catch regressions before they hit production**

[![Python](https://img.shields.io/badge/python-3.10+-blue)](https://www.python.org)
[![PyPI](https://img.shields.io/pypi/v/promptci)](https://pypi.org/project/promptci)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

## Install

```bash
pip install promptci
```

## The problem

You edit a prompt. The new version sounds better. You ship it. Three edge cases that worked before now fail silently. There's no test suite for prompts.

## Usage

```python
from promptci import PromptSuite, PromptTest
import anthropic

client = anthropic.Anthropic()

def call_claude(prompt: str) -> str:
    msg = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=256,
        messages=[{"role": "user", "content": prompt}]
    )
    return msg.content[0].text

suite = PromptSuite(
    prompt_template="You are a helpful assistant. {input}",
    model_fn=call_claude,
)

suite.add(PromptTest("responds in english",  "Say hello",          PromptTest.contains("hello")))
suite.add(PromptTest("gives non-empty reply", "Tell me a joke",    PromptTest.not_empty()))
suite.add(PromptTest("returns valid JSON",    "Return {\"ok\": 1}", PromptTest.json_has_keys("ok")))

result = suite.run()

# promptci: 3/3 passed
# ✓ responds in english
# ✓ gives non-empty reply
# ✓ returns valid JSON

assert result.failed == 0, str(result)
```

### In CI

```bash
pip install promptci
python run_prompt_tests.py  # exits non-zero if any prompt test fails
```

## Architecture

```
promptci/
├── promptci/
│   ├── __init__.py   # public API
│   └── *.py          # core implementation
└── tests/
    └── test_*.py     # 3 passed — no API key needed
```

## License

MIT © [bhupendra05](https://github.com/bhupendra05)

---

*Part of the [bhupendra05 developer tools collection](https://github.com/bhupendra05)*
