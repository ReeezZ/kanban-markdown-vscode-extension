#!/usr/bin/env python3
"""Checks the docs (default), or with --fix first rewrites their breadcrumbs.

Two checks, both offline, run by the pre-commit hook:

- Breadcrumbs: line 1 of each doc under docs/ and of each <folder>/README.md.
  The rule is in docs/CLAUDE.md ("Breadcrumb"); the part between README and the page
  title depends on where the doc lives:

      docs/areas/*             README › Architecture › <H1>
      docs/specs/*             README › Roadmap › <H1>
      other docs/*.md, <folder>/README.md   README › <H1>

  A path matching none of these fails instead of getting a guessed parent. The
  root README.md and the CLAUDE.md files have no breadcrumb. A doc is a breadcrumb line,
  a blank line, then the "# " title:

      [README](../README.md) › Roadmap › Some title

      # Some title

- Links: in those docs plus the root README.md, every CLAUDE.md, the backlog/*.md
  cards and the .claude/skills/*/SKILL.md skills (no breadcrumb there), every relative
  link must point at a file or folder git knows about (so a link to an ignored
  file fails, as it would on GitHub), and its #anchor must be a heading of the
  target doc under GitHub's slug rules, or for other files a line range within
  the file (#L42, #L42-L51). Links inside code blocks and code spans are
  examples and are skipped, and so are http(s) and mailto links: a hook doesn't
  go to the network. Reference-style links are checked too. A link to a single
  backlog card fails even if the file exists, except from another card: cards
  move when they're finished.

- Cards: the frontmatter of every card in backlog/ and backlog/done/ (id is the file
  name, status is a board column and matches the done/ folder, one kind and one area
  label, epic is null, "XX <name>" or a roadmap phase, order unique per epic), and that
  a `**Needs:**` id is a card. A mention of another card in a card's body is a link to
  its file, `[`id`](id.md)`, which lets the board's preview jump to it.

--fix rewrites breadcrumbs and those card links (also when a card has moved between
backlog/ and backlog/done/); other broken links are reported for a human.
The links check is plain regexes over the text instead of a Markdown parser or
a tool like lychee: the docs use a small subset of Markdown, and the hook stays
stdlib-only. Tests: scripts/test_docs_check.py.
"""

import argparse
import functools
import os
import posixpath
import re
import subprocess
import sys
from fnmatch import fnmatchcase
from pathlib import Path
from typing import NamedTuple
from urllib.parse import unquote

# First match wins. A None parent means the folder has no rule yet, which is
# reported instead of guessed. fnmatch's "*" also matches "/", like the shell
# `case` patterns this was written with.
PARENT_RULES: list[tuple[str, str | None]] = [
    ("docs/areas/*.md", " › [Architecture](../architecture.md#building-blocks)"),
    ("docs/specs/*.md", " › [Roadmap](../roadmap.md)"),
    ("docs/*/*", None),
    ("docs/*.md", ""),
    ("*/README.md", ""),
]

