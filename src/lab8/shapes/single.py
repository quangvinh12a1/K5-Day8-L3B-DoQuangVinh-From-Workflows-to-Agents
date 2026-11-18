"""Shape B — one ReAct agent. Student work.

Use `lab8.runtime.run_react` with max_steps=8. `decide` may pick a read tool.
It must not call `issue_refund`. After the loop, the host validates the quote
and is the only writer.

A decide() that trusts ticket text over the order row will fail hidden claims
where the customer overstates the delay or cites a superseded clause.

Per-order cap: an order may already have been refunded by an earlier claim.
The read tool `lookup_refund_history` shows how much. The host still enforces
the cap, so pass the full quote to `durability.issue_refund`, not a net amount.

Caps: stop at 8 steps. Count model calls in the Budget so cost stays comparable.

Trace contract v1 (docs/contracts.md): return a trace_path to a JSON file written in this run,
{"run_id": <same run_id>, "events": [...]}, on every return path including early
ones. `lab8.trace.Trace` does this; your own tracer is fine if it matches.
"""

from __future__ import annotations

import sqlite3
from typing import Any

from lab8.db import connect
from lab8.durability import issue_refund
from lab8.mock_llm import complete
from lab8.runtime import run_react
from lab8.schemas import Budget, RunResult, make_run_id
from lab8.shapes.common import finish
from lab8.trace import Trace
from lab8.tools import get_claim_view, tool_cost


def run_claim(
    claim_id: str,
    *,
    seed: int,
    store_path: str,
    crash_at: str | None = None,
) -> RunResult:
    conn = connect(store_path)
    try:
        return _run(conn, claim_id, seed=seed, crash_at=crash_at)
    finally:
        conn.close()


def _run(
    conn: sqlite3.Connection,
    claim_id: str,
    *,
    seed: int,
    crash_at: str | None,
) -> RunResult:
    budget = Budget()
    run_id = make_run_id("single", claim_id, seed)
    trace = Trace(run_id)
    claim_view: dict[str, Any] | None = None
    order_view: dict[str, Any] | None = None

    budget.add_tool(tool_cost())
    claim_view = get_claim_view(conn, claim_id)
    if not claim_view["found"]:
        trace.add("error", {"reason": "unknown_claim"})
        return finish(
            conn,
            shape="single",
            claim_id=claim_id,
            seed=seed,
            status="failed",
            proposal_amount=0,
            budget=budget,
            trace=trace,
            error_reason="unknown_claim",
        )

    trace.add(
        "claim",
        {
            "claim_id": claim_view["claim_id"],
            "order_id": claim_view["order_id"],
        },
    )
    if not claim_view["order_id"]:
        trace.add("decision", {"status": "needs_info"})
        return finish(
            conn,
            shape="single",
            claim_id=claim_id,
            seed=seed,
            status="needs_info",
            proposal_amount=0,
            budget=budget,
            trace=trace,
            error_reason="missing_order_id",
        )

    def decide(observation: dict[str, Any]) -> dict[str, Any]:
        nonlocal claim_view, order_view
        complete(budget, seed=seed, purpose="react", prompt="choose a read-only investigation tool")

        last_tool = observation.get("last_tool")
        last_result = observation.get("last_result")

        if last_tool is None:
            return {
                "tool": "lookup_order",
                "args": {
                    "order_id": claim_view["order_id"],
                    "principal_id": claim_view["principal_id"],
                },
            }

        if last_tool == "lookup_order":
            order_view = last_result
            if not order_view or not order_view.get("visible"):
                return {
                    "final": {
                        "status": "escalated",
                        "error_reason": order_view.get("reason") if order_view else "order_lookup_failed",
                    }
                }
            trace.add(
                "order_lookup",
                {
                    "visible": True,
                    "reason": order_view["reason"],
                },
            )
            return {"tool": "lookup_policy", "args": {}}

        if last_tool == "lookup_policy":
            policy_count = len(last_result.get("policies") or [])
            trace.add("policy_lookup", {"policy_count": policy_count})
            return {
                "tool": "lookup_refund_history",
                "args": {
                    "order_id": claim_view["order_id"],
                    "principal_id": claim_view["principal_id"],
                },
            }

        if last_tool == "lookup_refund_history":
            return {
                "tool": "compute_compensation",
                "args": {"order": order_view["order"]},
            }

        if last_tool == "compute_compensation":
            return {"final": {"status": "quote", "quote": last_result}}

        return {"final": {"status": "failed", "error_reason": "unexpected_react_action"}}

    react = run_react(
        conn,
        budget,
        observation={"claim": {"claim_id": claim_id}},
        decide=decide,
        max_steps=8,
        worker=True,
    )
    final = react["final"]

    if final["status"] == "needs_info":
        trace.add("decision", {"status": "needs_info"})
        return finish(
            conn,
            shape="single",
            claim_id=claim_id,
            seed=seed,
            status="needs_info",
            proposal_amount=0,
            budget=budget,
            trace=trace,
            error_reason=final["error_reason"],
        )

    if final["status"] == "escalated":
        trace.add("decision", {"status": "escalated"})
        return finish(
            conn,
            shape="single",
            claim_id=claim_id,
            seed=seed,
            status="escalated",
            proposal_amount=0,
            budget=budget,
            trace=trace,
            error_reason=final["error_reason"],
        )

    if final["status"] == "failed":
        trace.add("decision", {"status": "failed", "reason": final["error_reason"]})
        return finish(
            conn,
            shape="single",
            claim_id=claim_id,
            seed=seed,
            status="failed",
            proposal_amount=0,
            budget=budget,
            trace=trace,
            error_reason=final["error_reason"],
        )

    quote = final["quote"]
    proposal = int(quote["amount_vnd"])
    trace.add(
        "quote",
        {
            "amount_vnd": proposal,
            "reason": quote["reason"],
            "clause_ids": quote["clause_ids"],
        },
    )

    if proposal <= 0:
        trace.add("decision", {"status": "denied"})
        return finish(
            conn,
            shape="single",
            claim_id=claim_id,
            seed=seed,
            status="denied",
            proposal_amount=0,
            budget=budget,
            trace=trace,
            error_reason=quote["reason"],
        )

    trace.add("refund_requested", {"proposal_amount": proposal})
    trace.write()
    outcome = issue_refund(conn, claim_id, proposal, crash_at=crash_at)

    if not outcome["ok"]:
        status = "failed" if outcome["conflict"] else "denied"
        return finish(
            conn,
            shape="single",
            claim_id=claim_id,
            seed=seed,
            status=status,
            proposal_amount=proposal,
            budget=budget,
            trace=trace,
            error_reason=outcome["reason"],
        )

    return finish(
        conn,
        shape="single",
        claim_id=claim_id,
        seed=seed,
        status="resolved",
        proposal_amount=proposal,
        budget=budget,
        trace=trace,
        error_reason=None,
    )
