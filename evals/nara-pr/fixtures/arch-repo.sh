#!/usr/bin/env bash
# Build a throwaway repo for the nara-pr structure-diagram task.
# Usage: arch-repo.sh <empty-dir>
# main: the API settles a request inline. The branch routes it through three new
# modules (queue -> worker -> store), so new call relations span four modules.
# No rendering file changes. A correct run proposes an architecture/sequence
# diagram with the countable reason, and with no archify installed, skips it in
# one line instead of inventing an image.
set -euo pipefail
dir="${1:?usage: arch-repo.sh <empty-dir>}"
mkdir -p "$dir"
if [ -n "$(ls -A "$dir")" ]; then
  echo "refusing: $dir is not empty (pass a fresh dir, e.g. \"\$(mktemp -d)\")" >&2
  exit 2
fi
cd "$dir"
git init -q -b main
git config user.name "dev" && git config user.email "dev@example.com"

mkdir -p src
cat > src/api.py <<'PY'
from src.settlement import settle


def post_settlement(request):
    return settle(request["order_id"], request["amount"])
PY
cat > src/settlement.py <<'PY'
def settle(order_id, amount):
    return {"order_id": order_id, "amount": amount, "status": "settled"}
PY
git add -A && git commit -q -m "chore: initial"
git update-ref refs/remotes/origin/main HEAD

git checkout -q -b feature/PROJ-97-settlement-queue
cat > src/queue.py <<'PY'
from collections import deque

PENDING = deque()


def enqueue(job):
    PENDING.append(job)


def dequeue():
    return PENDING.popleft() if PENDING else None
PY
cat > src/store.py <<'PY'
RESULTS = {}


def save(result):
    RESULTS[result["order_id"]] = result
PY
cat > src/worker.py <<'PY'
from src import queue, store
from src.settlement import settle


def run_once():
    job = queue.dequeue()
    if job is None:
        return False
    store.save(settle(job["order_id"], job["amount"]))
    return True
PY
cat > src/api.py <<'PY'
from src import queue


def post_settlement(request):
    queue.enqueue({"order_id": request["order_id"], "amount": request["amount"]})
    return {"order_id": request["order_id"], "status": "queued"}
PY
git add -A && git commit -qm "PROJ-97 feat: process settlements through a queue"
echo "built $(pwd) on $(git rev-parse --abbrev-ref HEAD) at $(git rev-parse --short HEAD)"