DOC_PATH = re.compile(r"^docs/(?!CLAUDE\.md$).*\.md$|^[^/]+/README\.md$")
# backlog/ holds the kanban cards and .claude/skills/ the skills; their links are checked,
# but they have no breadcrumb.
# backlog/done/ is left out: the extension moves finished cards there without
# rewriting their links, and they're deleted when their phase closes.
LINK_PATH = re.compile(
    DOC_PATH.pattern + r"|^README\.md$|^(.+/)?CLAUDE\.md$|^backlog/[^/]+\.md$|^\.claude/skills/[^/]+/SKILL\.md$"
)
# A card moves into backlog/done/ when it's finished, so a link to one would break.
# Matched on the path alone, so a link to a card that has already moved gets this
# message instead of "no such file".
CARD_PATH = re.compile(r"^backlog/(done/)?[^/]+\.md$")
CARD_LINK_MESSAGE = "link the backlog/ folder; name a card by its id in backticks"
# Only another card may link a card file, and --fix keeps those links pointing at the right
# place when a card moves. The id is the file name.
CARD_FILE = re.compile(r"backlog/(?:done/)?([^/]+)\.md")
CARD_REFERENCE = re.compile(
    r"\[(?P<text>[^\]]*)\]\((?P<target>[^)\s#]*\.md)(?P<fragment>#[^)\s]*)?\)"
    r"|`(?P<id>[a-z0-9]+(?:-[a-z0-9]+)*)`"
)
NEEDS_LINE = re.compile(r"^\*\*Needs:\*\*(.*)$")
PHASE_HEADING = re.compile(r"^### Phase (\d+): (.+?)\s*$", re.MULTILINE)
REQUIRED_KEYS = [
    "id", "status", "priority", "assignee", "epic", "dueDate",
    "created", "modified", "completedAt", "labels", "order",
]  # fmt: skip
PRIORITIES = {"critical", "high", "medium", "low"}
BUILDING_BLOCKS = "## Building blocks"
SCRIPT = "./scripts/docs_check.py"

FENCE = re.compile(r"^\s*(`{3,}|~{3,})")
CODE_SPAN = re.compile(r"(`+)(?!`).*?(?<!`)\1(?!`)")
INLINE_LINK = re.compile(r"!?\[[^\]]*\]\((<[^>]*>|[^)\s]*)(?:\s+\"[^\"]*\")?\)")
REFERENCE_DEF = re.compile(r"^ {0,3}\[[^\]]+\]:[ \t]*(<[^>]*>|\S+)", re.MULTILINE)
HEADING = re.compile(r"^ {0,3}#{1,6}[ \t]+(.+?)\s*$", re.MULTILINE)
SCHEME = re.compile(r"^[a-z][a-z0-9+.-]*:", re.IGNORECASE)
LINE_RANGE = re.compile(r"^L(\d+)(?:C\d+)?(?:-L(\d+)(?:C\d+)?)?$")


def repo_root() -> Path:
    out = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        check=True,
        capture_output=True,
        text=True,
    )
    return Path(out.stdout.strip())


