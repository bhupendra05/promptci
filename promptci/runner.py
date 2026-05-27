from __future__ import annotations
import re, json
from dataclasses import dataclass, field
from typing import Callable, Any

@dataclass
class PromptTest:
    name: str
    input: str
    check: Callable[[str], bool]
    description: str = ""

    @staticmethod
    def contains(text: str) -> Callable[[str], bool]:
        return lambda output: text.lower() in output.lower()

    @staticmethod
    def matches(pattern: str) -> Callable[[str], bool]:
        return lambda output: bool(re.search(pattern, output, re.I))

    @staticmethod
    def json_has_keys(*keys: str) -> Callable[[str], bool]:
        def _check(output: str) -> bool:
            try:
                data = json.loads(output)
                return all(k in data for k in keys)
            except Exception:
                return False
        return _check

    @staticmethod
    def not_empty() -> Callable[[str], bool]:
        return lambda output: bool(output.strip())

@dataclass
class TestResult:
    test: PromptTest
    passed: bool
    output: str
    error: str = ""

@dataclass
class SuiteResult:
    results: list[TestResult] = field(default_factory=list)

    @property
    def passed(self): return sum(1 for r in self.results if r.passed)
    @property  
    def failed(self): return sum(1 for r in self.results if not r.passed)
    @property
    def total(self): return len(self.results)

    def __str__(self):
        lines = [f"\npromptci: {self.passed}/{self.total} passed"]
        for r in self.results:
            status = "✓" if r.passed else "✗"
            lines.append(f"  {status} {r.test.name}")
            if not r.passed:
                lines.append(f"      output: {r.output[:100]!r}")
                if r.error: lines.append(f"      error:  {r.error}")
        return "\n".join(lines)

class PromptSuite:
    """Collection of prompt tests with a shared prompt template."""

    def __init__(self, prompt_template: str, model_fn: Callable[[str], str]):
        """
        ::

            from promptci import PromptSuite, PromptTest

            def call_claude(prompt): ...  # your LLM caller

            suite = PromptSuite(
                prompt_template="You are a helpful assistant. {input}",
                model_fn=call_claude,
            )
            suite.add(PromptTest("says hello", "Say hello", PromptTest.contains("hello")))
            suite.add(PromptTest("non-empty", "Tell me a joke", PromptTest.not_empty()))

            result = suite.run()
            assert result.failed == 0
        """
        self.template = prompt_template
        self.model_fn = model_fn
        self.tests: list[PromptTest] = []

    def add(self, test: PromptTest):
        self.tests.append(test)
        return self

    def run(self, verbose: bool = True) -> SuiteResult:
        result = SuiteResult()
        for test in self.tests:
            prompt = self.template.format(input=test.input)
            try:
                output = self.model_fn(prompt)
                passed = test.check(output)
                result.results.append(TestResult(test=test, passed=passed, output=output))
            except Exception as e:
                result.results.append(TestResult(test=test, passed=False, output="", error=str(e)))
        if verbose:
            print(result)
        return result

def run_suite(tests: list[PromptTest], model_fn: Callable[[str], str]) -> SuiteResult:
    """Shorthand: run a list of PromptTests against a model function."""
    result = SuiteResult()
    for test in tests:
        try:
            output = model_fn(test.input)
            passed = test.check(output)
            result.results.append(TestResult(test=test, passed=passed, output=output))
        except Exception as e:
            result.results.append(TestResult(test=test, passed=False, output="", error=str(e)))
    print(result)
    return result
