"""Invalid tool calls must fail closed without disconnecting the MCP client."""

from __future__ import annotations

import json
import subprocess
import sys
import unittest

from support import ROOT


class McpToolValidationTests(unittest.TestCase):
    def _exchange(self, requests: list[dict]) -> list[dict]:
        process = subprocess.run(
            [sys.executable, "-m", "asb", "mcp"],
            cwd=ROOT,
            input="".join(json.dumps(request) + "\n" for request in requests),
            text=True,
            capture_output=True,
            timeout=5,
            check=False,
        )
        self.assertEqual(process.returncode, 0, process.stderr)
        self.assertEqual(process.stderr, "")
        return [json.loads(line) for line in process.stdout.splitlines()]

    def _assert_invalid_call(self, params: object, *, omit_params: bool = False) -> None:
        request = {"jsonrpc": "2.0", "id": "bad-call", "method": "tools/call"}
        if not omit_params:
            request["params"] = params
        responses = self._exchange([
            request,
            {"jsonrpc": "2.0", "id": 0, "method": "ping"},
        ])
        self.assertEqual(len(responses), 2)
        error, pong = responses
        self.assertEqual(set(error), {"jsonrpc", "id", "error"})
        self.assertEqual(error["jsonrpc"], "2.0")
        self.assertEqual(error["id"], "bad-call")
        self.assertEqual(error["error"]["code"], -32602)
        self.assertIsInstance(error["error"]["message"], str)
        self.assertTrue(error["error"]["message"])
        self.assertEqual(pong, {"jsonrpc": "2.0", "id": 0, "result": {}})

    def test_invalid_call_params_leave_connection_usable(self) -> None:
        self._assert_invalid_call(None, omit_params=True)
        for params in (None, False, 0, "", [], [1], "get_passage"):
            with self.subTest(params=params):
                self._assert_invalid_call(params)

    def test_missing_or_unknown_tool_names_are_protocol_errors(self) -> None:
        self._assert_invalid_call({})
        for name in (None, False, 0, [], {}, "", "unknown_tool"):
            with self.subTest(name=name):
                self._assert_invalid_call({"name": name})

    def test_get_passage_enforces_advertised_argument_schema(self) -> None:
        self._assert_invalid_call({"name": "get_passage"})
        invalid_arguments = [None, False, 0, "", [], [1], {}, {"extra": "value"}]
        for value in (None, False, 0, [], {}):
            invalid_arguments.append({"ref": value})
            invalid_arguments.append({"ref": "John 3:16", "translation": value})
        invalid_arguments.append({"ref": "John 3:16", "extra": "value"})
        for arguments in invalid_arguments:
            with self.subTest(arguments=arguments):
                self._assert_invalid_call({"name": "get_passage", "arguments": arguments})

    def test_list_translations_rejects_arguments_outside_its_schema(self) -> None:
        for arguments in (None, False, 0, "", [], [1], {"ref": "John 3:16"}):
            with self.subTest(arguments=arguments):
                self._assert_invalid_call({"name": "list_translations", "arguments": arguments})

    def test_list_translations_accepts_omitted_or_empty_arguments(self) -> None:
        responses = self._exchange([
            {"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": "list_translations"}},
            {"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {"name": "list_translations", "arguments": {}}},
        ])
        self.assertEqual([response["id"] for response in responses], [1, 2])
        self.assertEqual(responses[0]["result"], responses[1]["result"])
        result = responses[0]["result"]
        self.assertFalse(result["isError"])
        translations = json.loads(result["content"][0]["text"])
        self.assertEqual(translations["default"], "BSB")
        self.assertEqual(set(translations["allowed"]), {"BSB", "WEB", "KJV"})


if __name__ == "__main__":
    unittest.main()
