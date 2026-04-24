// Photoshoot Generator frontend.
// State is kept in a simple in-memory object; nothing is persisted.

const ANGLES = ["front", "back", "side"];

const state = {
  dresses: [],          // {id, name, images: {front, back, side}}
  defaults: null,       // loaded from /api/defaults
  jobId: null,
  generating: false,
  provider: "gemini",   // "gemini" | "openai"
  concurrency: 3,       // 1..5 — how many images generate in parallel
  totals: { cost: 0, images: 0, input: 0, outputImage: 0 },
};

const $ = (sel, root = document) => root.querySelector(sel);
const $$ = (sel, root = document) => Array.from(root.querySelectorAll(sel));

function uid() { return Math.random().toString(36).slice(2, 10); }

// ---------- Prompt panel ----------
async function loadDefaults() {
  const res = await fetch("/api/defaults");
  state.defaults = await res.json();
  applyDefaultsToForm();
}

function applyDefaultsToForm() {
  $("#prompt_garment").value = state.defaults.garment;
  $("#prompt_model").value = state.defaults.model;
  $("#prompt_background").value = state.defaults.background;
  $("#prompt_output").value = state.defaults.output;
  const angles = state.defaults.angles || {};
  $("#prompt_angle_front").value = angles.front || "";
  $("#prompt_angle_back").value = angles.back || "";
  $("#prompt_angle_side").value = angles.side || "";
  if (state.defaults.provider) setProvider(state.defaults.provider);
}

function setProvider(p) {
  state.provider = p;
  $$(".seg-btn").forEach(b => b.classList.toggle("active", b.dataset.provider === p));
}

$$(".seg-btn[data-provider]").forEach(btn => {
  btn.addEventListener("click", () => setProvider(btn.dataset.provider));
});

function setConcurrency(n) {
  const v = Math.max(1, Math.min(5, parseInt(n, 10) || 3));
  state.concurrency = v;
  $$(".seg-btn[data-concurrency]").forEach(b =>
    b.classList.toggle("active", Number(b.dataset.concurrency) === v)
  );
}
$$(".seg-btn[data-concurrency]").forEach(btn => {
  btn.addEventListener("click", () => setConcurrency(btn.dataset.concurrency));
});

// Main tabs
$$(".tab").forEach(btn => {
  btn.addEventListener("click", () => {
    $$(".tab").forEach(b => b.classList.toggle("active", b === btn));
    const key = btn.dataset.tab;
    $$(".tab-body").forEach(body => {
      body.classList.toggle("active", body.dataset.tab === key);
    });
  });
});

// Angles sub-tabs
$$(".sub-tab").forEach(btn => {
  btn.addEventListener("click", () => {
    $$(".sub-tab").forEach(b => b.classList.toggle("active", b === btn));
    const key = btn.dataset.angle;
    $$(".angle-body").forEach(body => {
      body.classList.toggle("active", body.dataset.angle === key);
    });
  });
});

$("#resetPrompts").addEventListener("click", () => {
  if (confirm("Reset all prompts to defaults?")) applyDefaultsToForm();
});

$("#togglePrompts").addEventListener("click", () => {
  const p = $("#promptPanel");
  p.hidden = !p.hidden;
});

// ---------- Dress cards ----------
function addDress() {
  const dress = {
    id: uid(),
    name: `Dress ${state.dresses.length + 1}`,
    images: { front: null, back: null, side: null },
  };
  state.dresses.push(dress);
  renderDress(dress);
}

function removeDress(id) {
  state.dresses = state.dresses.filter(d => d.id !== id);
  const el = document.querySelector(`[data-dress="${id}"]`);
  if (el) el.remove();
}

