"""Exercise the published MCP entry point using the standard stdio wire format."""

from __future__ import annotations

import json
import queue
import subprocess
import sys
import threading
import unittest

from support import ROOT

from asb.lookup import get


class McpStdioTests(unittest.TestCase):
    def test_initialize_replies_before_stdin_closes(self) -> None:
        with subprocess.Popen(
            [sys.executable, "-m", "asb", "mcp"],
            cwd=ROOT,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        ) as process:
            try:
                request = {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "initialize",
                    "params": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {},
                        "clientInfo": {"name": "contract-test", "version": "1"},
                    },
                }
                process.stdin.write((json.dumps(request) + "\n").encode("utf-8"))
                process.stdin.flush()
                lines = queue.Queue()
                reader = threading.Thread(target=lambda: lines.put(process.stdout.readline()), daemon=True)
                reader.start()
                try:
                    line = lines.get(timeout=5)
                except queue.Empty:
                    self.fail("MCP did not write a complete response before stdin EOF")
                response = json.loads(line)
                self.assertEqual(response["id"], 1)
                self.assertEqual(response["result"]["protocolVersion"], "2024-11-05")
                self.assertEqual(response["result"]["serverInfo"]["name"], "agent-safe-bible")
                process.stdin.close()
                self.assertEqual(process.wait(timeout=5), 0)
                self.assertEqual(process.stdout.read(), b"")
                self.assertEqual(process.stderr.read(), b"")
            finally:
                if process.poll() is None:
                    process.kill()

    def test_multiple_messages_preserve_utf8_and_escaped_newlines(self) -> None:
        requests = [
            {"jsonrpc": "2.0", "method": "notifications/initialized"},
            {"jsonrpc": "2.0", "id": 2, "method": "tools/list"},
            {
                "jsonrpc": "2.0", "id": 3, "method": "tools/call",
                "params": {"name": "get_passage", "arguments": {"ref": "Psalm 23:1–2"}},
            },
            {
                "jsonrpc": "2.0", "id": 4, "method": "tools/call",
                "params": {"name": "get_passage", "arguments": {"ref": "John 3:16", "translation": "NIV"}},
            },
            {"jsonrpc": "2.0", "id": 5, "method": "ping"},
        ]
        process = subprocess.run(
            [sys.executable, "-m", "asb", "mcp"],
            cwd=ROOT,
            input="".join(json.dumps(request, ensure_ascii=False) + "\n" for request in requests).encode("utf-8"),
            capture_output=True,
            timeout=5,
            check=False,
        )
        self.assertEqual(process.returncode, 0, process.stderr.decode("utf-8"))
        self.assertEqual(process.stderr, b"")
        responses = [json.loads(line) for line in process.stdout.splitlines()]
        self.assertEqual([row["id"] for row in responses], [2, 3, 4, 5])
        self.assertEqual({tool["name"] for tool in responses[0]["result"]["tools"]}, {"get_passage", "list_translations"})
        passage = responses[1]["result"]
        self.assertFalse(passage["isError"])
        self.assertEqual(json.loads(passage["content"][0]["text"]), get("Psalm 23:1–2"))
        refusal = responses[2]["result"]
        self.assertTrue(refusal["isError"])
        self.assertEqual(json.loads(refusal["content"][0]["text"])["error"], "refused_translation")
        self.assertEqual(responses[3]["result"], {})


if __name__ == "__main__":
    unittest.main()
