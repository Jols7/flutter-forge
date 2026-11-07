# Git: Conventional Commits, branches and PRs

This file applies only when the brief sets `git: commit` or `git: pr`, or when the person
explicitly asks for a commit. With `git: none` (the default), propose the message in
`result.json` (`proposed_commit`) and do nothing else.

## 1. Detect first

Look at the project's existing convention before writing anything:
- `git log --oneline -20`;
- `commitlint.config.*` or `.commitlintrc*`;
- `.github/pull_request_template.md`.

If the project uses another convention, follow it, and note that in `why[]`. If it already
uses Conventional Commits, or has no clear convention, use the rules below.

## 2. Format ([Conventional Commits 1.0](https://www.conventionalcommits.org/en/v1.0.0/))

`<type>(<scope>)!: <summary>`. The summary is imperative, in English and at most 72 characters.

| Element | Rule | Example |
|---|---|---|
| Types | `feat`, `fix`, `docs`, `refactor`, `test`, `perf`, `build`, `ci`, `chore`, `revert` | `fix(mobile): keep fee preview after rotation` |
| Scope | `mobile` (the app's area in a monorepo; also in single-app repos unless the project uses another scope) | `feat(mobile): add transfer preview` |
| Breaking change | `!` + footer `BREAKING CHANGE: <what breaks>` | `feat(mobile)!: drop Android 7 support` |
| References | Footer `Refs HU-12` / `Refs #12` only when the brief or story provides it; never invented | `Refs HU-12` |
| Body | Optional; the *why* when the summary is not enough | — |

Split the work into a few meaningful commits, not one per file:
1. `feat(mobile): add transfers data layer`
2. `feat(mobile): add transfer screen`
3. `test(mobile): cover transfer flow`

Generated files go with the change that generated them.

## 3. Branch

`<type>/<HU-or-issue>-<slug>`, e.g. `feat/HU-12-transfers`. Create it from the current
branch only when you are on the default branch; otherwise keep the branch the caller gave you.

## 4. `git: commit`

1. Check `git status`: the scope is only files of this run, plus generated files and the ARB
   files it touched.
2. Stage explicit paths. Never `git add -A` over a dirty tree that has unrelated changes; list
   those files in the report instead.
3. Commit. Never `--no-verify`. When a hook rejects the message, fix the message.
4. **No push.**

## 5. `git: pr`

Do everything from `git: commit`, then:
1. `git push -u origin <branch>`.
2. `gh pr create --title "<main commit message>" --body-file <file>` with this body:
   ```markdown
   ## Qué
   <2–4 lines: the feature and its scope>
   ## Por qué
   <the why[] entries>
   ## Dónde revisar
   <the review_points[] entries, as file:line>
   ## Pruebas
   <unit/widget/e2e results, coverage, review verdict>
   ```
3. Never merge, force-push, rebase shared branches or push to the default branch.

## 6. Report it

Record the outcome in `result.json` under `git`:

```json
{"branch": "feat/HU-12-transfers",
 "commits": [{"sha": "a1b2c3d", "message": "feat(mobile): add transfers data layer"}],
 "pr": "https://github.com/org/repo/pull/34"}
```
