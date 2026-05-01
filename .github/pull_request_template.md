## Summary

<!-- 1–3 bullets describing what this PR changes and why. -->

## Test plan

<!-- How did you verify this works? Tick what applies and add details. -->

- [ ] `pnpm run build` runs clean
- [ ] `uv run pytest` passes locally
- [ ] `uv run djlint src/sphinx_lumina_theme/theme/ --check` passes (if templates changed)
- [ ] Manually loaded the docs build (`uv run sphinx-build docs docs/_build/html`) and exercised the affected feature in light + dark mode

## Screenshots / recordings

<!-- For any visual change, drop a before/after image or short clip here. -->

## Notes for reviewers

<!-- Anything non-obvious: tradeoffs, follow-ups, related issues. -->
