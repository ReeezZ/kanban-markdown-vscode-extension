"""Tests for docs_check.py. Run: python3 -m unittest discover -s scripts -t ."""

import os
import tempfile
import unittest
from pathlib import Path

from scripts import docs_check as d


class SlugTest(unittest.TestCase):
    def test_github_rules(self):
        # Headings that exercise each rule.
        cases = {
            "Clarification & Context-Gathering": "clarification--context-gathering",
            "TypeScript / React": "typescript--react",
            "Phase 0.5: Board Foundation": "phase-05-board-foundation",
            "Kanban Board - Vision & Roadmap": "kanban-board---vision--roadmap",
            "Why it's set up this way": "why-its-set-up-this-way",
            "Inside `src/`": "inside-src",
            "Server data through [TanStack Query](x.md) (planned)": "server-data-through-tanstack-query-planned",
        }
        for heading, expected in cases.items():
            with self.subTest(heading=heading):
                self.assertEqual(d.slug(heading), expected)


class DocPathsTest(unittest.TestCase):
    def test_claude_files_get_links_checked_but_no_breadcrumb(self):
        for path in ["CLAUDE.md", "docs/CLAUDE.md", "web/CLAUDE.md"]:
            with self.subTest(path=path):
                self.assertIsNone(d.DOC_PATH.match(path))
                self.assertIsNotNone(d.LINK_PATH.match(path))

    def test_backlog_cards_get_links_checked_but_no_breadcrumb(self):
        self.assertIsNone(d.DOC_PATH.match("backlog/card-filter.md"))
        self.assertIsNotNone(d.LINK_PATH.match("backlog/card-filter.md"))
        for path in ["backlog/done/card-filter.md", "backlog/sub/x.md", "backlog/x.txt"]:
            with self.subTest(path=path):
                self.assertIsNone(d.LINK_PATH.match(path))

    def test_skills_get_links_checked_but_no_breadcrumb(self):
        self.assertIsNone(d.DOC_PATH.match(".claude/skills/merge/SKILL.md"))
        self.assertIsNotNone(d.LINK_PATH.match(".claude/skills/merge/SKILL.md"))
        for path in [".claude/skills/SKILL.md", ".claude/skills/merge/notes.md", ".claude/skills/a/b/SKILL.md"]:
            with self.subTest(path=path):
                self.assertIsNone(d.LINK_PATH.match(path))

    def test_other_docs_still_get_a_breadcrumb(self):
        for path in ["docs/roadmap.md", "docs/areas/ui.md", "web/README.md"]:
            with self.subTest(path=path):
                self.assertIsNotNone(d.DOC_PATH.match(path))


class HeadingAnchorsTest(unittest.TestCase):
    def test_repeated_headings_are_numbered(self):
        self.assertEqual(d.heading_anchors("# A\n## A\n## A"), {"a", "a-1", "a-2"})

    def test_headings_in_fences_are_ignored(self):
        text = "# Real\n```sh\n# when done:\n```\n"
        self.assertEqual(d.heading_anchors(text), {"real"})


class StripTest(unittest.TestCase):
    def test_fences_are_emptied_line_for_line(self):
        self.assertEqual(d.strip_fences("a\n```\n# x\n```\nb"), "a\n\n\n\nb")

    def test_indented_tilde_fence_in_a_list(self):
        text = "- item\n  ~~~sh\n  [x](y)\n  ~~~\n- next"
        self.assertEqual(d.strip_fences(text), "- item\n\n\n\n- next")

    def test_a_shorter_fence_does_not_close_a_longer_one(self):
        self.assertEqual(d.strip_fences("````\n```\nx\n````\nb"), "\n\n\n\nb")

    def test_code_spans_with_one_or_two_backticks(self):
        self.assertEqual(d.strip_spans("see `[a](b.md)` and ``x ` [c](d)`` here"), "see  and  here")

    def test_link_text_in_code_keeps_the_link(self):
        self.assertEqual(d.strip_spans("[`code`](file.md)"), "[](file.md)")


