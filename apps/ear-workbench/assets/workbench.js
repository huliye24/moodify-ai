/* Moodify Ear workbench client — MFY_EAR_PRODUCT_SURFACE_V1_001.
   Consumes the canonical Ear API only. Never derives product state locally:
   job/case states come from the server and are rendered as-is.
   Private audio, internal paths and logs never leave the API boundary. */

"use strict";

const API = window.MOODIFY_API_BASE || "/api/v1";

async function api(path, options) {
  const response = await fetch(`${API}${path}`, options);
  let body = null;
  try { body = await response.json(); } catch (_) { /* non-JSON */ }
  if (!response.ok) {
    const error = (body && body.error) || { code: "HTTP_" + response.status, message: "Request failed" };
    throw new Error(`${error.code}: ${error.message}`);
  }
  return body;
}

function stateOf(job) {
  if (!job) return { key: "neutral", label: "Unknown" };
  switch (job.status) {
    case "QUEUED": return { key: "processing", label: "Queued" };
    case "RUNNING": return { key: "processing", label: "Listening" };
    case "SUCCEEDED": return { key: "verified", label: "Succeeded" };
    case "FAILED": return { key: "failed", label: "Failed" };
    default: return { key: "neutral", label: job.status || "Unknown" };
  }
}

function authorityStateOf(caseData) {
  if (!caseData) return null;
  const state = caseData.authority_state || caseData.lifecycle_state || "";
  const s = String(state).toUpperCase();
  if (s.includes("HUMAN") || s.includes("REQUIRED")) return { key: "human", label: "Human required" };
  if (s.includes("INCONCLUSIVE")) return { key: "inconclusive", label: "Inconclusive" };
  if (s.includes("FAILED")) return { key: "failed", label: "Failed" };
  if (s.includes("DECIDED") || s.includes("VERIFIED") || s.includes("COMPLETE")) return { key: "verified", label: "Machine decided" };
  return { key: "neutral", label: state };
}

function pill(state) {
  const el = document.createElement("span");
  el.className = `pill ${state.key}`;
  const dot = document.createElement("span");
  dot.className = "dot";
  dot.setAttribute("aria-hidden", "true");
  el.appendChild(dot);
  el.appendChild(document.createTextNode(state.label));
  return el;
}

function formatTime(totalSeconds) {
  if (!Number.isFinite(totalSeconds) || totalSeconds < 0) return "0:00";
  const m = Math.floor(totalSeconds / 60);
  const s = Math.floor(totalSeconds % 60);
  return `${m}:${String(s).padStart(2, "0")}`;
}

function el(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text != null) node.textContent = text;
  return node;
}

async function loadInstrument() {
  try {
    const health = await api("/health");
    const counts = (health.queue || {});
    const total = Object.values(counts).reduce((a, b) => a + (Number(b) || 0), 0);
    document.querySelectorAll("[data-instrument]").forEach((node) => {
      const key = node.getAttribute("data-instrument");
      if (key === "queue") node.textContent = `queue ${total} job${total === 1 ? "" : "s"}`;
      if (key === "version") node.textContent = `core ${health.version || "?"}`;
      if (key === "identity") node.textContent = health.identity || "";
    });
  } catch (_) {
    document.querySelectorAll("[data-instrument]").forEach((node) => {
      node.textContent = node.getAttribute("data-instrument") === "identity" ? "" : "offline";
    });
  }
}

async function loadRecentJobs() {
  const list = document.getElementById("recent-jobs");
  if (!list) return;
  list.textContent = "";
  // The V1 surface lists jobs it created this session; a server-side job
  // index endpoint is a later package (48/53). The API client keeps the
  // session job list in localStorage (ids only, no audio).
  const ids = JSON.parse(localStorage.getItem("moodify_ear_job_ids") || "[]");
  if (ids.length === 0) {
    list.appendChild(el("p", "note", "No cases yet. Introduce one sound to begin the first Production Case."));
    return;
  }
  for (const id of ids.slice(-10).reverse()) {
    try {
      const { job } = await api(`/auditory/jobs/${id}`);
      const card = el("article", "card");
      card.appendChild(pill(stateOf(job)));
      card.appendChild(el("h3", null, `Case ${id.slice(0, 8)}…`));
      if (job.last_error) card.appendChild(el("p", null, "Evidence was retained for operator review."));
      card.appendChild(el("div", "meta", `created ${(job.created_at || "").slice(0, 19).replace("T", " ")}`));
      const link = el("a", null, "Open case");
      link.href = `case.html?id=${encodeURIComponent(id)}`;
      card.appendChild(link);
      list.appendChild(card);
    } catch (_) {
      /* job may have been pruned; skip */
    }
  }
}

