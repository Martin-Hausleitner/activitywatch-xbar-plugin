import importlib.util
import json
import pathlib
import unittest
from datetime import datetime
from unittest import mock


SCRIPT = pathlib.Path(__file__).with_name("aw-time.10s.py")


def load_plugin():
    spec = importlib.util.spec_from_file_location("aw_time_plugin", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class PluginMenuTests(unittest.TestCase):
    def test_dropdown_contains_activitywatch_controls_and_stats(self):
        plugin = load_plugin()

        def duration_provider(start, end, tz_offset):
            del tz_offset
            days = (datetime.fromisoformat(end) - datetime.fromisoformat(start)).days
            return days * 2 * 3600

        output = plugin.render_menu(
            show_icon=False,
            today_secs=2 * 3600,
            week_secs=10 * 3600,
            now=datetime(2026, 5, 15, 12, 0).astimezone(),
            duration_provider=duration_provider,
            activitywatch_running=True,
        )

        self.assertIn("⏹ ActivityWatch stoppen", output)
        self.assertIn("▶ ActivityWatch starten", output)
        self.assertIn("📊 Statistiken", output)
        self.assertIn("--Monatsdurchschnitt/Tag:", output)
        self.assertIn("--Letzte Wochen", output)
        self.assertIn("--Diese Woche:", output)
        self.assertIn("--Vorwoche:", output)
        self.assertIn("🌐 Cognitor starten (Tailscale bleibt an)", output)
        self.assertIn("param1=--start-cognitor", output)
        self.assertIn("🔁 Cognitor Proxy rotieren + starten", output)
        self.assertIn("param1=--rotate-cognitor", output)
        self.assertIn("🧩 Lokale Services", output)
        self.assertRegex(output, r"\n[🟢🔴] FollowMyFriends")
        self.assertNotRegex(output, r"\n--[🟢🔴] FollowMyFriends")
        self.assertIn("FollowMyFriends", output)
        self.assertIn("OpenClaw Gateway", output)
        self.assertIn("Hermes Gateway", output)
        self.assertIn("Siemens Geschirrspueler", output)
        self.assertIn("param1=--service", output)
        self.assertIn("param2=clogwork", output)

    def test_stop_action_uses_timeout_before_process_kill(self):
        source = SCRIPT.read_text()
        self.assertIn("timeout=3", source)
        self.assertIn("subprocess.TimeoutExpired", source)
        self.assertIn('["pkill", "-KILL", "-x", process_name]', source)

    def test_cognitor_action_starts_detached_with_activitywatch_and_tailscale_left_on(self):
        source = SCRIPT.read_text()
        self.assertIn("COGNITOR_STOP_ACTIVITYWATCH", source)
        self.assertIn("COGNITOR_STOP_TAILSCALE", source)
        self.assertIn("COGNITOR_ROTATE_PROXY", source)
        self.assertIn('env["COGNITOR_LOAD_EXTENSIONS"] = "1"', source)
        self.assertIn('env["COGNITOR_LOAD_PROXY_MONITOR"] = "1"', source)
        self.assertIn("start_new_session=True", source)
        self.assertIn("--start-cognitor", source)
        self.assertIn("--rotate-cognitor", source)
        self.assertIn('env["COGNITOR_STOP_ACTIVITYWATCH"] = "0"', source)
        self.assertIn('env["COGNITOR_STOP_TAILSCALE"] = "0"', source)

    def test_activitywatch_health_requires_core_watchers(self):
        plugin = load_plugin()
        source = SCRIPT.read_text()

        self.assertIn("ACTIVITYWATCH_COMPONENTS", source)
        self.assertIn("missing_activitywatch_components", source)
        self.assertIn("clear_activitywatch_client_locks", source)
        self.assertIn("terminate_activitywatch_processes", source)
        self.assertIn("ACTIVITYWATCH_LOCK_DIR", source)
        self.assertIn("aw-watcher-window", source)
        self.assertNotIn('"binary"', source)
        with mock.patch.object(
            plugin,
            "missing_activitywatch_components",
            return_value=[{"label": "Fenster-Watcher"}],
        ):
            self.assertFalse(plugin.activitywatch_running())

    def test_error_menu_keeps_controls_visible(self):
        plugin = load_plugin()
        output = plugin.render_error_menu(RuntimeError("boom"))

        self.assertEqual("⚠ offline", output.splitlines()[0])
        self.assertIn("Details: boom", output)
        self.assertIn("▶ ActivityWatch starten", output)
        self.assertIn("⏹ ActivityWatch stoppen", output)
        self.assertIn("🌐 Cognitor starten (Tailscale bleibt an)", output)
        self.assertIn("🔁 Cognitor Proxy rotieren + starten", output)
        self.assertIn("🧩 Lokale Services", output)
        self.assertRegex(output, r"\n[🟢🔴] FindMySync Receiver")
        self.assertNotRegex(output, r"\n--[🟢🔴] FindMySync Receiver")
        self.assertIn("FindMySync Receiver", output)
        self.assertIn("param2=openclaw_gateway", output)
        self.assertIn("📊 Activity anzeigen", output)
        self.assertIn("🔄 Aktualisieren", output)

    def test_local_service_definitions_have_start_actions(self):
        plugin = load_plugin()
        service_ids = {item["id"] for item in plugin.LOCAL_SERVICES}

        self.assertIn("followmyfriends", service_ids)
        self.assertIn("findmysync_app", service_ids)
        self.assertIn("findmysync_receiver", service_ids)
        self.assertIn("openclaw_gateway", service_ids)
        self.assertIn("hermes_gateway", service_ids)
        self.assertIn("clogwork", service_ids)

    def test_app_services_are_stopped_before_restart(self):
        source = SCRIPT.read_text()
        self.assertIn("def stop_service_processes", source)
        self.assertIn('["pkill", "-TERM", "-x", process_name]', source)
        self.assertIn('was_running and service.get("app") and not label', source)

    def test_error_fallback_exits_successfully_for_xbar(self):
        source = SCRIPT.read_text()
        self.assertIn("print(render_error_menu(e))", source)
        self.assertRegex(source, r"except Exception as e:\n\s+print\(render_error_menu\(e\)\)\n\s+return 0")

    def test_status_url_overrides_open_port_for_service_status(self):
        plugin = load_plugin()
        service = {"status_url": "http://localhost/status", "status_ok_key": "ok", "ports": [1]}

        class FakeResponse:
            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc, traceback):
                return False

            def read(self):
                return json.dumps({"ok": False}).encode()

        with mock.patch.object(plugin.urllib.request, "urlopen", return_value=FakeResponse()):
            with mock.patch.object(plugin, "port_open", return_value=True):
                self.assertFalse(plugin.service_running(service))


if __name__ == "__main__":
    unittest.main()
