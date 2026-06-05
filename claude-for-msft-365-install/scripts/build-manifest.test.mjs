// Run with: node --test claude-for-msft-365-install/scripts/build-manifest.test.mjs
import assert from "node:assert/strict";
import { test } from "node:test";

import { buildParams } from "./build-manifest.mjs";

const GUID = "11111111-2222-3333-4444-555555555555";

test("no sovereign params → query string unchanged from before", () => {
  const params = buildParams(["gcp_project_id=acme-prod", "gcp_region=us-east5", "auto_connect=0"]);
  assert.equal(params.toString(), "gcp_project_id=acme-prod&gcp_region=us-east5&auto_connect=0");
});

test("GCC-High needs only graph_client_id — the cloud is auto-detected at sign-in", () => {
  const params = buildParams([`graph_client_id=${GUID}`, "entra_sso=1"]);
  assert.equal(params.get("graph_client_id"), GUID);
  assert.equal(params.get("graph_cloud"), null);
});

test("each cloud value passes with graph_client_id", () => {
  for (const cloud of ["us-gov-high", "us-gov-dod", "china"]) {
    const params = buildParams([`graph_client_id=${GUID}`, "entra_sso=1", `graph_cloud=${cloud}`]);
    assert.equal(params.get("graph_cloud"), cloud);
  }
});

test("graph_cloud=global passes without graph_client_id", () => {
  const params = buildParams(["graph_cloud=global"]);
  assert.equal(params.get("graph_cloud"), "global");
});

test("non-global cloud without graph_client_id fails with a clear message", () => {
  assert.throws(() => buildParams(["graph_cloud=us-gov-dod"]), /requires a graph_client_id/);
});

test("unrecognized cloud values fail — URLs are not accepted", () => {
  for (const bad of ["us-gov", "GCC-High", "https://graph.microsoft.us", "dod"]) {
    assert.throws(
      () => buildParams([`graph_client_id=${GUID}`, "entra_sso=1", `graph_cloud=${bad}`]),
      /not a recognized value/,
      bad,
    );
  }
});

test("removed URL params are rejected as unknown keys", () => {
  assert.throws(() => buildParams(["graph_endpoint=https://dod-graph.microsoft.us"]), /unknown key/);
  assert.throws(() => buildParams(["graph_auth_endpoint=https://login.microsoftonline.us"]), /unknown key/);
});
