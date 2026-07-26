/**
 * Supporting script for the sequencing animation.
 * 
 * @author: Preston Mackert
 */

// ------------------------------------------------------------------------------------- #
// define the sequencing steps and their details
// ------------------------------------------------------------------------------------- #

(() => {
  const STEPS = [
    {
      title: "Collect a sample",
      detail:
        "Sequencing usually starts with blood, saliva, or a tissue biopsy — cells that carry the DNA you want to read.",
      dwellMs: 9000,
    },
    {
      title: "Extract the DNA",
      detail:
        "Lab chemistry breaks open the cells and pulls out the long DNA molecules that hold the genetic instructions.",
      dwellMs: 14000,
    },
    {
      title: "Chop DNA into readable pieces",
      detail:
        "Those long strands are cut into shorter fragments and prepared so a sequencing machine can process millions of them in parallel.",
      dwellMs: 16000,
    },
    {
      title: "Read each letter",
      detail:
        "The machine detects chemical signals for adenine (A), thymine (T), guanine (G), and cytosine (C) — the four DNA letters.",
      dwellMs: 10000,
    },
    {
      title: "Turn signals into the letters in this app",
      detail:
        "Software converts those signals into a text string like ATGC…. That sequence is what you paste, upload, or load as a teaching sample here.",
      dwellMs: 10000,
    },
  ];

  // ------------------------------------------------------------------------------------- #
  // demo sequence used in the animation
  // ------------------------------------------------------------------------------------- #

  const DEMO_SEQ = "ATGACTGAATATAAACTTGTGGTAGTTGGAGCTGGTGGC";

  // ------------------------------------------------------------------------------------- #
  // UI elements and interactions
  // ------------------------------------------------------------------------------------- #

  const stage = document.getElementById("sequencing-stage");
  const caption = document.getElementById("sequencing-caption");
  const detail = document.getElementById("sequencing-detail");
  const stepIndex = document.getElementById("sequencing-step-index");
  const dots = Array.from(document.querySelectorAll(".sequencing__dot"));
  const prevBtn = document.getElementById("seq-prev");
  const nextBtn = document.getElementById("seq-next");
  const output = document.getElementById("seq-output-text");

  let step = 0;
  let autoTimer = null;
  let typeTimer = null;

  // ------------------------------------------------------------------------------------- #
  // animation functions
  // ------------------------------------------------------------------------------------- #

  function clearTimers() {
    if (autoTimer) {
      clearTimeout(autoTimer);
      autoTimer = null;
    }
    if (typeTimer) {
      clearInterval(typeTimer);
      typeTimer = null;
    }
  }

  function typeSequence() {
    output.textContent = "";
    let i = 0;
    typeTimer = setInterval(() => {
      output.textContent = DEMO_SEQ.slice(0, i + 1);
      i += 1;
      if (i >= DEMO_SEQ.length) {
        clearInterval(typeTimer);
        typeTimer = null;
      }
    }, 45);
  }

  function render() {
    stage.dataset.step = String(step);
    const current = STEPS[step];
    caption.textContent = current.title;
    detail.textContent = current.detail;
    stepIndex.textContent = `Step ${step + 1} of ${STEPS.length}`;

    dots.forEach((dot, index) => {
      const active = index === step;
      dot.classList.toggle("is-active", active);
      dot.setAttribute("aria-selected", String(active));
    });

    prevBtn.disabled = step === 0;
    nextBtn.textContent = step === STEPS.length - 1 ? "Done" : "Next";

    if (step === 4) {
      typeSequence();
    } else {
      output.textContent = "";
    }
  }

  function goTo(next, { autoplay = true } = {}) {
    clearTimers();
    step = Math.max(0, Math.min(STEPS.length - 1, next));
    render();
    if (autoplay && step < STEPS.length - 1) {
      autoTimer = setTimeout(() => goTo(step + 1), STEPS[step].dwellMs);
    }
  }

  prevBtn.addEventListener("click", () => goTo(step - 1));
  nextBtn.addEventListener("click", () => {
    if (step >= STEPS.length - 1) {
      goTo(0);
      return;
    }
    goTo(step + 1);
  });
  dots.forEach((dot) => {
    dot.addEventListener("click", () => goTo(Number(dot.dataset.step)));
  });

  goTo(0);
})();