class FindLinksTest(unittest.TestCase):
    def test_links_images_and_reference_definitions(self):
        text = 'a [x](b.md#c) b\n`[y](z)`\n![i](<d e.png> "t") [r]: no\n[r]: f.md'
        self.assertEqual(
            d.find_links(text),
            [(1, "b.md#c"), (3, "<d e.png>"), (4, "f.md")],
        )

    def test_link_text_can_wrap_lines(self):
        self.assertEqual(d.find_links("[wrapped\ntext](a.md)"), [(1, "a.md")])

    def test_links_in_fences_are_ignored(self):
        self.assertEqual(d.find_links("```\n[x](y.md)\n```"), [])

    def test_line_numbers_count_past_fences(self):
        self.assertEqual(d.find_links("```\nx\n```\n[a](b.md)"), [(4, "b.md")])


class LinkProblemTest(unittest.TestCase):
    """Runs in a temp repo, since anchors and line counts are read from disk."""

    FILES = {
        "README.md": "# Top\n",
        "docs/architecture.md": "# Arch\n\n## Building blocks\n\n## Risks\n",
        "docs/areas/items.md": "# Items\n",
        "src/core/item.ts": "a\nb\nc\n",
        "src/webview/history/page.tsx": "x\n",
        "notes.txt": "",
    }

    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        for name, content in self.FILES.items():
            path = Path(tmp.name, name)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content)
        previous = os.getcwd()
        os.chdir(tmp.name)
        self.addCleanup(os.chdir, previous)
        d.read_text.cache_clear()
        self.files = set(self.FILES)
        self.dirs = {p for f in self.files for p in d.parents(f)}

    def problem(self, target: str, path: str = "docs/areas/items.md") -> str | None:
        return d.link_problem(path, target, self.files, self.dirs)

    def test_valid_links(self):
        for target in [
            "../architecture.md",
            "../architecture.md#building-blocks",
            "../../src/core/item.ts",
            "../../src/core/item.ts#L3",
            "../../src/core/item.ts#L1-L3",
            "../../src/webview/history/",
            "../../src/webview/history",
            "../../",
            "#items",
            "<../architecture.md>",
            "https://example.com/x",
            "mailto:a@b.c",
        ]:
            with self.subTest(target=target):
                self.assertIsNone(self.problem(target))

    def test_moved_file(self):
        self.assertEqual(self.problem("../../src/core/db/item.ts"), "no such file or folder")

    def test_anchor_must_match_exactly(self):
        self.assertIn("no heading", self.problem("../architecture.md#Building-Blocks") or "")
        self.assertIn("no heading", self.problem("../architecture.md#nope") or "")
        self.assertIn("no heading", self.problem("#missing") or "")

    def test_line_range_past_the_end(self):
        self.assertIn("past the end", self.problem("../../src/core/item.ts#L4") or "")
        self.assertIn("past the end", self.problem("../../src/core/item.ts#L1-L9") or "")

    def test_other_fragment_on_a_non_markdown_file(self):
        self.assertIn("not a line range", self.problem("../../src/core/item.ts#top") or "")

    def test_fragment_on_a_folder(self):
        self.assertIn("folder", self.problem("../../src/#x") or "")

    def test_absolute_link(self):
        self.assertIn("absolute", self.problem("/README.md") or "")

    def test_leaving_the_repo(self):
        self.assertEqual(self.problem("../../../x.md"), "leaves the repo")

    def test_link_to_a_card_file_is_refused(self):
        self.files.add("backlog/card-filter.md")
        self.dirs.add("backlog")
        for target in ["../../backlog/card-filter.md", "../../backlog/done/gone.md"]:
            with self.subTest(target=target):
                self.assertEqual(self.problem(target), d.CARD_LINK_MESSAGE)

    def test_link_to_the_backlog_folder_is_fine(self):
        self.files.add("backlog/card-filter.md")
        self.dirs.add("backlog")
        self.assertIsNone(self.problem("../../backlog/"))

    def test_link_problem_alone_refuses_card_to_card(self):
        # link_problem refuses any card file; check_links is where a card may link a card
        # (see CardLinksInCheckLinksTest).
        self.assertEqual(self.problem("other-card.md", path="backlog/card-filter.md"), d.CARD_LINK_MESSAGE)

    def test_file_git_does_not_know_about(self):
        self.files.discard("notes.txt")
        self.assertEqual(self.problem("../../notes.txt"), "no such file or folder")