function renderDress(dress) {
  const tpl = $("#dressCardTpl").content.cloneNode(true);
  const card = tpl.querySelector(".dress-card");
  card.dataset.dress = dress.id;

  const nameInput = card.querySelector(".dress-name");
  nameInput.value = dress.name;
  nameInput.addEventListener("input", e => { dress.name = e.target.value; });

  card.querySelector(".remove-dress").addEventListener("click", () => removeDress(dress.id));

  $$(".slot", card).forEach(slot => {
    const angle = slot.dataset.angle;
    const input = slot.querySelector("input[type=file]");
    const thumb = slot.querySelector(".slot-thumb");
    const img = slot.querySelector("img");
    const rm = slot.querySelector(".slot-rm");

    thumb.addEventListener("click", e => {
      if (e.target === rm) return;
      input.click();
    });
    thumb.addEventListener("dragover", e => { e.preventDefault(); slot.classList.add("drag"); });
    thumb.addEventListener("dragleave", () => slot.classList.remove("drag"));
    thumb.addEventListener("drop", e => {
      e.preventDefault();
      slot.classList.remove("drag");
      const file = e.dataTransfer.files?.[0];
      if (file && file.type.startsWith("image/")) setFile(file);
    });
    input.addEventListener("change", e => {
      const file = e.target.files?.[0];
      if (file) setFile(file);
      input.value = "";
    });
    rm.addEventListener("click", e => {
      e.stopPropagation();
      dress.images[angle] = null;
      img.hidden = true;
      img.src = "";
      rm.hidden = true;
      slot.classList.remove("has-file");
    });

    function setFile(file) {
      dress.images[angle] = file;
      const url = URL.createObjectURL(file);
      img.onload = () => URL.revokeObjectURL(url);
      img.src = url;
      img.hidden = false;
      rm.hidden = false;
      slot.classList.add("has-file");
    }
  });

  $("#dressList").appendChild(card);
}

$("#addDressBtn").addEventListener("click", addDress);

// ---------- Generation ----------
function setStatus(text, klass = "") {
  const el = $("#resultsStatus");
  el.textContent = text;
  el.className = "status " + klass;
}

function openResults() { $("#resultsPanel").hidden = false; }

function addResultCard({ dressName, angle, id }) {
  const tpl = $("#resultCardTpl").content.cloneNode(true);
  const card = tpl.querySelector(".result-card");
  card.dataset.id = id;
  const label = angle.charAt(0).toUpperCase() + angle.slice(1);
  card.querySelector(".result-title").textContent = `${dressName} · ${label}`;
  $("#resultsGrid").appendChild(card);
  return card;
}

function fillResult(card, r) {
  const img = card.querySelector(".result-img");
  img.src = r.url;
  img.hidden = false;
  card.querySelector(".result-spinner").style.display = "none";
  const a = card.querySelector(".download");
  a.href = r.url;
  a.setAttribute("download", r.filename);

  // Stash everything needed to refine this image later.
  card.classList.add("ready");
  if (r.refined) card.classList.add("refined");
  card.dataset.url = r.url;
  card.dataset.jobId = r.job_id;
  card.dataset.dressName = r.dress;
  card.dataset.angle = r.angle;
  card.dataset.prompt = r.prompt || "";

  const refineBtn = card.querySelector(".refine-btn");
  if (refineBtn) refineBtn.hidden = false;
  const hint = card.querySelector(".refine-hint");
  if (hint) hint.hidden = false;

  applyStatsToCard(card, r.meta);
  accumulateTotals(r.meta);
}

function fmtUsd(v) {
  if (v == null) return "—";
  if (v < 0.01) return `$${v.toFixed(4)}`;
  return `$${v.toFixed(3)}`;
}
function fmtTokens(n) {
  if (!n) return "0";
  if (n < 1000) return String(n);
  return `${(n / 1000).toFixed(n < 10000 ? 2 : 1)}k`;
}

function applyStatsToCard(card, meta) {
  const row = card.querySelector(".result-stats");
  if (!row || !meta) return;
  const costEl = row.querySelector(".stat-cost");
  const tokEl = row.querySelector(".stat-tokens");
  if (meta.cost_usd == null) {
    costEl.textContent = "cost n/a";
    costEl.title = "Token usage isn't reported for this provider";
  } else {
    costEl.textContent = fmtUsd(meta.cost_usd);
    const b = meta.cost_breakdown || {};
    costEl.title =
      `Input: ${fmtUsd(b.input ?? 0)}  ·  ` +
      `Output text: ${fmtUsd(b.output_text ?? 0)}  ·  ` +
      `Output image: ${fmtUsd(b.output_image ?? 0)}`;
  }
  const tokensParts = [
    `${fmtTokens(meta.input_tokens)} in`,
    `${fmtTokens(meta.output_image_tokens)} img`,
  ];
  if (meta.output_text_tokens) tokensParts.push(`${fmtTokens(meta.output_text_tokens)} txt`);
  tokEl.textContent = tokensParts.join(" · ");
  tokEl.title =
    `Input tokens: ${meta.input_tokens}\n` +
    `Output image tokens: ${meta.output_image_tokens}\n` +
    `Output text/thinking tokens: ${meta.output_text_tokens}\n` +
    `Model: ${meta.model}` +
    (meta.image_size ? `  (${meta.image_size}${meta.aspect_ratio ? ", " + meta.aspect_ratio : ""})` : "");
  row.hidden = false;
}

