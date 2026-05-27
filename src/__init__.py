"""promptci — Test suite for LLM prompts. Catch regressions before they hit prod."""
from .runner import PromptTest, run_suite, PromptSuite
__version__ = "0.1.0"
__all__ = ["PromptTest", "run_suite", "PromptSuite"]