def card_text(body: str = "Body.\n", /, **overrides: str | None) -> str:
    """A valid card; `overrides` replace frontmatter lines by key (value written as-is)."""
    front: dict[str, str | None] = {
        "id": "alpha",
        "status": "todo",
        "priority": "high",
        "assignee": "null",
        "epic": "null",
        "dueDate": "null",
        "created": '"2026-01-01"',
        "modified": '"2026-01-01"',
        "completedAt": "null",
        "labels": '["feature", "ui"]',
        "order": "1",
    }
    front.update(overrides)
    lines = [f"{k}: {v}" for k, v in front.items() if v is not None]
    return "---\n" + "\n".join(lines) + "\n---\n" + body


VOCAB = d.Vocabulary(
    columns={"todo", "in-progress", "done"},
    kinds={"feature", "bug"},
    areas={"ui", "board"},
    phases={"03 Board & Filters"},
)


class ParseFrontmatterTest(unittest.TestCase):
    def test_value_shapes(self):
        text = '---\nid: x\nepic: null\nstatus: "todo"\nlabels: ["a", "b"]\norder: 3\n---\nbody'
        self.assertEqual(d.parse_frontmatter(text),{"id": "x", "epic": None, "status": "todo", "labels": ["a", "b"], "order": "3"})

    def test_no_opening_line(self):
        self.assertIsNone(d.parse_frontmatter("id: x\n---\n"))

    def test_no_closing_line(self):
        self.assertIsNone(d.parse_frontmatter("---\nid: x\nstatus: todo\n"))

    def test_empty_list(self):
        self.assertEqual(d.parse_frontmatter("---\nlabels: []\n---\n"), {"labels": []})


