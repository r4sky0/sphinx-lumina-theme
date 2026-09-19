"""Test Pagefind build integration failure handling."""

import subprocess
from types import SimpleNamespace

import sphinx_lumina_theme as theme


def _app(**options):
    return SimpleNamespace(
        outdir="/tmp/lumina-test-build",
        builder=SimpleNamespace(format="html", theme_options={"search_backend": "pagefind", **options}),
    )


def test_missing_pagefind_is_non_fatal(monkeypatch):
    """A missing local executable should skip indexing without a warning error."""
    monkeypatch.setattr("shutil.which", lambda name: None)
    messages = []
    monkeypatch.setattr(theme.logger, "info", lambda message, *args: messages.append(message % args))
    theme._run_pagefind(_app(), None)
    assert any("skipping indexing" in message for message in messages)


def test_pagefind_nonzero_exit_is_reported(monkeypatch):
    """A failed index command should be reported and leave the build intact."""
    monkeypatch.setattr("shutil.which", lambda name: "/usr/local/bin/pagefind")
    monkeypatch.setattr(
        subprocess,
        "run",
        lambda *args, **kwargs: (_ for _ in ()).throw(
            subprocess.CalledProcessError(1, args[0], stderr="invalid site")
        ),
    )
    messages = []
    monkeypatch.setattr(theme.logger, "warning", lambda message, *args: messages.append(message % args))
    theme._run_pagefind(_app(), None)
    assert "Pagefind indexing failed: invalid site" in messages


def test_pagefind_timeout_is_bounded(monkeypatch):
    """The configured timeout should be passed to the subprocess."""
    monkeypatch.setattr("shutil.which", lambda name: "/usr/local/bin/pagefind")
    calls = []

    def run(*args, **kwargs):
        calls.append(kwargs)
        raise subprocess.TimeoutExpired(args[0], kwargs["timeout"])

    monkeypatch.setattr(subprocess, "run", run)
    messages = []
    monkeypatch.setattr(theme.logger, "warning", lambda message, *args: messages.append(message % args))
    theme._run_pagefind(_app(pagefind_timeout="7"), None)
    assert calls[0]["timeout"] == 7.0
    assert "Pagefind indexing timed out after 7.0 seconds" in messages
