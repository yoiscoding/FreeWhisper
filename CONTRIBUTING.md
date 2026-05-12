# Contributing to FreeWhisper

Thanks for thinking about contributing. FreeWhisper is a tiny project — the kind of thing one person can fully understand in an evening. Pull requests, issues, and ideas are all welcome.

---

## Quick start for contributors

```bash
# 1. Fork and clone
git clone https://github.com/YOUR-USERNAME/FreeWhisper.git
cd FreeWhisper

# 2. Build a dev environment
arch -arm64 python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 3. Run from source
python freewhisper.py
```

You'll need an Apple Silicon Mac. There's no way around that — MLX is arm64-only.

---

## What to work on

Open issues with the **good first issue** label are picked to be self-contained. Anything in the [Roadmap](README.md#roadmap) is fair game too.

Genuinely useful things you can do, even without writing code:
- Test on macOS versions we haven't (especially older ones)
- Improve the README's troubleshooting section with anything that tripped you up
- Translate the README into other languages
- Submit screen recordings / screenshots for the README

---

## Code style

- Python 3.10+ syntax is fine.
- Format with `black` (line length 100). No config file needed — defaults are good.
- Lint with `ruff`. We're not strict on every rule but obvious smells get flagged.
- Keep functions short. If you're adding a new feature, please add a clear docstring.

```bash
pip install black ruff
black freewhisper.py
ruff check freewhisper.py
```

---

## How to test changes

There's no test suite yet — this project is small enough that manual testing covers it. Before opening a PR, please confirm:

1. **It launches.** `python freewhisper.py` produces a 🎙️ in the menu bar.
2. **The hotkey records.** Hold Right Option, talk for 3 seconds, release. Icon goes 🎙️ → 🔴 → ⏳ → 🎙️.
3. **The transcript pastes.** Open Notes, repeat step 2, verify text appears at the cursor.
4. **Glossary loads.** Add a word to `~/.freewhisper/glossary.txt`, restart the app, transcribe again.

If you're touching code in a specific area, please test that area extra. If you're refactoring, please test everything.

A proper test suite (with mocked audio + transcription) would be a great contribution.

---

## Pull request checklist

- [ ] My change works (see manual testing checklist above).
- [ ] I've described **what** the change does and **why** in the PR description.
- [ ] If I changed user-facing behavior, I updated the README.
- [ ] My code follows the existing style (black-formatted, mostly ruff-clean).
- [ ] I haven't added a new dependency without discussing it in an issue first.

---

## Reporting bugs

[Open a bug issue](https://github.com/yoiscoding/FreeWhisper/issues/new?template=bug_report.yml) using the template. The template asks for the info that helps most:

- Your macOS version (`sw_vers`)
- Your Mac model
- Python version
- `pip freeze` output
- Steps to reproduce
- What you saw vs what you expected
- Contents of `/tmp/freewhisper.log` if relevant

---

## Suggesting features

[Open a feature request](https://github.com/yoiscoding/FreeWhisper/issues/new?template=feature_request.yml). Keep it focused on the *problem* you're trying to solve, not just the *solution* you have in mind — sometimes there's a better fix you haven't considered.

---

## What we probably won't merge

- Features that send audio or transcripts off the user's Mac by default. FreeWhisper's "100% local" promise is the whole point.
- Heavy GUI rewrites (Electron, Qt, etc.). The menu-bar-only approach is intentional.
- Dependencies that aren't strictly necessary. Smaller install = happier users.
- Code that drops support for the lowest tested macOS version without a strong reason.

---

## License of contributions

By contributing, you agree that your contributions will be licensed under the same license as FreeWhisper itself — **GPL v3**.

In practice this means: your code can be used by anyone, freely, but anyone who distributes it has to keep it open source. That's the whole point of GPL.

---

## Code of conduct

Be kind. Assume good intent. If someone's stuck on a problem you find trivial, remember you were once stuck on something that's now trivial to you. Disagreements about technical decisions are fine; personal attacks aren't.

That's it. Welcome to the project.