function accumulateTotals(meta) {
  if (!meta) return;
  state.totals.images += 1;
  state.totals.input += meta.input_tokens || 0;
  state.totals.outputImage += meta.output_image_tokens || 0;
  if (typeof meta.cost_usd === "number") state.totals.cost += meta.cost_usd;
  renderTotals();
}

function resetTotals() {
  state.totals = { cost: 0, images: 0, input: 0, outputImage: 0 };
  renderTotals();
}

function renderTotals() {
  const el = $("#resultsTotal");
  if (!el) return;
  if (state.totals.images === 0) {
    el.hidden = true;
    el.textContent = "";
    return;
  }
  el.hidden = false;
  el.textContent =
    `${state.totals.images} image${state.totals.images === 1 ? "" : "s"} · ` +
    `${fmtUsd(state.totals.cost)} · ` +
    `${fmtTokens(state.totals.input + state.totals.outputImage)} tokens`;
  el.title =
    `Images: ${state.totals.images}\n` +
    `Est. cost: ${fmtUsd(state.totals.cost)}\n` +
    `Input tokens: ${state.totals.input}\n` +
    `Output image tokens: ${state.totals.outputImage}`;
}

function failResult(card, message) {
  card.querySelector(".result-spinner").style.display = "none";
  const err = card.querySelector(".result-error");
  err.textContent = message;
  err.hidden = false;
}

function anglePromptFor(angle) {
  const map = {
    front: "#prompt_angle_front",
    back: "#prompt_angle_back",
    side: "#prompt_angle_side",
  };
  return $(map[angle]).value;
}

async function generateOne({ dress, angle, jobId, shotIndex }) {
  const fd = new FormData();
  fd.append("dress_name", dress.name || "dress");
  fd.append("angle", angle);
  fd.append("pose", anglePromptFor(angle));
  fd.append("garment_prompt", $("#prompt_garment").value);
  fd.append("model_prompt", $("#prompt_model").value);
  fd.append("background_prompt", $("#prompt_background").value);
  fd.append("output_prompt", $("#prompt_output").value);
  fd.append("shot_index", String(shotIndex));
  fd.append("job_id", jobId);
  fd.append("provider", state.provider);
  // Send each uploaded angle under its own field so the server knows which is which.
  ANGLES.forEach(a => {
    const file = dress.images[a];
    if (file) fd.append(`ref_${a}`, file, file.name);
  });

  const res = await fetch("/api/generate", { method: "POST", body: fd });
  if (!res.ok) {
    let msg = `HTTP ${res.status}`;
    try { const j = await res.json(); msg = j.detail || msg; } catch {}
    throw new Error(msg);
  }
  return res.json();
}

async function generateAll() {
  if (state.generating) return;

  // Build the task list: one shot per uploaded angle, per dress.
  // generateOne() reads dress.images directly and sends each angle as its own field.
  const tasks = [];
  for (const dress of state.dresses) {
    const hasAny = ANGLES.some(a => dress.images[a]);
    if (!hasAny) continue;
    ANGLES.forEach((angle, i) => {
      if (!dress.images[angle]) return;
      tasks.push({ dress, angle, shotIndex: i });
    });
  }

  if (tasks.length === 0) {
    alert("Upload at least one image (Front / Back / Side) on at least one dress.");
    return;
  }

  state.generating = true;
  state.jobId = uid() + uid();
  $("#resultsGrid").innerHTML = "";
  $("#downloadZip").disabled = true;
  resetTotals();
  openResults();
  setStatus(`Generating ${tasks.length} image(s)…`);

  // Prep the result cards up-front so users can watch them fill in.
  for (const t of tasks) {
    t.card = addResultCard({ dressName: t.dress.name, angle: t.angle, id: uid() });
  }

  let ok = 0, fail = 0, inFlight = 0;
  const queue = tasks.slice();
  const updateStatus = () => {
    const remaining = queue.length + inFlight;
    const busy = inFlight > 0 ? ` · ${inFlight} in flight` : "";
    setStatus(`${ok} done · ${fail} failed · ${remaining} left${busy}`);
  };

  async function worker() {
    while (queue.length) {
      const t = queue.shift();
      inFlight++;
      updateStatus();
      try {
        const r = await generateOne({
          dress: t.dress,
          angle: t.angle,
          jobId: state.jobId,
          shotIndex: t.shotIndex,
        });
        fillResult(t.card, r);
        ok++;
      } catch (e) {
        failResult(t.card, e.message || String(e));
        fail++;
      } finally {
        inFlight--;
        updateStatus();
      }
    }
  }

  const workerCount = Math.max(1, Math.min(state.concurrency, tasks.length));
  await Promise.all(Array.from({ length: workerCount }, () => worker()));

  state.generating = false;
  $("#downloadZip").disabled = ok === 0;
  setStatus(
    fail === 0 ? `All ${ok} image(s) ready.` : `${ok} succeeded, ${fail} failed.`,
    fail === 0 ? "ok" : "err"
  );
}