class LintCardTest(unittest.TestCase):
    PATH = "backlog/alpha.md"

    def lint(self, text: str, path: str = PATH, cards: dict[str, str] | None = None) -> list[str]:
        return d.lint_card(path, text, VOCAB, cards if cards is not None else {"alpha": path})

    def assertOneProblem(self, problems: list[str], fragment: str):
        self.assertEqual(len(problems), 1, problems)
        self.assertTrue(problems[0].startswith(self.PATH), problems)
        self.assertIn(fragment, problems[0])

    def test_valid_card(self):
        self.assertEqual(self.lint(card_text()), [])

    def test_valid_done_card(self):
        text = card_text(id="beta", status="done", completedAt='"2026-02-01"')
        self.assertEqual(self.lint(text, "backlog/done/beta.md", {"beta": "backlog/done/beta.md"}), [])

    def test_no_frontmatter(self):
        self.assertOneProblem(self.lint("just text\n"), "frontmatter")

    def test_missing_required_key(self):
        problems = self.lint(card_text(order=None))
        self.assertOneProblem(problems, "order")

    def test_every_required_key_is_required(self):
        for key in d.REQUIRED_KEYS:
            with self.subTest(key=key):
                problems = self.lint(card_text(**{key: None}))
                self.assertTrue(any(key in p for p in problems), problems)

    def test_id_must_be_file_name(self):
        self.assertOneProblem(self.lint(card_text(id="other")), "other")

    def test_status_must_be_a_column(self):
        self.assertOneProblem(self.lint(card_text(status="wip")), "wip")

    def test_done_status_outside_done_folder(self):
        self.assertOneProblem(self.lint(card_text(status="done", completedAt='"2026-02-01"')), "done")

    def test_open_status_inside_done_folder(self):
        problems = self.lint(card_text(), "backlog/done/alpha.md", {"alpha": "backlog/done/alpha.md"})
        self.assertEqual(len(problems), 1, problems)
        self.assertTrue(problems[0].startswith("backlog/done/alpha.md"))

    def test_completed_at_on_a_non_done_card(self):
        self.assertOneProblem(self.lint(card_text(completedAt='"2026-02-01"')), "completedAt")

    def test_completed_at_null_on_a_done_card(self):
        problems = self.lint(card_text(status="done"), "backlog/done/alpha.md", {"alpha": "backlog/done/alpha.md"})
        self.assertEqual(len(problems), 1, problems)
        self.assertIn("completedAt", problems[0])

    def test_priority(self):
        for ok in ["critical", "high", "medium", "low"]:
            with self.subTest(ok=ok):
                self.assertEqual(self.lint(card_text(priority=ok)), [])
        self.assertOneProblem(self.lint(card_text(priority="urgent")), "urgent")

    def test_unknown_label(self):
        problems = self.lint(card_text(labels='["feature", "ui", "bogus"]'))
        self.assertTrue(any("bogus" in p for p in problems), problems)

    def test_label_counts(self):
        cases = {
            "no kind": '["ui"]',
            "two kinds": '["feature", "bug", "ui"]',
            "no area": '["feature"]',
            "two areas": '["feature", "ui", "board"]',
        }
        for name, labels in cases.items():
            with self.subTest(name=name):
                problems = self.lint(card_text(labels=labels))
                self.assertEqual(len(problems), 1, problems)
                self.assertTrue(problems[0].startswith(self.PATH))

    def test_epic_values(self):
        for ok in ["null", '"XX Anything"', '"03 Board & Filters"']:
            with self.subTest(ok=ok):
                self.assertEqual(self.lint(card_text(epic=ok)), [])
        for bad in ['"3 Board & Filters"', '"09 Unknown"', '"Board"', '"XXAnything"']:
            with self.subTest(bad=bad):
                self.assertOneProblem(self.lint(card_text(epic=bad)), "epic")

    def test_needs_must_name_a_card(self):
        self.assertOneProblem(self.lint(card_text("**Needs:** `ghost`\n")), "ghost")

    def test_needs_with_known_cards_and_none(self):
        cards = {"alpha": self.PATH, "beta": "backlog/beta.md", "gamma": "backlog/done/gamma.md"}
        self.assertEqual(self.lint(card_text("**Needs:** `beta`, `gamma`\n"), cards=cards), [])
        self.assertEqual(self.lint(card_text("**Needs:** none\n")), [])

    def test_needs_reports_each_unknown_card(self):
        problems = self.lint(card_text("**Needs:** `ghost`, `phantom`\n"))
        self.assertEqual(len(problems), 2, problems)


class LintOrdersTest(unittest.TestCase):
    def front(self, epic, order) -> dict[str, object]:
        return {"epic": epic, "order": order}

    def test_same_epic_same_order(self):
        problems = d.lint_orders({
            "backlog/a.md": self.front("XX A", "1"),
            "backlog/b.md": self.front("XX A", "1"),
        })
        self.assertEqual(len(problems), 1, problems)
        self.assertTrue(problems[0].startswith("backlog/"))

    def test_different_epics_are_fine(self):
        self.assertEqual(d.lint_orders({
            "backlog/a.md": self.front("XX A", "1"),
            "backlog/b.md": self.front("XX B", "1"),
        }), [])

    def test_different_orders_are_fine(self):
        self.assertEqual(d.lint_orders({
            "backlog/a.md": self.front("XX A", "1"),
            "backlog/b.md": self.front("XX A", "2"),
        }), [])

    def test_done_cards_do_not_count(self):
        self.assertEqual(d.lint_orders({
            "backlog/a.md": self.front("XX A", "1"),
            "backlog/done/b.md": self.front("XX A", "1"),
        }), [])

    def test_null_epic_is_one_group(self):
        problems = d.lint_orders({
            "backlog/a.md": self.front(None, "1"),
            "backlog/b.md": self.front(None, "1"),
        })
        self.assertEqual(len(problems), 1, problems)


