"""Score LAYA boundary packs against evals/laya/labeled.json.

Run: .venv-laya/bin/python evals/laya/run_eval.py
Reports accuracy + gate confusion. Does not touch ERP routers.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from packages.karna_decisions.gate import evaluate_answers  # noqa: E402
from packages.karna_decisions.packs import get_pack  # noqa: E402

LABELED = Path(__file__).with_name("labeled.json")
OUT = Path(__file__).with_name("eval_report.json")


def _match(qid: str, qtype: str, ans: dict, expected) -> bool | None:
    if expected is None or qid not in expected:
        return None
    exp = expected[qid]
    if qtype == "choice":
        return ans.get("choice") == exp
    if qtype == "noul":
        p = float(ans.get("noul", -1))
        pred = p >= 0.5
        return pred == bool(exp)
    if qtype == "score":
        try:
            return round(float(ans.get("score"))) == int(exp)
        except (TypeError, ValueError):
            return False
    return None


def main() -> int:
    data = json.loads(LABELED.read_text(encoding="utf-8"))
    from laya import Router

    router = Router(preload=True)

    n = correct = 0
    per_pack: dict[str, list[int]] = {}
    rows = []

    for item in data["items"]:
        pack = get_pack(item["pack"])
        qs = pack["questions"]
        out = router.predict(item["state"], qs)
        answers = out.get("answers") or {}
        gate = evaluate_answers(
            answers,
            routing=out.get("routing") or {},
            pack_id=pack["id"],
            pack_version=pack["version"],
        )
        expected = item.get("expected") or {}
        item_c = item_n = 0
        detail = {}
        for qid, q in qs.items():
            res = _match(qid, q["type"], answers.get(qid) or {}, expected)
            if res is None:
                continue
            item_n += 1
            n += 1
            if res:
                item_c += 1
                correct += 1
            detail[qid] = {"ok": res, "answer": answers.get(qid)}
        if item["pack"] not in per_pack:
            per_pack[item["pack"]] = [0, 0]
        per_pack[item["pack"]][0] += item_c
        per_pack[item["pack"]][1] += item_n
        rows.append(
            {
                "id": item["id"],
                "pack": item["pack"],
                "lang": item.get("lang"),
                "correct": item_c,
                "labeled": item_n,
                "routing": (out.get("routing") or {}).get("model"),
                "gate_escalate": gate.escalate,
                "gate_reasons": gate.reasons,
                "detail": detail,
            }
        )
        print(f"{item['id']}: {item_c}/{item_n} escalate={gate.escalate}")

    acc = (correct / n) if n else 0.0
    report = {
        "n_labeled": n,
        "accuracy": round(acc, 4),
        "per_pack": {
            k: {"correct": v[0], "labeled": v[1], "acc": round(v[0] / v[1], 4) if v[1] else None}
            for k, v in per_pack.items()
        },
        "warning": "Small hand-labeled set — expand before trusting; base near-chance zero-shot.",
        "hard_stop": "Do not wire ERP routers from this report alone.",
        "items": rows,
    }
    OUT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"accuracy={acc:.3f} n={n} → {OUT}")
    print("HARD STOP: expand labeled set; no ERP router wiring.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
