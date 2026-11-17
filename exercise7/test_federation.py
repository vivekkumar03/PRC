"""Federation test: alice@cr261517.matrix.test creates a room, invites bob@partner.matrix.test,
both exchange messages and a file. Uses only the Matrix client-server API."""
import json
import time
import urllib.request

A, B = "http://localhost:8008", "http://localhost:8009"


def call(base, method, path, token=None, body=None, raw=None, ctype="application/json"):
    data = raw if raw is not None else (json.dumps(body).encode() if body is not None else None)
    req = urllib.request.Request(base + path, data=data, method=method)
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    if data is not None:
        req.add_header("Content-Type", ctype)
    return json.load(urllib.request.urlopen(req))


def login(base, user, pw):
    r = call(base, "POST", "/_matrix/client/v3/login", body={
        "type": "m.login.password", "identifier": {"type": "m.id.user", "user": user}, "password": pw})
    return r["access_token"]


ta = login(A, "alice", "Alice-Pass-123")
tb = login(B, "bob", "Bob-Pass-123")

room = call(A, "POST", "/_matrix/client/v3/createRoom", ta,
            {"name": "federation-test", "invite": ["@bob:partner.matrix.test"]})["room_id"]
print("room:", room)
enc = call(A, "GET", f"/_matrix/client/v3/rooms/{room}/state/m.room.encryption", ta)
print("m.room.encryption state (default for new rooms):", enc)

time.sleep(1)
call(B, "POST", f"/_matrix/client/v3/join/{room}", tb, {})
print("bob (partner.matrix.test) joined")

call(A, "PUT", f"/_matrix/client/v3/rooms/{room}/send/m.room.message/t1", ta,
     {"msgtype": "m.text", "body": "hello from cr261517.matrix.test"})
call(B, "PUT", f"/_matrix/client/v3/rooms/{room}/send/m.room.message/t2", tb,
     {"msgtype": "m.text", "body": "hello back from partner.matrix.test"})

up = call(A, "POST", "/_matrix/media/v3/upload?filename=hello.txt", ta, raw=b"file shared over federation\n",
          ctype="text/plain")
call(A, "PUT", f"/_matrix/client/v3/rooms/{room}/send/m.room.message/t3", ta,
     {"msgtype": "m.file", "body": "hello.txt", "url": up["content_uri"]})
print("file uploaded:", up["content_uri"])

time.sleep(2)
members = call(B, "GET", f"/_matrix/client/v3/rooms/{room}/joined_members", tb)["joined"]
print("members seen from partner server:", list(members))
msgs = call(B, "GET", f"/_matrix/client/v3/rooms/{room}/messages?dir=b&limit=10", tb)["chunk"]
for m in reversed(msgs):
    if m["type"] in ("m.room.message", "m.room.encrypted"):
        print(" ", m["sender"], "->", m["type"], m["content"].get("body", "<ciphertext>"))