class CardPathsTest(unittest.TestCase):
    def test_card_locations(self):
        files = [
            "backlog/a.md", "backlog/done/b.md", "backlog/sub/c.md",
            "docs/d.md", "README.md", "backlog/e.txt", "docs/backlog/f.md", "x/backlog/done/g.md",
        ]
        self.assertEqual(d.card_locations(files), {"a": "backlog/a.md", "b": "backlog/done/b.md"})

    def test_card_link_target_resolves_from_a_card(self):
        cases = [
            ("backlog/a.md", "b.md", "backlog/b.md"),
            ("backlog/a.md", "done/b.md", "backlog/done/b.md"),
            ("backlog/done/a.md", "../b.md", "backlog/b.md"),
            ("backlog/done/a.md", "b.md", "backlog/done/b.md"),
            ("backlog/a.md", "b.md#section", "backlog/b.md"),
            ("backlog/a.md", "./b.md", "backlog/b.md"),
        ]
        for path, target, expected in cases:
            with self.subTest(path=path, target=target):
                self.assertEqual(d.card_link_target(path, target), expected)

    def test_card_link_target_none_cases(self):
        cases = [
            ("docs/roadmap.md", "../backlog/a.md"),
            ("README.md", "backlog/a.md"),
            ("backlog/a.md", "https://example.com/b.md"),
            ("backlog/a.md", "mailto:x@y.z"),
            ("backlog/a.md", "http:b.md"),
            ("backlog/a.md", "/backlog/b.md"),
            ("backlog/a.md", "../docs/roadmap.md"),
            ("backlog/a.md", "notes.txt"),
            ("backlog/a.md", "#top"),
        ]
        for path, target in cases:
            with self.subTest(path=path, target=target):
                self.assertIsNone(d.card_link_target(path, target))


