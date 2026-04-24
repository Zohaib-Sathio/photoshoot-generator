// Photoshoot Generator frontend.
// State is kept in a simple in-memory object; nothing is persisted.

const ANGLES = ["front", "back", "side"];

const state = {
  dresses: [],          // {id, name, images: {front, back, side}}
  defaults: null,       // loaded from /api/defaults
  jobId: null,
  generating: false,
  provider: "gemini",   // "gemini" | "openai"
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

$$(".seg-btn").forEach(btn => {
  btn.addEventListener("click", () => setProvider(btn.dataset.provider));
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

function fillResult(card, { url, filename }) {
  const img = card.querySelector(".result-img");
  img.src = url;
  img.hidden = false;
  card.querySelector(".result-spinner").style.display = "none";
  const a = card.querySelector(".download");
  a.href = url;
  a.setAttribute("download", filename);
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

async function generateOne({ dress, angle, jobId, references, shotIndex }) {
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
  references.forEach(f => fd.append("references", f, f.name));

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
  // Each call sends ALL uploaded angles as references for fabric fidelity.
  const tasks = [];
  for (const dress of state.dresses) {
    const refs = ANGLES.map(a => dress.images[a]).filter(Boolean);
    if (refs.length === 0) continue;
    ANGLES.forEach((angle, i) => {
      if (!dress.images[angle]) return;
      tasks.push({ dress, angle, references: refs, shotIndex: i });
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
  openResults();
  setStatus(`Generating ${tasks.length} image(s)…`);

  // Prep the result cards up-front so users can watch them fill in.
  for (const t of tasks) {
    t.card = addResultCard({ dressName: t.dress.name, angle: t.angle, id: uid() });
  }

  let ok = 0, fail = 0;
  for (const t of tasks) {
    try {
      const r = await generateOne({
        dress: t.dress,
        angle: t.angle,
        references: t.references,
        jobId: state.jobId,
        shotIndex: t.shotIndex,
      });
      fillResult(t.card, r);
      ok++;
    } catch (e) {
      failResult(t.card, e.message || String(e));
      fail++;
    }
    setStatus(`${ok} done · ${fail} failed · ${tasks.length - ok - fail} left`);
  }

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

// ---------- Init ----------
loadDefaults().then(() => {
  if (state.dresses.length === 0) addDress();
});
