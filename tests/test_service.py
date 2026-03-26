import unittest

from oss_pr_agent.markdown import render_markdown
from oss_pr_agent.service import parse_repo_url


class ServiceTests(unittest.TestCase):
    def test_parse_repo_url_handles_standard_url(self) -> None:
        self.assertEqual(parse_repo_url("https://github.com/openai/openai-python"), "openai/openai-python")

    def test_parse_repo_url_strips_git_suffix(self) -> None:
        self.assertEqual(parse_repo_url("https://github.com/openai/openai-python.git"), "openai/openai-python")

    def test_render_markdown_supports_headers_lists_and_links(self) -> None:
        html = render_markdown("# Title\n\n- item\n\n[site](https://example.com)")
        self.assertIn("<h1>Title</h1>", html)
        self.assertIn("<li>item</li>", html)
        self.assertIn('href="https://example.com"', html)


if __name__ == "__main__":
    unittest.main()