class RelinkCardsTest(unittest.TestCase):
    CARDS = {
        "alpha": "backlog/alpha.md",
        "beta": "backlog/beta.md",
        "gone": "backlog/done/gone.md",
    }

    def relink(self, body: str, path: str = "backlog/alpha.md"):
        text = card_text(body)
        new, problems = d.relink_cards(path, text, self.CARDS)
        return text, new, problems

    def test_backticked_id_becomes_a_link(self):
        text, new, problems = self.relink("See `beta` now.\n")
        self.assertEqual(new, text.replace("`beta`", "[`beta`](beta.md)"))
        self.assertEqual(len(problems), 1, problems)

    def test_link_from_open_to_done_and_back(self):
        _, new, _ = self.relink("See `gone`.\n")
        self.assertIn("[`gone`](done/gone.md)", new)
        done_text = card_text("See `beta`.\n", id="gone")
        new, _ = d.relink_cards("backlog/done/gone.md", done_text, self.CARDS)
        self.assertIn("[`beta`](../beta.md)", new)

    def test_moved_card_is_repointed_keeping_text_and_fragment(self):
        text, new, problems = self.relink("See [the card](gone.md#part) here.\n")
        self.assertEqual(new, text.replace("[the card](gone.md#part)", "[the card](done/gone.md#part)"))
        self.assertEqual(len(problems), 1, problems)

    def test_link_pointing_the_wrong_way_from_done(self):
        text = card_text("See [x](beta.md).\n", id="gone")
        new, problems = d.relink_cards("backlog/done/gone.md", text, self.CARDS)
        self.assertIn("[x](../beta.md)", new)
        self.assertEqual(len(problems), 1, problems)

    def test_correct_link_is_untouched(self):
        text, new, problems = self.relink("See [`beta`](beta.md) and [g](done/gone.md#x).\n")
        self.assertEqual(new, text)
        self.assertEqual(problems, [])

    def test_link_to_a_missing_card(self):
        text, new, problems = self.relink("See [x](missing.md).\n")
        self.assertEqual(new, text)
        self.assertEqual(len(problems), 1, problems)
        self.assertIn("no such card", problems[0])

    def test_own_id_stays_plain(self):
        text, new, problems = self.relink("This is `alpha`.\n")
        self.assertEqual(new, text)
        self.assertEqual(problems, [])

    def test_frontmatter_is_untouched(self):
        text = card_text("Body.\n", id="alpha", epic='"XX beta"', labels='["feature", "ui"]')
        text = text.replace("order: 1", "order: 1\nnote: `beta`")
        new, problems = d.relink_cards("backlog/alpha.md", text, self.CARDS)
        self.assertEqual(new, text)
        self.assertEqual(problems, [])

    def test_fenced_code_is_untouched(self):
        text, new, problems = self.relink("```\n`beta` [x](gone.md)\n```\n")
        self.assertEqual(new, text)
        self.assertEqual(problems, [])

    def test_backticked_non_cards_are_untouched(self):
        text, new, problems = self.relink("Use `pnpm-test` and `foo` here.\n")
        self.assertEqual(new, text)
        self.assertEqual(problems, [])

    def test_id_inside_link_text_is_not_linked_twice(self):
        text, new, problems = self.relink("See [`beta`](beta.md).\n")
        self.assertEqual(new, text)
        self.assertEqual(problems, [])

    def test_id_inside_link_text_with_wrong_target_is_only_repointed(self):
        _, new, problems = self.relink("See [`gone`](gone.md).\n")
        self.assertIn("[`gone`](done/gone.md)", new)
        self.assertNotIn("[[", new)
        self.assertEqual(len(problems), 1, problems)

    def test_one_problem_per_change_with_line_number(self):
        body = "one\nSee `beta` and `gone`.\n[m](missing.md)\n[g](gone.md)\n"
        text = card_text(body)
        first_body_line = text.split("\n").index("one") + 1
        _, problems = d.relink_cards("backlog/alpha.md", text, self.CARDS)
        self.assertEqual(len(problems), 4, problems)
        self.assertIn(f":{first_body_line + 1}:", problems[0])
        self.assertIn(f":{first_body_line + 1}:", problems[1])
        self.assertIn(f":{first_body_line + 2}:", problems[2])
        self.assertIn(f":{first_body_line + 3}:", problems[3])


class CardRepoTest(unittest.TestCase):
    """Runs in a temp repo, since the vocabulary and the cards are read from disk."""

    SETTINGS = (
        '{"kanban-markdown.columns": [\n'
        '  {"id": "todo", "name": "To Do"},\n'
        '  {"id": "in-progress", "name": "In Progress"},\n'
        '  {"id": "done", "name": "Done"}\n]}\n'
    )
    CLAUDE = "# Docs\n\n- `labels`: one kind (`feature`, `bug`) and one area (`ui`, `board`).\n"
    ROADMAP = "# Roadmap\n\n### Phase 3: Board & Filters\n\n### Phase 12: Later On\n"

    def write(self, name: str, content: str):
        path = Path(name)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)

    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        previous = os.getcwd()
        os.chdir(tmp.name)
        self.addCleanup(os.chdir, previous)
        d.read_text.cache_clear()
        self.addCleanup(d.read_text.cache_clear)
        self.write(".vscode/settings.json", self.SETTINGS)
        self.write("docs/CLAUDE.md", self.CLAUDE)
        self.write("docs/roadmap.md", self.ROADMAP)


