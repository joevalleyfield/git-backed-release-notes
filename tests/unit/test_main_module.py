from __future__ import annotations

from unittest import mock

import pytest

from git_release_notes import __main__ as main_module


def test_install_signal_handlers_registers_signals_and_stops_loop(monkeypatch: pytest.MonkeyPatch) -> None:
    loop = mock.Mock()
    registered_handlers: dict[int, object] = {}

    def fake_signal(signum: int, handler: object) -> None:
        registered_handlers[signum] = handler

    monkeypatch.setattr(main_module.signal, "signal", fake_signal)

    main_module._install_signal_handlers(loop)

    handled_signals = set(registered_handlers)
    expected_signals = {main_module.signal.SIGINT}
    sigterm = getattr(main_module.signal, "SIGTERM", None)
    if sigterm is not None:
        expected_signals.add(sigterm)

    assert handled_signals == expected_signals

    handler = registered_handlers[main_module.signal.SIGINT]
    handler(main_module.signal.SIGINT, None)

    loop.add_callback_from_signal.assert_called_once_with(loop.stop)


def test_start_ioloop_swallows_keyboard_interrupt_and_stops_loop() -> None:
    loop = mock.Mock()
    loop.start.side_effect = KeyboardInterrupt

    main_module._start_ioloop(loop)

    loop.start.assert_called_once()
    loop.stop.assert_called_once()


def test_start_ioloop_passes_through_when_loop_exits_cleanly() -> None:
    loop = mock.Mock()

    main_module._start_ioloop(loop)

    loop.start.assert_called_once()
    loop.stop.assert_not_called()