$("#generateBtn").addEventListener("click", generateAll);

$("#downloadZip").addEventListener("click", () => {
  if (!state.jobId) return;
  window.location.href = `/outputs/${state.jobId}.zip`;
});

// ---------- Refine flow ----------
const refineModal = $("#refineModal");
const refinePreview = $("#refinePreview");
const refineInput = $("#refineInput");
const refineTitle = $("#refineTitle");
const refineSub = $("#refineSub");
const refineGo = $("#refineGo");
const refinePanel = refineModal.querySelector(".modal-panel");

let refineTarget = null; // { jobId, dressName, angle, prompt, sourceCard }

function openRefine(card) {
  if (!card.classList.contains("ready")) return;
  refineTarget = {
    jobId: card.dataset.jobId,
    dressName: card.dataset.dressName,
    angle: card.dataset.angle,
    prompt: card.dataset.prompt,
    sourceCard: card,
  };
  const label = refineTarget.angle.charAt(0).toUpperCase() + refineTarget.angle.slice(1);
  refineTitle.textContent = `Refine · ${refineTarget.dressName} — ${label}`;
  refineSub.textContent = "Add extra instructions. Your original prompt is kept.";
  refinePreview.src = card.dataset.url;
  refineInput.value = "";
  refineModal.hidden = false;
  setTimeout(() => refineInput.focus(), 30);
}

function closeRefine() {
  refineModal.hidden = true;
  refineModal.classList.remove("busy");
  refinePanel.classList.remove("loading");
  refineTarget = null;
}

$("#refineClose").addEventListener("click", closeRefine);
$("#refineCancel").addEventListener("click", closeRefine);
refineModal.querySelector(".modal-backdrop").addEventListener("click", closeRefine);
document.addEventListener("keydown", e => {
  if (e.key === "Escape" && !refineModal.hidden) closeRefine();
});

// Delegated click: open modal when a ready result card is clicked.
$("#resultsGrid").addEventListener("click", e => {
  const card = e.target.closest(".result-card");
  if (!card || !card.classList.contains("ready")) return;
  // Don't hijack the download link.
  if (e.target.closest(".download")) return;
  openRefine(card);
});

refineGo.addEventListener("click", async () => {
  if (!refineTarget) return;
  const extra = refineInput.value.trim();
  if (!extra) {
    refineInput.focus();
    return;
  }

  refineModal.classList.add("busy");
  refinePanel.classList.add("loading");

  const fd = new FormData();
  fd.append("job_id", refineTarget.jobId);
  fd.append("dress_name", refineTarget.dressName);
  fd.append("angle", refineTarget.angle);
  fd.append("provider", state.provider);
  fd.append("base_prompt", refineTarget.prompt);
  fd.append("extra_instructions", extra);

  // Prep a fresh card so the user sees the new image appear in the grid.
  const newCard = addResultCard({
    dressName: refineTarget.dressName,
    angle: refineTarget.angle,
    id: uid(),
  });

  try {
    const res = await fetch("/api/refine", { method: "POST", body: fd });
    if (!res.ok) {
      let msg = `HTTP ${res.status}`;
      try { const j = await res.json(); msg = j.detail || msg; } catch {}
      throw new Error(msg);
    }
    const r = await res.json();
    fillResult(newCard, r);
    state.jobId = r.job_id;
    $("#downloadZip").disabled = false;
    setStatus(`Refined image ready.`, "ok");
    closeRefine();
  } catch (e) {
    failResult(newCard, e.message || String(e));
    setStatus("Refinement failed.", "err");
    refineModal.classList.remove("busy");
    refinePanel.classList.remove("loading");
  }
});

// ---------- Init ----------
loadDefaults().then(() => {
  if (state.dresses.length === 0) addDress();
});