class LoadVocabularyTest(CardRepoTest):
    def test_reads_columns_labels_and_phases(self):
        vocab, problems = d.load_vocabulary()
        self.assertEqual(problems, [])
        self.assertEqual(vocab.columns, {"todo", "in-progress", "done"})
        self.assertEqual(vocab.kinds, {"feature", "bug"})
        self.assertEqual(vocab.areas, {"ui", "board"})
        self.assertEqual(vocab.phases, {"03 Board & Filters", "12 Later On"})

    def test_hyphenated_labels_are_read(self):
        self.write("docs/CLAUDE.md", "# Docs\n\n- `labels`: one kind (`new-feature`, `bug`) and one area (`web-ui`, `board`).\n")
        vocab, problems = d.load_vocabulary()
        self.assertEqual(problems, [])
        self.assertEqual(vocab.kinds, {"new-feature", "bug"})
        self.assertEqual(vocab.areas, {"web-ui", "board"})

    def test_missing_sources_are_reported(self):
        self.write(".vscode/settings.json", "{}")
        self.write("docs/CLAUDE.md", "# Docs\n")
        vocab, problems = d.load_vocabulary()
        self.assertEqual(len(problems), 2, problems)
        self.assertEqual(vocab.columns, set())
        self.assertEqual(vocab.kinds, set())


class CheckCardsTest(CardRepoTest):
    def setUp(self):
        super().setUp()
        self.write("backlog/alpha.md", card_text("See `beta` and `gone`.\n", order="1"))
        self.write("backlog/beta.md", card_text("Plain.\n", id="beta", order="2"))
        self.write(
            "backlog/done/gone.md",
            card_text("Done.\n", id="gone", status="done", completedAt='"2026-02-01"'),
        )
        self.files = ["backlog/alpha.md", "backlog/beta.md", "backlog/done/gone.md"]

    def test_check_reports_and_writes_nothing(self):
        before = Path("backlog/alpha.md").read_text()
        problems = d.check_cards(self.files, fix=False)
        self.assertEqual(len(problems), 2, problems)
        self.assertEqual(Path("backlog/alpha.md").read_text(), before)

    def test_fix_rewrites_and_then_is_clean(self):
        self.assertEqual(d.check_cards(self.files, fix=True), [])
        self.assertIn("[`beta`](beta.md) and [`gone`](done/gone.md)", Path("backlog/alpha.md").read_text())
        d.read_text.cache_clear()
        self.assertEqual(d.check_cards(self.files, fix=False), [])

    def test_lint_problems_come_back_either_way(self):
        self.write("backlog/beta.md", card_text("Plain.\n", id="beta", priority="urgent", order="2"))
        for fix in (False, True):
            with self.subTest(fix=fix):
                d.read_text.cache_clear()
                problems = d.check_cards(self.files, fix=fix)
                self.assertTrue(any("urgent" in p and p.startswith("backlog/beta.md") for p in problems), problems)

    def test_duplicate_order_is_reported(self):
        self.write("backlog/beta.md", card_text("Plain.\n", id="beta", order="1"))
        problems = d.check_cards(self.files, fix=True)
        self.assertEqual(len(problems), 1, problems)
        self.assertIn("order", problems[0])


class CardLinksInCheckLinksTest(CardRepoTest):
    def test_card_may_link_another_card(self):
        self.write("backlog/alpha.md", card_text("See [b](beta.md) and [g](done/gone.md).\n"))
        self.write("backlog/beta.md", card_text(id="beta"))
        self.write("backlog/done/gone.md", card_text(id="gone"))
        files = ["backlog/alpha.md", "backlog/beta.md", "backlog/done/gone.md"]
        self.assertEqual(d.check_links(files), [])

    def test_doc_linking_a_card_is_still_reported(self):
        self.write("docs/notes.md", "# Notes\n\nSee [b](../backlog/beta.md).\n")
        self.write("backlog/beta.md", card_text(id="beta"))
        problems = d.check_links(["docs/notes.md", "backlog/beta.md"])
        self.assertEqual(len(problems), 1, problems)
        self.assertIn(d.CARD_LINK_MESSAGE, problems[0])


if __name__ == "__main__":
    unittest.main()
