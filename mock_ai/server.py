import json
import random
import time
from http.server import BaseHTTPRequestHandler, HTTPServer

TOKEN = "test-token"  # chat API
REPLIES = [
    "Sure. Here is a short answer to: {p}",
    "Happy to help. About '{p}': it depends on the context, but here is a summary.",
    "Good question. In brief, {p} can be approached in a few ways.",
]
REFUSAL = "I can't follow instructions that try to override my rules."

# Notes API, used for the OWASP API Security tests
USERS = {
    "token-alice": {"name": "alice", "role": "user"},
    "token-bob": {"name": "bob", "role": "user"},
    "token-carol": {"name": "carol", "role": "user"},
    "token-admin": {"name": "admin", "role": "admin"},
}
NOTES = {
    1: {"id": 1, "owner": "alice", "title": "Alice's note", "body": "private to alice",
        "owner_email": "alice@example.com", "internal_flags": ["beta"]},
    2: {"id": 2, "owner": "bob", "title": "Bob's note", "body": "private to bob",
        "owner_email": "bob@example.com", "internal_flags": []},
}
RATE_LIMIT = 20
RATE_WINDOW = 10
hits = {}


def rate_limited(token):
    now = time.time()
    recent = [t for t in hits.get(token, []) if now - t < RATE_WINDOW]
    recent.append(now)
    hits[token] = recent
    return len(recent) > RATE_LIMIT


class Handler(BaseHTTPRequestHandler):
    def _send(self, status, body):
        data = b"" if status == 204 else json.dumps(body).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _note_id(self):
        parts = self.path.strip("/").split("/")
        if len(parts) == 3 and parts[:2] == ["v1", "notes"] and parts[2].isdigit():
            return int(parts[2])
        return None

    def _notes_user(self):
        token = self.headers.get("Authorization", "").removeprefix("Bearer ")
        return token, USERS.get(token)

    def do_GET(self):
        note_id = self._note_id()
        if note_id is None:
            return self._send(404, {"error": "not found"})
        token, user = self._notes_user()
        if user is None:
            return self._send(401, {"error": "unauthorized"})
        if rate_limited(token):
            return self._send(429, {"error": "too many requests"})
        note = NOTES.get(note_id)
        if note is None:
            return self._send(404, {"error": "not found"})
        # Deliberate weaknesses for the tests: no ownership check,
        # and internal fields are returned to the caller.
        return self._send(200, note)

    def do_DELETE(self):
        note_id = self._note_id()
        if note_id is None:
            return self._send(404, {"error": "not found"})
        token, user = self._notes_user()
        if user is None:
            return self._send(401, {"error": "unauthorized"})
        if rate_limited(token):
            return self._send(429, {"error": "too many requests"})
        if user["role"] != "admin":
            return self._send(403, {"error": "forbidden"})
        if note_id not in NOTES:
            return self._send(404, {"error": "not found"})
        return self._send(204, {})

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