async function loadJob() {
  const params = new URLSearchParams(location.search);
  const id = params.get("id");
  const host = document.getElementById("job-host");
  const poll = document.getElementById("poll");
  if (!id) {
    host.appendChild(el("div", "error-box", "Missing case id."));
    return;
  }
  let job = null;
  try {
    ({ job } = await api(`/auditory/jobs/${encodeURIComponent(id)}`));
  } catch (error) {
    host.appendChild(el("div", "error-box", error.message));
    return;
  }
  const status = stateOf(job);
  document.getElementById("case-pill").replaceChildren(pill(status));
  document.getElementById("case-id").textContent = id;

  const authority = document.getElementById("authority-pill");
  if (authority) authority.replaceChildren(pill(authorityStateOf(null)));

  // steps
  const steps = ["Listen", "Represent", "Judge", "Intervene", "Verify", "Learn"];
  const stepper = document.getElementById("stepper");
  if (stepper) {
    stepper.textContent = "";
    const order = { QUEUED: 0, RUNNING: 1, SUCCEEDED: 5, FAILED: 1 };
    const idx = order[job.status] ?? 0;
    steps.forEach((label, i) => {
      const node = el("span", "stage");
      const b = el("b", null, label);
      node.appendChild(b);
      node.appendChild(el("span", null, i < idx ? "done" : i === idx && job.status === "RUNNING" ? "active" : "pending"));
      if (job.status === "FAILED" && i === 1) node.appendChild(el("span", null, "failed"));
      stepper.appendChild(node);
    });
  }

  if (job.status === "QUEUED" || job.status === "RUNNING") {
    poll.hidden = false;
    poll.textContent = "Refreshing every 4s…";
    setTimeout(() => location.reload(), 4000);
  } else if (job.status === "SUCCEEDED" && job.case_dir) {
    poll.hidden = true;
    const link = el("a", "btn btn-primary", "View result");
    link.href = `result.html?id=${encodeURIComponent(id)}`;
    poll.replaceChildren(link);
  } else if (job.status === "FAILED") {
    poll.hidden = true;
    poll.replaceChildren(el("div", "error-box", "Processing failed. The evidence was retained for operator review; contact support with the case id above."));
  }
}

async function loadResult() {
  const params = new URLSearchParams(location.search);
  const id = params.get("id");
  const host = document.getElementById("result-host");
  if (!id) {
    host.appendChild(el("div", "error-box", "Missing case id."));
    return;
  }
  let payload = null;
  try {
    payload = await api(`/auditory/jobs/${encodeURIComponent(id)}/result`);
  } catch (error) {
    host.appendChild(el("div", "error-box", error.message));
    return;
  }
  const job = payload.job || {};
  const caseData = payload.production_case || {};
  const review = payload.algorithmic_review || {};
  const scores = payload.algorithmic_scores || {};
  const manifest = payload.case_manifest || {};

  document.getElementById("case-pill").replaceChildren(pill(stateOf(job)));
  document.getElementById("case-id").textContent = id;
  const authority = document.getElementById("authority-pill");
  if (authority) authority.replaceChildren(pill(authorityStateOf(caseData)));

  // ---- layer 1: findings, no raw JSON ----
  const findings = document.getElementById("findings");
  findings.textContent = "";
  if (caseData.objective) {
    const f = el("div", "finding");
    f.appendChild(el("b", null, "Objective"));
    f.appendChild(el("span", null, caseData.objective));
    findings.appendChild(f);
  }
  const items = Array.isArray(review.ranking) ? review.ranking : [];
  if (items.length > 0) {
    items.forEach((item) => {
      const label = typeof item === "string" ? item : (item.id || item.name || item.candidate || "Item");
      const rank = typeof item === "object" && "rank" in item ? ` — rank ${item.rank}` : "";
      const f = el("div", "finding");
      f.appendChild(el("b", null, `Finding${rank}`));
      f.appendChild(el("span", null, String(label)));
      findings.appendChild(f);
    });
  } else if (review.reviewer_id || scores.reviewer_id) {
    findings.appendChild(el("div", "finding", "No ranking items in the review record."));
  }
  if (review.notes) {
    const f = el("div", "finding");
    f.appendChild(el("b", null, "Reviewer note"));
    f.appendChild(el("span", null, review.notes));
    findings.appendChild(f);
  }
  const revId = review.reviewer_id || scores.reviewer_id || (caseData.authority_state || "").toLowerCase().includes("human") ? "designated human reviewer" : null;
  document.getElementById("reviewer-line").textContent = revId ? `Decision authority: ${revId}` : "";

  // ---- layer 2: measurements ----
  const measures = document.getElementById("measurements");
  measures.textContent = "";
  const scoreRows = scores.scores;
  if (scoreRows && typeof scoreRows === "object") {
    for (const [name, value] of Object.entries(scoreRows).slice(0, 8)) {
      measures.appendChild(el("tr", null, null)).appendChild(el("td", null, name)).parentElement.appendChild(el("td", null, String(typeof value === "number" ? value.toFixed(3) : value)));
    }
  }
  if (caseData.measurement_ids && caseData.measurement_ids.length) {
    caseData.measurement_ids.forEach((m) => {
      const tr = document.createElement("tr");
      tr.appendChild(el("td", null, "measurement"));
      tr.appendChild(el("td", null, m));
      measures.appendChild(tr);
    });
  }

  // ---- layer 3: methods & versions ----
  document.getElementById("method-version").textContent =
    `Formula: ${scores.formula_version || "unknown"} · Schema: ${manifest.schema_version || review.schema_version || "unknown"}`;
  const evidenceList = document.getElementById("evidence-list");
  evidenceList.textContent = "";
  (caseData.evidence_ids || []).forEach((e) => {
    const li = document.createElement("li");
    li.textContent = e;
    evidenceList.appendChild(li);
  });
  if (caseData.source_id) document.getElementById("source-id").textContent = `Source: ${caseData.source_id}`;
}

