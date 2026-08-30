import assert from "node:assert/strict";
import fs from "node:fs";
import test from "node:test";

const scope = fs.readFileSync("MOOD_SCOPE_FREEZE.md", "utf8");
const agents = fs.readFileSync("AGENTS.md", "utf8");

test("INV-026-01: scope freeze is in the repository authority path", () => {
  assert.match(agents, /MOOD_SCOPE_FREEZE\.md/);
  assert.match(scope, /CANONICAL FOR GENESIS 026/);
});

test("INV-026-02: all four entropy treatments are defined", () => {
  for (const treatment of ["KEEP", "FREEZE", "ARCHIVE", "DELETE"]) {
    assert.ok(scope.includes(`| \`${treatment}\``));
  }
});

test("INV-026-03: 027 and horizontal expansion are refused", () => {
  assert.match(scope, /package 027/);
  assert.match(scope, /new horizontal numbered feature package/);
});

test("INV-026-04: calendar date cannot authorize token launch", () => {
  assert.match(scope, /September 1 is a \*\*Go\/No-Go review date\*\*/);
  assert.match(scope, /not an automatic launch authorization/);
  assert.match(scope, /action-time human approval/);
});

test("INV-026-05: destructive cleanup remains reviewed and recoverable", () => {
  assert.match(scope, /DELETE.*classification before it is a filesystem action/s);
  assert.match(scope, /migration\/rollback/);
});

test("INV-026-06: completion is based on a real proof-producing network", () => {
  for (const required of [
    "WORLD is reachable",
    "PROTOCOL is readable",
    "PORTAL can connect a wallet",
    "Contribution can produce a verifiable Proof",
    "Agent and a Node can produce real activity",
  ]) {
    assert.match(scope, new RegExp(required));
  }
});
