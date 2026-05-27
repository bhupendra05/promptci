from promptci import PromptTest, run_suite, PromptSuite

def mock_llm(prompt): return "Hello world, I am an assistant!"

def test_contains_check():
    t = PromptTest("hello", "say hi", PromptTest.contains("hello"))
    assert t.check("Hello there!")

def test_suite_pass():
    tests = [PromptTest("not empty", "hi", PromptTest.not_empty())]
    result = run_suite(tests, mock_llm)
    assert result.passed == 1 and result.failed == 0

def test_suite_fail():
    tests = [PromptTest("has xyz", "hi", PromptTest.contains("xyz"))]
    result = run_suite(tests, mock_llm)
    assert result.failed == 1