async function loadStatus() {
  try {
    const health = await api("/health");
    document.getElementById("status-product").textContent = health.product || "?";
    document.getElementById("status-version").textContent = health.version || "?";
    document.getElementById("status-identity").textContent = health.identity || "?";
    const queue = health.queue || {};
    const rows = document.getElementById("queue-rows");
    rows.textContent = "";
    Object.entries(queue).forEach(([name, count]) => {
      const tr = document.createElement("tr");
      tr.appendChild(el("td", null, name));
      tr.appendChild(el("td", null, String(count)));
      rows.appendChild(tr);
    });
  } catch (error) {
    document.getElementById("status-host").replaceChildren(el("div", "error-box", error.message));
  }
}

document.addEventListener("DOMContentLoaded", () => {
  loadInstrument();
  const page = document.body.dataset.page;
  if (page === "home") loadRecentJobs();
  if (page === "case") loadJob();
  if (page === "result") loadResult();
  if (page === "status") loadStatus();

  const form = document.getElementById("new-case-form");
  if (form) {
    form.addEventListener("submit", async (event) => {
      event.preventDefault();
      const output = document.getElementById("form-output");
      const fileInput = document.getElementById("source-file");
      const objective = document.getElementById("objective");
      const submit = document.getElementById("submit-case");
      if (!fileInput.files || !fileInput.files[0]) {
        output.textContent = "Choose one audio source first.";
        return;
      }
      submit.disabled = true;
      output.textContent = "Uploading…";
      const data = new FormData();
      data.append("audio", fileInput.files[0]);
      data.append("prompt", objective.value.trim().slice(0, 1000));
      try {
        const { job } = await api("/auditory/jobs", { method: "POST", body: data });
        const ids = JSON.parse(localStorage.getItem("moodify_ear_job_ids") || "[]");
        ids.push(job.job_id);
        localStorage.setItem("moodify_ear_job_ids", JSON.stringify(ids.slice(-50)));
        location.href = `case.html?id=${encodeURIComponent(job.job_id)}`;
      } catch (error) {
        output.textContent = error.message;
        submit.disabled = false;
      }
    });
  }

  const compare = document.getElementById("compare-host");
  if (compare) {
    // Compare rows are rendered by the result page with real evidence URLs;
    // the V1 surface keeps playback strictly in the browser, never uploads.
    compare.querySelectorAll("audio").forEach((audio) => {
      audio.addEventListener("error", () => {
        const note = document.createElement("div");
        note.className = "note";
        note.textContent = "This media is not available for playback.";
        audio.replaceWith(note);
      });
    });
  }
});
