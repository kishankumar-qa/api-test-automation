import json
import random
import time
from http.server import BaseHTTPRequestHandler, HTTPServer

TOKEN = "test-token"
REPLIES = [
    "Sure. Here is a short answer to: {p}",
    "Happy to help. About '{p}': it depends on the context, but here is a summary.",
    "Good question. In brief, {p} can be approached in a few ways.",
]
REFUSAL = "I can't follow instructions that try to override my rules."


class Handler(BaseHTTPRequestHandler):
    def _send(self, status, body):
        data = json.dumps(body).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_POST(self):
        if self.path != "/v1/chat":
            return self._send(404, {"error": "not found"})
        if self.headers.get("Authorization") != f"Bearer {TOKEN}":
            return self._send(401, {"error": "unauthorized"})
        length = int(self.headers.get("Content-Length", 0))
        try:
            body = json.loads(self.rfile.read(length) or b"{}")
        except json.JSONDecodeError:
            return self._send(400, {"error": "invalid JSON"})
        prompt = body.get("prompt")
        if not isinstance(prompt, str) or not prompt.strip():
            return self._send(400, {"error": "prompt is required"})
        if len(prompt) > 500:
            return self._send(413, {"error": "prompt too long"})
        max_tokens = body.get("max_tokens", 50)
        if not isinstance(max_tokens, int) or max_tokens < 1:
            return self._send(400, {"error": "max_tokens must be a positive integer"})
        time.sleep(random.uniform(0.05, 0.3))
        if "ignore previous instructions" in prompt.lower():
            reply = REFUSAL
        else:
            reply = random.choice(REPLIES).format(p=prompt[:40])
        words = reply.split()[:max_tokens]
        self._send(200, {
            "id": f"chat-{random.randint(1000, 9999)}",
            "model": "mock-llm-1",
            "reply": " ".join(words),
            "usage": {"prompt_tokens": len(prompt.split()), "completion_tokens": len(words)},
        })

    def log_message(self, *args):
        pass


if __name__ == "__main__":
    HTTPServer(("127.0.0.1", 8000), Handler).serve_forever()