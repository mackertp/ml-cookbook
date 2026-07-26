/**
 * Frontend application logic for the genomics app. The design_system folder contains 
 * a scss system that is used for custom styling of the app, written to main.css. 
 * 
 * Thank God for modern AI, it makes it so much easier to write code!
 * 
 * @author: Preston Mackert
 */

// ------------------------------------------------------------------------------------- #
// define the UI elements and their interactions
// ------------------------------------------------------------------------------------- #

(() => {
  const form = document.getElementById("analyze-form");
  const presetInput = document.getElementById("preset_id");
  const presetPicker = document.getElementById("preset-picker");
  const presetToggle = document.getElementById("preset-toggle");
  const presetValue = document.getElementById("preset-value");
  const presetMenu = document.getElementById("preset-menu");
  const presetContext = document.getElementById("preset-context");
  const customReference = document.getElementById("custom-reference");
  const sampleFile = document.getElementById("sample_file");
  const sampleText = document.getElementById("sample_text");
  const referenceFile = document.getElementById("reference_file");
  const referenceText = document.getElementById("reference_text");
  const referencePaste = document.getElementById("reference-paste");
  const referenceUpload = document.getElementById("reference-upload");
  const samplePaste = document.getElementById("sample-paste");
  const sampleUpload = document.getElementById("sample-upload");
  const sampleDemoHelp = document.getElementById("sample-demo-help");
  const demoRadio = form.querySelector('input[name="sample_mode"][value="demo"]');
  const pasteRadio = form.querySelector('input[name="sample_mode"][value="paste"]');
  const errorEl = document.getElementById("error");
  const resultsEmpty = document.getElementById("results-empty");
  const results = document.getElementById("results");
  const analyzeBtn = document.getElementById("analyze-btn");
  const clearBtn = document.getElementById("clear-btn");
  const researchPicker = document.getElementById("research-picker");
  const researchToggle = document.getElementById("research-area-toggle");
  const researchValue = document.getElementById("research-area-value");
  const researchMenu = document.getElementById("research-area-menu");
  const heroCopy = document.getElementById("hero-copy");
  const presets = window.__PRESETS__ || [];
  const researchAreas = window.__RESEARCH_AREAS__ || [];

  function showError(message) {
    errorEl.textContent = message;
    errorEl.classList.add("is-visible");
  }

  function clearError() {
    errorEl.textContent = "";
    errorEl.classList.remove("is-visible");
  }

  function clearResults() {
    results.hidden = true;
    resultsEmpty.hidden = false;
    document.getElementById("stat-row").innerHTML = "";
    document.getElementById("ref-track").innerHTML = "";
    document.getElementById("sample-track").innerHTML = "";
    document.getElementById("events").innerHTML = "";
    document.getElementById("protein-view").textContent = "";
    document.getElementById("notes").innerHTML = "";
    document.getElementById("notes-summary").textContent = "";
    document.getElementById("notes-summary").hidden = true;
    document.getElementById("indication").innerHTML = "";
    document.getElementById("indication-block").hidden = true;
    document.getElementById("treatments").innerHTML = "";
  }

  function escapeHtml(value) {
    return String(value)
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;");
  }

  function createPicker({ root, toggle, valueEl, menu, onChange }) {
    function options() {
      return Array.from(menu.querySelectorAll(".picker__option"));
    }

    function selectedOption() {
      return (
        options().find((option) => option.getAttribute("aria-selected") === "true") ||
        options()[0] ||
        null
      );
    }

    function setOpen(open) {
      root.classList.toggle("is-open", open);
      toggle.setAttribute("aria-expanded", String(open));
      menu.hidden = !open;
      if (open) {
        const selected = selectedOption();
        options().forEach((option) => option.classList.remove("is-active"));
        if (selected) {
          selected.classList.add("is-active");
          selected.focus();
        }
      }
    }

    function choose(option) {
      options().forEach((item) => {
        item.setAttribute("aria-selected", String(item === option));
        item.classList.remove("is-active");
      });
      valueEl.textContent = option.textContent.trim();
      setOpen(false);
      toggle.focus();
      onChange(option.dataset.value, option);
    }

    function moveFocus(current, delta) {
      const items = options();
      const index = items.indexOf(current);
      const next = items[index + delta];
      if (next) {
        items.forEach((option) => option.classList.remove("is-active"));
        next.classList.add("is-active");
        next.focus();
      }
    }

    function bindOption(option) {
      option.addEventListener("click", () => choose(option));
      option.addEventListener("keydown", (event) => {
        if (event.key === "Enter" || event.key === " ") {
          event.preventDefault();
          choose(option);
        } else if (event.key === "ArrowDown") {
          event.preventDefault();
          moveFocus(option, 1);
        } else if (event.key === "ArrowUp") {
          event.preventDefault();
          moveFocus(option, -1);
        } else if (event.key === "Escape") {
          setOpen(false);
          toggle.focus();
        }
      });
    }

    toggle.addEventListener("click", () => setOpen(menu.hidden));
    toggle.addEventListener("keydown", (event) => {
      if (event.key === "ArrowDown" || event.key === "Enter" || event.key === " ") {
        event.preventDefault();
        setOpen(true);
      }
    });

    document.addEventListener("click", (event) => {
      if (!menu.hidden && !root.contains(event.target)) {
        setOpen(false);
      }
    });

    return {
      options,
      selectedOption,
      setOpen,
      choose,
      bindOption,
      rebuild(items, selectedValue) {
        menu.innerHTML = "";
        items.forEach((item) => {
          const option = document.createElement("li");
          option.className = "picker__option";
          option.setAttribute("role", "option");
          option.dataset.value = item.value;
          option.tabIndex = -1;
          option.textContent = item.label;
          option.setAttribute(
            "aria-selected",
            String(item.value === selectedValue)
          );
          bindOption(option);
          menu.appendChild(option);
        });
        const selected = selectedOption();
        if (selected) {
          valueEl.textContent = selected.textContent.trim();
          onChange(selected.dataset.value, selected);
        }
      },
    };
  }

  function selectedResearchAreaId() {
    const selected = researchMenu.querySelector('.picker__option[aria-selected="true"]');
    return selected ? selected.dataset.value : "cancer";
  }

  function presetsForArea(areaId) {
    return presets.filter((preset) => {
      if (!preset.research_areas) {
        return true;
      }
      return preset.research_areas.includes(areaId);
    });
  }

  function preferredPresetId(areaId, available) {
    const current = presetInput.value;
    if (available.some((preset) => preset.id === current)) {
      return current;
    }
    if (areaId === "cancer") {
      const egfr = available.find((preset) => preset.id === "egfr_exon19");
      if (egfr) {
        return egfr.id;
      }
    }
    const teaching = available.find((preset) => preset.id);
    return teaching ? teaching.id : "";
  }

  function syncTeachingSampleAvailability() {
    const hasTeachingSample = Boolean(presetInput.value);
    demoRadio.disabled = !hasTeachingSample;
    demoRadio.closest(".radio").classList.toggle("is-disabled", !hasTeachingSample);

    if (!hasTeachingSample && demoRadio.checked) {
      pasteRadio.checked = true;
    }

    if (hasTeachingSample) {
      const preset = presets.find((p) => p.id === presetInput.value);
      const label = preset ? preset.label : "the selected reference";
      sampleDemoHelp.textContent = `Uses the paired teaching sample from data/ for ${label}.`;
    } else {
      sampleDemoHelp.textContent =
        "No teaching sample for this research area yet — paste or upload your own sample sequence.";
    }
  }

  function syncPresetUi(presetId) {
    const id = presetId ?? presetInput.value;
    const preset = presets.find((p) => p.id === id) || presets.find((p) => !p.id);
    presetInput.value = id;
    customReference.hidden = Boolean(id);
    presetContext.innerHTML = preset ? preset.context : "";
    syncTeachingSampleAvailability();
    syncSampleMode();
  }

  function selectedMode(name) {
    const checked = form.querySelector(`input[name="${name}"]:checked`);
    return checked ? checked.value : "demo";
  }

  function syncReferenceMode() {
    const mode = selectedMode("reference_mode");
    const paste = mode === "paste";
    referencePaste.hidden = !paste;
    referenceUpload.hidden = paste;
    if (paste) {
      referenceFile.value = "";
    } else {
      referenceText.value = "";
    }
  }

  function syncSampleMode() {
    const mode = selectedMode("sample_mode");
    const hasTeachingSample = Boolean(presetInput.value);
    sampleDemoHelp.hidden = hasTeachingSample ? mode !== "demo" : false;
    samplePaste.hidden = mode !== "paste";
    sampleUpload.hidden = mode !== "upload";

    if (mode === "demo") {
      sampleFile.value = "";
      sampleText.value = "";
    } else if (mode === "paste") {
      sampleFile.value = "";
    } else {
      sampleText.value = "";
    }
  }

  function badge(label, kind) {
    return `<span class="badge badge--${kind}">${label}</span>`;
  }

  function renderSpans(container, spans) {
    container.innerHTML = spans
      .map((span) => {
        const kindClass =
          span.kind === "match" ? "" : ` sequence-view__base--${span.kind}`;
        return `<span class="sequence-view__base${kindClass}">${escapeHtml(span.text)}</span>`;
      })
      .join("");
  }

  function renderResults(data) {
    resultsEmpty.hidden = true;
    results.hidden = false;

    const delta = data.length_delta;
    const frameLabel = data.in_frame_length_change
      ? badge("in-frame Δ", "inframe")
      : badge("frameshift Δ", "frameshift");

    document.getElementById("stat-row").innerHTML = [
      badge(`${data.reference.length} bp ref`, "neutral"),
      badge(`${data.sample.length} bp sample`, "neutral"),
      badge(`${delta >= 0 ? "+" : ""}${delta} bp`, delta < 0 ? "deletion" : delta > 0 ? "insertion" : "neutral"),
      frameLabel,
      badge(`${data.events.length} event(s)`, "neutral"),
    ].join("");

    renderSpans(document.getElementById("ref-track"), data.spans.reference);
    renderSpans(document.getElementById("sample-track"), data.spans.sample);

    const eventsEl = document.getElementById("events");
    if (!data.events.length) {
      eventsEl.innerHTML = `<p class="empty-state">No indel or mismatch events detected.</p>`;
    } else {
      eventsEl.innerHTML = data.events
        .map((event) => {
          if (event.type === "deletion") {
            return `<article class="event-chip">${badge("deletion", "deletion")}
              <div><strong>${event.length} bp</strong> removed at ref ${event.ref_start}</div>
              <code>${escapeHtml(event.deleted_bases)}</code></article>`;
          }
          if (event.type === "insertion") {
            return `<article class="event-chip">${badge("insertion", "insertion")}
              <div><strong>${event.length} bp</strong> inserted at ref ${event.ref_start}</div>
              <code>${escapeHtml(event.inserted_bases)}</code></article>`;
          }
          return `<article class="event-chip">${badge("mismatch", "mismatch")}
            <div>ref ${event.ref_pos}: <code>${escapeHtml(event.ref_base)} → ${escapeHtml(event.alt_base)}</code></div></article>`;
        })
        .join("");
    }

    const align = data.protein_alignment;
    document.getElementById("protein-view").textContent = [
      `ref  ${align.reference}`,
      `     ${align.marks}`,
      `alt  ${align.alternate}`,
      "",
      `Reference protein: ${data.reference.protein}`,
      `Sample protein:    ${data.sample.protein}`,
    ].join("\n");

    const indicationBlock = document.getElementById("indication-block");
    const indicationEl = document.getElementById("indication");
    if (data.indication) {
      indicationBlock.hidden = false;
      const slug = data.indication.slug || "";
      indicationEl.innerHTML = `<article class="indication-card">
        <div class="indication-card__row">
          <span class="indication-card__slug">${escapeHtml(slug)}</span>
          <span class="badge badge--neutral">${escapeHtml(data.indication.category)}</span>
        </div>
        <h3 class="indication-card__title">${escapeHtml(data.indication.label)}</h3>
        <p class="indication-card__detail">${escapeHtml(data.indication.detail)}</p>
      </article>`;
    } else {
      indicationBlock.hidden = true;
      indicationEl.innerHTML = "";
    }

    document.getElementById("notes").innerHTML = data.notes
      .map(
        (note) => `<article class="anomaly anomaly--${escapeHtml(note.severity)}">
          <h3 class="anomaly__title">${escapeHtml(note.title)}</h3>
          <p class="anomaly__detail">${escapeHtml(note.detail)}</p>
        </article>`
      )
      .join("");

    const notesSummary = document.getElementById("notes-summary");
    if (data.notes_summary) {
      notesSummary.hidden = false;
      notesSummary.innerHTML = `<strong>Analysis:</strong> ${escapeHtml(data.notes_summary)}`;
    } else {
      notesSummary.hidden = true;
      notesSummary.textContent = "";
    }

    const treatmentsEl = document.getElementById("treatments");
    const treatments = data.treatments || [];
    if (!treatments.length) {
      treatmentsEl.innerHTML = `<p class="empty-state">No matching treatment in this teaching catalog for the detected alteration (some findings are counseling-only).</p>`;
    } else {
      treatmentsEl.innerHTML = treatments
        .map((drug) => {
          const brands = (drug.brands || [])
            .map(
              (brand) =>
                `<a class="treatment-card__brand" href="${escapeHtml(brand.url)}" target="_blank" rel="noopener noreferrer">${escapeHtml(brand.name)}</a>`
            )
            .join("");
          return `<article class="treatment-card">
            <a class="treatment-card__name" href="${escapeHtml(drug.drugbank_url)}" target="_blank" rel="noopener noreferrer">${escapeHtml(drug.name)}</a>
            <p class="treatment-card__class">${escapeHtml(drug.drug_class)}</p>
            <p class="treatment-card__biomarker">${escapeHtml(drug.biomarker)}</p>
            ${brands ? `<div class="treatment-card__brands"><span class="treatment-card__brands-label">Brands</span>${brands}</div>` : ""}
            ${drug.evidence ? `<p class="treatment-card__evidence">${escapeHtml(drug.evidence)}</p>` : ""}
          </article>`;
        })
        .join("");
    }
  }

  const researchAreaPicker = createPicker({
    root: researchPicker,
    toggle: researchToggle,
    valueEl: researchValue,
    menu: researchMenu,
    onChange(areaId) {
      const area = researchAreas.find((item) => item.id === areaId);
      if (area) {
        heroCopy.innerHTML = area.description;
      }
      refreshPresetOptions();
    },
  });

  const referencePicker = createPicker({
    root: presetPicker,
    toggle: presetToggle,
    valueEl: presetValue,
    menu: presetMenu,
    onChange(presetId) {
      syncPresetUi(presetId);
    },
  });

  function refreshPresetOptions() {
    const areaId = selectedResearchAreaId();
    const available = presetsForArea(areaId);
    const selectedId = preferredPresetId(areaId, available);
    referencePicker.rebuild(
      available.map((preset) => ({ value: preset.id, label: preset.label })),
      selectedId
    );
  }

  researchMenu.querySelectorAll(".picker__option").forEach((option) => {
    researchAreaPicker.bindOption(option);
  });

  document.querySelectorAll("[data-upload]").forEach((zone) => {
    zone.addEventListener("dragover", (event) => {
      event.preventDefault();
      zone.classList.add("is-dragover");
    });
    zone.addEventListener("dragleave", () => zone.classList.remove("is-dragover"));
    zone.addEventListener("drop", (event) => {
      event.preventDefault();
      zone.classList.remove("is-dragover");
      const input = zone.querySelector('input[type="file"]');
      if (event.dataTransfer.files.length) {
        input.files = event.dataTransfer.files;
        input.dispatchEvent(new Event("change"));
      }
    });
  });

  form.querySelectorAll('input[name="reference_mode"]').forEach((input) => {
    input.addEventListener("change", syncReferenceMode);
  });
  form.querySelectorAll('input[name="sample_mode"]').forEach((input) => {
    input.addEventListener("change", syncSampleMode);
  });

  clearBtn.addEventListener("click", () => {
    sampleFile.value = "";
    sampleText.value = "";
    if (!demoRadio.disabled) {
      demoRadio.checked = true;
    } else {
      pasteRadio.checked = true;
    }
    syncSampleMode();
    clearError();
    clearResults();
  });

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    clearError();
    analyzeBtn.disabled = true;
    analyzeBtn.textContent = "Analyzing…";

    const sampleMode = selectedMode("sample_mode");
    const body = new FormData(form);
    body.set("use_demo_sample", sampleMode === "demo" ? "true" : "false");

    if (selectedMode("reference_mode") === "paste") {
      body.delete("reference_file");
    } else {
      body.delete("reference_text");
    }
    if (sampleMode !== "upload") {
      body.delete("sample_file");
    }
    if (sampleMode !== "paste") {
      body.delete("sample_text");
    }

    try {
      const response = await fetch("/api/analyze", { method: "POST", body });
      const payload = await response.json();
      if (!response.ok) {
        throw new Error(payload.error || "Analysis failed");
      }
      renderResults(payload);
    } catch (err) {
      showError(err.message || String(err));
    } finally {
      analyzeBtn.disabled = false;
      analyzeBtn.textContent = "Compare & translate";
    }
  });

  const initialArea = researchAreas.find((item) => item.id === "cancer") || researchAreas[0];
  if (initialArea) {
    heroCopy.innerHTML = initialArea.description;
  }
  refreshPresetOptions();
  syncReferenceMode();
  syncSampleMode();
})();
