"""Skills point at each other's references and scripts by relative path; a stale path means the
agent reads nothing and guesses. This test resolves every such path.

A path is resolved against the file that mentions it, then against that file's skill folder
(SKILL.md files say `references/x.md` relative to the skill; references say `../forge-y/...`).

Run: python3 -m unittest discover -s plugins/flutter-forge/tests -v
"""
from __future__ import annotations

import glob
import os
import re
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
SKILLS = os.path.join(os.path.dirname(HERE), "skills")
LINK = re.compile(r"`((?:\.\./|references/|scripts/|presets/)[A-Za-z0-9_\-./]+\.(?:md|py|json|sh|rb))`")


def skill_dir(path: str) -> str:
    rel = os.path.relpath(path, SKILLS)
    return os.path.join(SKILLS, rel.split(os.sep, 1)[0])


class SkillLinksTest(unittest.TestCase):
    def test_every_relative_reference_resolves(self):
        broken = []
        for path in sorted(glob.glob(os.path.join(SKILLS, "**", "*.md"), recursive=True)):
            with open(path, encoding="utf-8") as fh:
                text = fh.read()
            for match in LINK.finditer(text):
                ref = match.group(1)
                candidates = [os.path.normpath(os.path.join(os.path.dirname(path), ref)),
                              os.path.normpath(os.path.join(skill_dir(path), ref))]
                if not any(os.path.exists(c) for c in candidates):
                    line = text.count("\n", 0, match.start()) + 1
                    broken.append("%s:%d  %s" % (os.path.relpath(path, SKILLS), line, ref))
        self.assertEqual(broken, [], "unresolvable references:\n" + "\n".join(broken))


if __name__ == "__main__":
    unittest.main()
