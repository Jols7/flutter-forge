"""Structure tests for the hu-v1 story template and the story fixtures.

hu-to-brief.md is an instruction for the model, not a script. `read_story` below is a small
reference reader of its "Reading a story" rules. It proves the template and the fixtures can be
read by section number, with §5/§6 limited to `### mobile`. Run with:
python3 -m unittest discover -s plugins/flutter-forge/tests -v
"""
from __future__ import annotations

import os
import re
import unittest
from typing import Dict, List, Optional

HERE = os.path.dirname(os.path.abspath(__file__))
PLUGIN = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(PLUGIN))
TEMPLATE = os.path.join(PLUGIN, "skills", "forge-requirements", "references", "hu-template.md")
FIXTURES = os.path.join(HERE, "fixtures", "hu")
EXAMPLE_STORY = os.path.join(REPO, "example", "forge_demo", "docs", "stories", "HU-01-transfer.md")

HU_V1_TITLES = [
    "Story and purpose",
    "Use cases",
    "Business rules and validations",
    "Acceptance criteria",
    "Interface, flows and states",
    "Design references",
    "Data and integration (contract-first, to be confirmed by backend)",
    "Security and privacy",
    "Out of scope",
    "Open questions",
]
SURFACE_SECTIONS = (5, 6)


def read(path: str) -> str:
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def template_body(text: str) -> str:
    """The story skeleton inside the template's ```markdown fence."""
    m = re.search(r"```markdown\n(.*)\n```", text, re.S)
    if not m:
        raise AssertionError("template has no ```markdown block")
    return m.group(1)


def sections(text: str) -> Dict[int, Dict[str, str]]:
    """{number: {"title": …, "body": …}} for every `## N. Title` heading."""
    out: Dict[int, Dict[str, str]] = {}
    matches = list(re.finditer(r"^## (\d+)\. (.+)$", text, re.M))
    for i, m in enumerate(matches):
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        out[int(m.group(1))] = {"title": m.group(2).strip(), "body": text[m.end():end]}
    return out


def header(text: str) -> Dict[str, str]:
    fields = {}
    for m in re.finditer(r"^\| ([^|]+?) \| ([^|]*?) \|$", text.split("## 1.")[0], re.M):
        fields[m.group(1).strip()] = m.group(2).strip()
    return fields


def surfaces_of(head: Dict[str, str]) -> List[str]:
    """`Surfaces` (hu-v1) or `Platform` (earlier stories), normalized to surface names."""
    raw = head.get("Surfaces") or head.get("Platform") or ""
    found = set(re.findall(r"\b(api|web|mobile)\b", raw.lower()))
    if "Surfaces" not in head and re.search(r"\bapp\b", raw.lower()):
        found.add("mobile")
    return sorted(found)


def surface_block(body: str, surface: str) -> Optional[str]:
    """Content of `### <surface>` inside a section; the whole body when there are no subsections."""
    blocks = list(re.finditer(r"^### (\w+)\s*$", body, re.M))
    if not blocks:
        return body
    for i, m in enumerate(blocks):
        if m.group(1) == surface:
            end = blocks[i + 1].start() if i + 1 < len(blocks) else len(body)
            return body[m.end():end]
    return None


def read_story(text: str, surface: str = "mobile") -> Dict[str, object]:
    head = header(text)
    secs = sections(text)
    applies = surface in surfaces_of(head)
    content = {}
    gaps = []
    for n, sec in secs.items():
        if n in SURFACE_SECTIONS:
            block = surface_block(sec["body"], surface)
            if block is None:
                gaps.append("§%d has no ### %s block" % (n, surface))
                block = ""
            content[n] = block
        else:
            content[n] = sec["body"]
    return {"template": head.get("Template", "pre-hu-v1"), "applies": applies, "sections": content, "gaps": gaps}


class HuTemplateTest(unittest.TestCase):
    def setUp(self):
        self.text = read(TEMPLATE)
        self.body = template_body(self.text)

    def test_sections_1_to_10_in_order_with_titles(self):
        secs = sections(self.body)
        self.assertEqual(list(secs), list(range(1, 11)))
        self.assertEqual([secs[n]["title"] for n in range(1, 11)], HU_V1_TITLES)

    def test_header_declares_contract_and_surfaces(self):
        head = header(self.body)
        self.assertEqual(head.get("Template"), "hu-v1")
        for field in ("Epic", "Surfaces", "Priority", "Points", "Depends on", "Status", "Design"):
            self.assertIn(field, head)
        self.assertNotIn("Platform", head)

    def test_surface_sections_have_web_and_mobile_blocks(self):
        secs = sections(self.body)
        for n in SURFACE_SECTIONS:
            self.assertIsNotNone(surface_block(secs[n]["body"], "web"), "§%d ### web" % n)
            self.assertIsNotNone(surface_block(secs[n]["body"], "mobile"), "§%d ### mobile" % n)

    def test_rules_keep_numbering_and_surface_convention(self):
        self.assertIn("`### <surface>` convention", self.text)
        self.assertIn("map sections by number", self.text)
        self.assertIn("`N/A — <reason>`", self.text)


class StoryReadingTest(unittest.TestCase):
    def test_legacy_flat_story_still_reads(self):
        story = read_story(read(os.path.join(FIXTURES, "legacy-flat.md")))
        self.assertEqual(story["template"], "pre-hu-v1")
        self.assertTrue(story["applies"], "Platform: App (mobile) must apply")
        self.assertEqual(sorted(story["sections"]), list(range(1, 11)))
        self.assertIn("Nueva transferencia", story["sections"][5])     # flat §5 read whole
        self.assertEqual(story["gaps"], [])

    def test_multisurface_story_reads_only_mobile(self):
        story = read_story(read(os.path.join(FIXTURES, "hu-v1-multisurface.md")))
        self.assertEqual(story["template"], "hu-v1")
        self.assertTrue(story["applies"])
        for n in SURFACE_SECTIONS:
            self.assertNotIn("WEB-ONLY", story["sections"][n], "§%d leaked web content" % n)
        self.assertIn("Pagos", story["sections"][5])
        self.assertIn("20:5", story["sections"][6])
        self.assertEqual(story["gaps"], [])

    def test_story_without_mobile_does_not_apply(self):
        text = read(os.path.join(FIXTURES, "hu-v1-multisurface.md")).replace(
            "| Surfaces | api · web · mobile |", "| Surfaces | api · web |")
        self.assertFalse(read_story(text)["applies"])

    def test_missing_mobile_block_is_a_gap(self):
        text = read(os.path.join(FIXTURES, "hu-v1-multisurface.md"))
        text = re.sub(r"(## 6\. Design references\n.*?)### mobile\n.*?(?=\n## 7\.)", r"\1", text, flags=re.S)
        self.assertEqual(read_story(text)["gaps"], ["§6 has no ### mobile block"])

    def test_example_story_is_hu_v1(self):
        text = read(EXAMPLE_STORY)
        story = read_story(text)
        self.assertEqual(story["template"], "hu-v1")
        self.assertTrue(story["applies"])
        self.assertEqual([sections(text)[n]["title"] for n in range(1, 11)], HU_V1_TITLES)
        self.assertEqual(story["gaps"], [])


if __name__ == "__main__":
    unittest.main()