def tracked_files() -> list[str]:
    """Tracked and untracked (not ignored) files, so a new doc is checked before it's staged."""
    out = subprocess.run(
        ["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
        check=True,
        capture_output=True,
        text=True,
    )
    paths = {p for p in out.stdout.split("\0") if p}
    # A file deleted in the working tree is still listed as cached.
    return sorted(p for p in paths if Path(p).is_file())


def parent_crumb(path: str) -> str | None:
    """The part between "README" and the title, or None if no rule covers `path`."""
    for pattern, parent in PARENT_RULES:
        if fnmatchcase(path, pattern):
            return parent
    return None


def expected_crumb(path: str, parent: str, title: str) -> str:
    up = "../" * path.count("/")
    return f"[README]({up}README.md){parent} › {title}"


def first_lines(path: str, count: int = 3) -> list[str]:
    with open(path, encoding="utf-8") as f:
        lines: list[str] = []
        for _ in range(count):
            line = f.readline()
            if not line:
                break
            lines.append(line.rstrip("\n"))
        return lines


def check_crumb(path: str, fix: bool) -> list[str]:
    """Returns the problems found in `path`; with `fix`, rewrites the crumb first."""
    parent = parent_crumb(path)
    if parent is None:
        folder = "folder" if path.startswith("docs/") else "path"
        return [f"{path}: no breadcrumb rule for this {folder}; add one in {SCRIPT}"]

    lines = first_lines(path)
    has_crumb = bool(lines) and lines[0].startswith("[README](")
    title_index = 2 if has_crumb else 0
    title_line = lines[title_index] if len(lines) > title_index else ""
    if not title_line.startswith("# "):
        return [f"{path}: no '# ' title on line 1 (or line 3 after a breadcrumb)"]

    crumb = expected_crumb(path, parent, title_line.removeprefix("# "))
    is_correct = has_crumb and lines[0] == crumb and len(lines) > 1 and lines[1] == ""
    if not is_correct:
        if not fix:
            return [f"{path}: breadcrumb missing or wrong, expected: {crumb}"]
        write_crumb(path, crumb, replace_existing=has_crumb)
        print(f"fixed {path}", file=sys.stderr)
    return []


def write_crumb(path: str, crumb: str, replace_existing: bool) -> None:
    """Puts `crumb` and a blank line above the title, replacing an old crumb and its blank line."""
    with open(path, encoding="utf-8") as f:
        rest = f.readlines()
    if replace_existing:
        rest = rest[2:]
    with open(path, "w", encoding="utf-8") as f:
        f.write(f"{crumb}\n\n{''.join(rest)}")


def strip_fences(text: str) -> str:
    """Empties the lines of fenced code blocks (``` or ~~~, indented or not).

    Lines stay in place, so line numbers computed afterwards still match.
    """
    out: list[str] = []
    fence = ""
    for line in text.split("\n"):
        match = FENCE.match(line)
        if fence:
            closes = match and match.group(1)[0] == fence[0] and len(match.group(1)) >= len(fence)
            if closes:
                fence = ""
            out.append("")
        elif match:
            fence = match.group(1)
            out.append("")
        else:
            out.append(line)
    return "\n".join(out)


def strip_spans(text: str) -> str:
    """Removes inline code spans (one line each, any number of backticks)."""
    return CODE_SPAN.sub("", text)


def find_links(text: str) -> list[tuple[int, str]]:
    """The (line, target) of every link and image outside code, in line order."""
    body = strip_spans(strip_fences(text))
    found: list[tuple[int, str]] = []
    for pattern in (INLINE_LINK, REFERENCE_DEF):
        for match in pattern.finditer(body):
            line = body.count("\n", 0, match.start()) + 1
            found.append((line, match.group(1)))
    return sorted(found)


def slug(heading: str) -> str:
    """GitHub's anchor for a heading, before duplicate numbering.

    Lowercase, punctuation dropped, each space a hyphen (never collapsed).
    """
    text = re.sub(r"!?\[([^\]]*)\]\([^)]*\)", r"\1", heading).replace("`", "")
    return re.sub(r"[^\w\- ]", "", text.lower()).replace(" ", "-")


def heading_anchors(text: str) -> set[str]:
    """The anchors of a doc's headings; a repeated heading gets -1, -2, ..."""
    seen: dict[str, int] = {}
    anchors: set[str] = set()
    for match in HEADING.finditer(strip_fences(text)):
        base = slug(match.group(1))
        count = seen.get(base, 0)
        seen[base] = count + 1
        anchors.add(base if count == 0 else f"{base}-{count}")
    return anchors


@functools.cache
def read_text(path: str) -> str:
    return Path(path).read_text(encoding="utf-8", errors="replace")


def link_problem(path: str, target: str, files: set[str], dirs: set[str]) -> str | None:
    """Why the link `target`, written in doc `path`, is broken, or None if it's fine."""
    target = target.removeprefix("<").removesuffix(">")
    if not target or SCHEME.match(target):
        return None
    if target.startswith("/"):
        return "absolute links resolve differently on GitHub; use a relative path"

    file_part, _, fragment = target.partition("#")
    resolved = path
    if file_part:
        resolved = posixpath.normpath(posixpath.join(posixpath.dirname(path), unquote(file_part)))
        if resolved == ".." or resolved.startswith("../"):
            return "leaves the repo"
        if CARD_PATH.match(resolved):
            return CARD_LINK_MESSAGE
        if resolved != "." and resolved not in files and resolved not in dirs:
            return "no such file or folder"
        if resolved == "." or resolved in dirs:
            return "a folder can't take a #fragment" if fragment else None
    if not fragment:
        return None

    if resolved.endswith(".md"):
        if fragment not in heading_anchors(read_text(resolved)):
            return f"no heading with the anchor #{fragment} in {resolved}"
        return None
    lines = LINE_RANGE.match(fragment)
    if not lines:
        return f"#{fragment} is not a line range (#L42 or #L42-L51)"
    last = int(lines.group(2) or lines.group(1))
    total = len(read_text(resolved).splitlines())
    if last > total:
        return f"line {last} is past the end of {resolved} ({total} lines)"
    return None


def check_links(files: list[str]) -> list[str]:
    known = set(files)
    dirs = {parent for f in files for parent in parents(f)}
    problems: list[str] = []
    for path in files:
        if not LINK_PATH.match(path):
            continue
        for line, target in find_links(read_text(path)):
            if card_link_target(path, target):  # check_cards looks at these
                continue
            problem = link_problem(path, target, known, dirs)
            if problem:
                problems.append(f"{path}:{line}: link {target} — {problem}")
    return problems


def parents(path: str) -> list[str]:
    """Every folder above `path`, as repo-relative paths without a trailing slash."""
    folders: list[str] = []
    folder = posixpath.dirname(path)
    while folder:
        folders.append(folder)
        folder = posixpath.dirname(folder)
    return folders


class Vocabulary(NamedTuple):
    """What a card's frontmatter may say, read from the docs and settings that define it."""

    columns: set[str]
    kinds: set[str]
    areas: set[str]
    phases: set[str]


def load_vocabulary() -> tuple[Vocabulary, list[str]]:
    """Reads the board columns, label vocabulary and roadmap phases; the problems say what's missing.

    The sources are `.vscode/settings.json` (columns), `docs/CLAUDE.md` (the `labels` bullet)
    and `docs/roadmap.md` (`### Phase N: Name` headings, as the epics `NN Name`), so each
    fact stays written in one place.
    """
    problems: list[str] = []
    settings = Path(".vscode/settings.json").read_text(encoding="utf-8")
    columns = set(re.findall(r'"id":\s*"([\w-]+)",\s*"name"', settings))
    if not columns:
        problems.append(".vscode/settings.json: no kanban-markdown.columns found")

    labels = re.search(r"^\s*- `labels`:(.*)$", Path("docs/CLAUDE.md").read_text(encoding="utf-8"), re.MULTILINE)
    head, _, tail = (labels.group(1) if labels else "").partition("one area")
    kinds, areas = set(re.findall(r"`([\w-]+)`", head)), set(re.findall(r"`([\w-]+)`", tail))
    if not kinds or not areas:
        problems.append("docs/CLAUDE.md: no `labels` bullet with 'one kind (...)' and 'one area (...)'")

    roadmap = Path("docs/roadmap.md").read_text(encoding="utf-8")
    phases = {f"{int(n):02d} {name}" for n, name in PHASE_HEADING.findall(roadmap)}
    return Vocabulary(columns, kinds, areas, phases), problems


def parse_frontmatter(text: str) -> dict[str, object] | None:
    """The `key: value` lines between the opening and closing `---` of a card, or None if there are none.

    Values are null, a quoted string, a `["a", "b"]` list of strings or a bare word, the
    shapes the Kanban Markdown extension writes. Not a YAML parser, so the hook stays stdlib-only.
    """
    lines = text.split("\n")
    if lines[0] != "---":
        return None
    data: dict[str, object] = {}
    for line in lines[1:]:
        if line == "---":
            return data
        match = re.match(r"^([A-Za-z]+):\s*(.*?)\s*$", line)
        if not match:
            continue
        key, value = match.groups()
        if value == "null":
            data[key] = None
        elif value.startswith("["):
            data[key] = re.findall(r'"([^"]*)"', value)
        else:
            data[key] = value.strip('"')
    return None


def lint_card(path: str, text: str, vocab: Vocabulary, cards: dict[str, str]) -> list[str]:
    """Problems in one card's frontmatter and `**Needs:**` line. `cards` maps each card id to its path."""
    front = parse_frontmatter(text)
    if front is None:
        return [f"{path}: no frontmatter between --- lines"]
    problems: list[str] = []

    def bad(message: str) -> None:
        problems.append(f"{path}: {message}")

    for key in REQUIRED_KEYS:
        if key not in front:
            bad(f"frontmatter has no {key}")
    stem = CARD_FILE.fullmatch(path)
    if stem and front.get("id") != stem.group(1):
        bad(f"id {front.get('id')!r} must be the file name {stem.group(1)!r}")

    in_done_folder = path.startswith("backlog/done/")
    status = front.get("status")
    if status not in vocab.columns:
        bad(f"status {status!r} is not a board column ({', '.join(sorted(vocab.columns))})")
    elif status == "done" and not in_done_folder:
        bad("status is done, so git mv the card into backlog/done/")
    elif status != "done" and in_done_folder:
        bad(f"in backlog/done/ but status is {status!r}")
    if (front.get("completedAt") is not None) != (status == "done"):
        bad("completedAt is set exactly when status is done")

    if front.get("priority") not in PRIORITIES:
        bad(f"priority {front.get('priority')!r} is not one of {', '.join(sorted(PRIORITIES))}")

    labels = front.get("labels")
    labels = labels if isinstance(labels, list) else []
    unknown = [label for label in labels if label not in vocab.kinds | vocab.areas]
    if unknown:
        bad(f"unknown labels: {', '.join(unknown)}")
    if sum(label in vocab.kinds for label in labels) != 1:
        bad(f"labels need exactly one kind ({', '.join(sorted(vocab.kinds))})")
    if sum(label in vocab.areas for label in labels) != 1:
        bad(f"labels need exactly one area ({', '.join(sorted(vocab.areas))})")

    epic = front.get("epic")
    if epic is not None and not (isinstance(epic, str) and epic.startswith("XX ")) and epic not in vocab.phases:
        bad(f"epic {epic!r} must be null, 'XX <name>' or a roadmap phase as 'NN <name>'")

    for line in text.split("\n"):
        needs = NEEDS_LINE.match(line)
        for card in re.findall(r"`([^`]+)`", needs.group(1)) if needs else []:
            if card not in cards:
                bad(f"Needs names `{card}`, which is no card")
    return problems


def lint_orders(fronts: dict[str, dict[str, object]]) -> list[str]:
    """Two open cards of one epic sharing an `order` leave their sequence undefined."""
    seen: dict[tuple[object, object], str] = {}
    problems: list[str] = []
    for path, front in sorted(fronts.items()):
        if path.startswith("backlog/done/") or front.get("order") is None:
            continue
        key = (front.get("epic"), front["order"])
        if key in seen:
            problems.append(f"{path}: order {front['order']!r} in epic {front.get('epic')!r} is also {seen[key]}'s")
        seen.setdefault(key, path)
    return problems


def card_locations(files: list[str]) -> dict[str, str]:
    """Each card id (its file name) and where its file is, in backlog/ or backlog/done/."""
    return {m.group(1): f for f in files if (m := CARD_FILE.fullmatch(f))}


def card_link_target(path: str, target: str) -> str | None:
    """The card file that a link written in card `path` points at, or None if it isn't a card link."""
    if not CARD_FILE.fullmatch(path) or SCHEME.match(target) or target.startswith("/"):
        return None
    resolved = posixpath.normpath(
        posixpath.join(posixpath.dirname(path), unquote(target.partition("#")[0]))
    )
    return resolved if CARD_PATH.match(resolved) else None


def relink_cards(path: str, text: str, cards: dict[str, str]) -> tuple[str, list[str]]:
    """The card's text with every mention of another card as a link to where that card is now.

    A card id in backticks becomes a link, and a link to a card that has moved (into or out of
    backlog/done/) is pointed at its file again. Returns the new text and one problem per
    change, plus one for a link to a card that doesn't exist. Frontmatter and code blocks are
    left alone; the card's own id stays plain.
    """
    own = CARD_FILE.fullmatch(path).group(1)  # type: ignore[union-attr]
    lines = text.split("\n")
    fenced = strip_fences(text).split("\n")
    problems: list[str] = []
    in_front = lines[0] == "---"

    def link_to(card: str) -> str:
        return posixpath.relpath(cards[card], posixpath.dirname(path))

    for number, line in enumerate(lines, start=1):
        if in_front:
            in_front = number == 1 or line != "---"
            continue
        if line and not fenced[number - 1]:
            continue

        def replace(match: re.Match[str]) -> str:
            if match.group("id"):
                card = match.group("id")
                if card == own or card not in cards:
                    return match.group(0)
                problems.append(f"{path}:{number}: card `{card}` is not a link; run {SCRIPT} --fix")
                return f"[`{card}`]({link_to(card)})"
            target = match.group("target")
            resolved = card_link_target(path, target)
            if resolved is None:
                return match.group(0)
            card = posixpath.basename(resolved).removesuffix(".md")
            if card not in cards:
                problems.append(f"{path}:{number}: link {target} — no such card")
                return match.group(0)
            if target == link_to(card):
                return match.group(0)
            problems.append(f"{path}:{number}: link {target} — {card} is at {link_to(card)}; run {SCRIPT} --fix")
            return f"[{match.group('text')}]({link_to(card)}{match.group('fragment') or ''})"

        lines[number - 1] = CARD_REFERENCE.sub(replace, line)
    return "\n".join(lines), problems


def check_cards(files: list[str], fix: bool) -> list[str]:
    """Lints every card and checks its mentions of other cards; with `fix`, rewrites those mentions first."""
    vocab, problems = load_vocabulary()
    cards = card_locations(files)
    fronts: dict[str, dict[str, object]] = {}
    for path in cards.values():
        text = read_text(path)
        new_text, reference_problems = relink_cards(path, text, cards)
        if fix and new_text != text:
            Path(path).write_text(new_text, encoding="utf-8")
            read_text.cache_clear()
            print(f"fixed {path}", file=sys.stderr)
            text = new_text
        else:
            problems += reference_problems
        problems += lint_card(path, text, vocab, cards)
        fronts[path] = parse_frontmatter(text) or {}
    return problems + lint_orders(fronts)


def main() -> int:
    parser = argparse.ArgumentParser(description=(__doc__ or "").split("\n\n")[0])
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true", help="report problems (default)")
    mode.add_argument(
        "--fix", action="store_true", help="write the breadcrumbs and card links, then check"
    )
    fix = parser.parse_args().fix

    os.chdir(repo_root())
    files = tracked_files()

    crumb_problems: list[str] = []
    architecture = Path("docs/architecture.md").read_text(encoding="utf-8")
    if architecture.split("\n").count(BUILDING_BLOCKS) != 1:
        crumb_problems.append(
            f'docs/architecture.md: needs exactly one "{BUILDING_BLOCKS}" heading '
            "(area breadcrumbs link to it)"
        )
    for path in files:
        if DOC_PATH.match(path):
            crumb_problems += check_crumb(path, fix)

    # After the crumbs, so --fix's rewrites are what gets checked.
    link_problems = check_cards(files, fix) + check_links(files)

    for problem in crumb_problems + link_problems:
        print(problem, file=sys.stderr)
    if crumb_problems and not fix:
        print(f"Run {SCRIPT} --fix to write the breadcrumbs.", file=sys.stderr)
    return 1 if crumb_problems or link_problems else 0


if __name__ == "__main__":
    sys.exit(main())
