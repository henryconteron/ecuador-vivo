(() => {

  const i18n = window.atlasI18n;
  const choices = [...document.querySelectorAll("[data-story-choice]")];
  const panels = [...document.querySelectorAll("[data-story-panel]")];
  const reducedMotion = () => window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const scrollTo = (element) => element?.scrollIntoView({ behavior: reducedMotion() ? "auto" : "smooth", block: "start" });

  function storyFromLocation() {
    const hash = window.location.hash.slice(1);
    const targetPanel = document.getElementById(hash)?.closest("[data-story-panel]");
    const requested = targetPanel?.dataset.storyPanel ?? new URLSearchParams(window.location.search).get("story");
    return panels.some((panel) => panel.dataset.storyPanel === requested) ? requested : "earth";
  }

  function selectStory(story, { navigate = false, reveal = true } = {}) {
    choices.forEach((choice) => {
      const active = choice.dataset.storyChoice === story;
      choice.setAttribute("aria-selected", String(active));
      choice.tabIndex = active ? 0 : -1;
    });
    panels.forEach((panel) => { panel.hidden = panel.dataset.storyPanel !== story; });
    if (navigate) {
      const url = new URL(window.location.href);
      url.searchParams.set("story", story);
      url.hash = "story-" + story;
      window.history.pushState({ ...window.history.state, story }, "", url);
      const panel = panels.find((item) => item.dataset.storyPanel === story);
      if (reveal) {
        panel?.focus({ preventScroll: true });
        scrollTo(panel);
      }
    }
  }

  choices.forEach((choice, index) => {
    choice.addEventListener("click", (event) => {
      event.preventDefault();
      selectStory(choice.dataset.storyChoice, { navigate: true });
    });
    choice.addEventListener("keydown", (event) => {
      const keys = ["ArrowLeft", "ArrowRight", "Home", "End"];
      if (!keys.includes(event.key)) return;
      event.preventDefault();
      const nextIndex = event.key === "Home" ? 0 : event.key === "End" ? choices.length - 1
        : (index + (event.key === "ArrowRight" ? 1 : -1) + choices.length) % choices.length;
      choices[nextIndex].focus();
      selectStory(choices[nextIndex].dataset.storyChoice, { navigate: true, reveal: false });
      choices[nextIndex].focus({ preventScroll: true });
    });
  });
  if (panels.length) {
    selectStory(storyFromLocation());
    window.addEventListener("popstate", () => {
      selectStory(storyFromLocation());
      const target = document.getElementById(window.location.hash.slice(1));
      if (target) scrollTo(target);
    });
    window.addEventListener("hashchange", () => selectStory(storyFromLocation()));
  }

  const checks = [...document.querySelectorAll("[data-learning-check]")];
  function renderCheck(check) {
    const selected = check.dataset.selectedAnswer;
    const feedback = check.querySelector("[data-check-feedback]");
    if (!selected) return;
    const correct = selected === check.dataset.correctAnswer;
    feedback.hidden = false;
    feedback.dataset.state = correct ? "correct" : "incorrect";
    check.querySelector("[data-check-heading]").textContent = i18n.t(correct ? "check.correct" : "check.retry");
    check.querySelectorAll("[data-check-choice]").forEach((button) => {
      button.setAttribute("aria-pressed", String(button.dataset.checkChoice === selected));
    });
  }
  checks.forEach((check) => {
    check.querySelectorAll("[data-check-choice]").forEach((button) => {
      button.addEventListener("click", () => {
        check.dataset.selectedAnswer = button.dataset.checkChoice;
        renderCheck(check);
        check.querySelector("[data-check-feedback]").focus({ preventScroll: true });
      });
    });
  });

  function updateStoryLinks() {
    document.querySelectorAll("[data-story-map], [data-story-choice]").forEach((link) => {
      const url = new URL(link.href);
      url.searchParams.set("lang", i18n.language);
      link.href = url.href;
    });
    checks.forEach(renderCheck);
  }
  updateStoryLinks();
  window.addEventListener("atlas:languagechange", updateStoryLinks);

  // Keep original scientific images intact; show an enlarged, attributed copy in a dialog.
  const viewer = document.createElement("dialog");
  viewer.className = "figure-viewer";
  const close = document.createElement("button");
  close.type = "button";
  const enlarged = document.createElement("img");
  const caption = document.createElement("div");
  caption.className = "figure-viewer-caption";
  let activeFigure = null;
  viewer.append(close, enlarged, caption);
  document.body.append(viewer);
  const updateViewerLabels = () => {
    viewer.setAttribute("aria-label", i18n.t("figure.dialog"));
    close.textContent = i18n.t("figure.close") + " ×";
    document.querySelectorAll("[data-enlarge-figure]").forEach((button) => {
      button.textContent = i18n.t("figure.expand") + " ↗";
    });
  };
  close.addEventListener("click", () => viewer.close());
  viewer.addEventListener("click", (event) => { if (event.target === viewer) viewer.close(); });
  caption.addEventListener("click", (event) => { if (event.target.closest("a")) viewer.close(); });
  document.querySelectorAll("[data-story-panel] figure").forEach((figure) => {
    const image = figure.querySelector("img");
    if (!image) return;
    const expand = document.createElement("button");
    expand.type = "button";
    expand.className = "figure-expand";
    expand.dataset.enlargeFigure = "";
    expand.addEventListener("click", () => {
      activeFigure = figure;
      enlarged.src = image.src;
      enlarged.alt = image.alt;
      const source = figure.querySelector("figcaption") ?? figure.closest(".clue-card")?.querySelector("small");
      caption.replaceChildren();
      if (source) caption.append(source.cloneNode(true));
      viewer.showModal();
    });
    figure.append(expand);
  });
  updateViewerLabels();
  window.addEventListener("atlas:languagechange", () => {
    updateViewerLabels();
    if (viewer.open && activeFigure) {
      enlarged.alt = activeFigure.querySelector("img").alt;
      const source = activeFigure.querySelector("figcaption") ?? activeFigure.closest(".clue-card")?.querySelector("small");
      caption.replaceChildren();
      if (source) caption.append(source.cloneNode(true));
    }
  });

  const storyNav = document.querySelector("[data-story-nav]");

  if (storyNav) {
    const links = [...storyNav.querySelectorAll("[data-story-link]")];
    const track = storyNav.querySelector(".story-nav-track");
    const sections = links
      .map((link) => document.querySelector(`[data-story-section="${link.dataset.storyLink}"]`))
      .filter(Boolean);
    const progress = storyNav.querySelector("[data-story-progress]");
    let frameRequested = false;

    const setActiveSection = (sectionId) => {
      links.forEach((link) => {
        const isActive = link.dataset.storyLink === sectionId;
        link.classList.toggle("is-active", isActive);
        if (isActive) {
          link.setAttribute("aria-current", "location");
          // Scroll only the chapter strip, never the page while the reader scrolls.
          if (track) track.scrollTo({ left: link.offsetLeft - (track.clientWidth - link.clientWidth) / 2,
            behavior: reducedMotion() ? "auto" : "smooth" });
        } else {
          link.removeAttribute("aria-current");
        }
      });
    };

    const updateProgress = () => {
      frameRequested = false;
      if (!progress || sections.length === 0 || storyNav.closest("[data-story-panel]")?.hidden) return;
      const start = sections[0].offsetTop;
      const end = sections.at(-1).offsetTop + sections.at(-1).offsetHeight - window.innerHeight;
      const ratio = end <= start ? 1 : Math.min(1, Math.max(0, (window.scrollY - start) / (end - start)));
      progress.style.width = `${ratio * 100}%`;
    };

    const requestProgressUpdate = () => {
      if (frameRequested) return;
      frameRequested = true;
      window.requestAnimationFrame(updateProgress);
    };

    if ("IntersectionObserver" in window) {
      const observer = new IntersectionObserver(
        (entries) => {
          const visible = entries
            .filter((entry) => entry.isIntersecting)
            .sort((a, b) => b.intersectionRatio - a.intersectionRatio)[0];
          if (visible) setActiveSection(visible.target.dataset.storySection);
        },
        { rootMargin: "-30% 0px -55%", threshold: [0, 0.1, 0.35] },
      );
      sections.forEach((section) => observer.observe(section));
    } else if (sections[0]) {
      setActiveSection(sections[0].dataset.storySection);
    }

    links.forEach((link) => {
      link.addEventListener("click", () => setActiveSection(link.dataset.storyLink));
    });
    window.addEventListener("hashchange", () => {
      const sectionId = window.location.hash.slice(1);
      if (links.some((link) => link.dataset.storyLink === sectionId)) {
        setActiveSection(sectionId);
      }
    });
    const initialSectionId = window.location.hash.slice(1);
    if (links.some((link) => link.dataset.storyLink === initialSectionId)) {
      setActiveSection(initialSectionId);
    }

    window.addEventListener("scroll", requestProgressUpdate, { passive: true });
    window.addEventListener("resize", requestProgressUpdate);
    requestProgressUpdate();
  }

  const lab = document.querySelector("[data-field-lab]");
  if (!lab || !window.atlasI18n) return;

  const scenarios = [
    { id: "normal", answer: "normal", image: "papers/tarbuck-normal-fault.webp", source: "figure.sourceTarbuckNormal", ref: "ref-tarbuck" },
    { id: "reverse", answer: "unknown", image: "papers/pallatanga-riobamba-scarp.webp", source: "figure.sourceBaize2015C", ref: "ref-baize-2015" },
    { id: "strike", answer: "strike", image: "papers/pallatanga-yacupamba-offset.webp", source: "figure.sourceBaize2015B", ref: "ref-baize-2015" },
  ];
  const answerButtons = [...lab.querySelectorAll("[data-lab-answer]")];

  const elements = {
    answers: lab.querySelector("[data-lab-answers]"),
    caseNumber: lab.querySelector("[data-lab-case]"),
    clue: lab.querySelector("[data-lab-clue]"),
    feedback: lab.querySelector("[data-lab-feedback]"),
    image: lab.querySelector("[data-lab-image]"),
    source: lab.querySelector("[data-lab-source]"),
    kicker: lab.querySelector("[data-lab-kicker]"),
    next: lab.querySelector("[data-lab-next]"),
    nextLabel: lab.querySelector("[data-lab-next] span"),
    progress: lab.querySelector("[data-lab-progress]"),
    progressBar: lab.querySelector("[data-lab-progress-bar]"),
    question: lab.querySelector("[data-lab-question]"),
    restart: lab.querySelector("[data-lab-restart]"),
  };

  let currentIndex = 0;
  let score = 0;
  let selectedAnswer = null;
  let showingResult = false;

  const t = (key) => window.atlasI18n.t(key);
  const interpolate = (value, replacements) =>
    Object.entries(replacements).reduce(
      (result, [key, replacement]) => result.replace(`{${key}}`, replacement),
      value,
    );

  function scenarioKey(suffix) {
    return `lab.scenario.${scenarios[currentIndex].id}.${suffix}`;
  }

  function renderFeedback() {
    if (!selectedAnswer) {
      elements.feedback.hidden = true;
      elements.feedback.textContent = "";
      return;
    }

    const isCorrect = selectedAnswer === scenarios[currentIndex].answer;
    elements.feedback.hidden = false;
    elements.feedback.dataset.state = isCorrect ? "correct" : "incorrect";
    elements.feedback.innerHTML = "";

    const heading = document.createElement("strong");
    heading.textContent = t(isCorrect ? "lab.correct" : "lab.incorrect");
    const explanation = document.createElement("span");
    explanation.textContent = t(scenarioKey("explanation"));
    elements.feedback.append(heading, explanation);
  }

  function renderScenario() {
    const scenario = scenarios[currentIndex];
    const position = currentIndex + 1;
    elements.caseNumber.textContent = String(position).padStart(2, "0");
    elements.progress.textContent = interpolate(t("lab.progress"), {
      current: position,
      total: scenarios.length,
    });
    elements.progressBar.value = position;
    elements.progressBar.max = scenarios.length;
    elements.progressBar.textContent = elements.progress.textContent;
    elements.kicker.textContent = t(scenarioKey("kicker"));
    elements.question.textContent = t(scenarioKey("question"));
    elements.clue.textContent = t(scenarioKey("clue"));
    elements.image.alt = t(scenarioKey("imageAlt"));
    elements.image.src = "assets/images/education/" + scenario.image;
    elements.source.textContent = t(scenario.source);
    elements.source.href = "#" + scenario.ref;
    elements.nextLabel.textContent = t(
      currentIndex === scenarios.length - 1 ? "lab.results" : "lab.next",
    );

    answerButtons.forEach((button) => {
      const answer = button.dataset.labAnswer;
      const isSelected = answer === selectedAnswer;
      button.disabled = Boolean(selectedAnswer);
      button.classList.toggle("is-selected", isSelected);
      button.classList.toggle(
        "is-correct",
        Boolean(selectedAnswer) && answer === scenario.answer,
      );
      button.classList.toggle(
        "is-incorrect",
        isSelected && answer !== scenario.answer,
      );
    });

    renderFeedback();
  }

  function renderResult() {
    showingResult = true;
    elements.answers.hidden = true;
    elements.next.hidden = true;
    elements.restart.hidden = false;
    elements.kicker.textContent = t("lab.resultKicker");
    elements.question.textContent = t("lab.resultTitle");
    elements.clue.textContent = interpolate(t("lab.resultCopy"), {
      score,
      total: scenarios.length,
    });
    elements.feedback.hidden = false;
    elements.feedback.dataset.state = score === scenarios.length ? "correct" : "neutral";
    elements.feedback.innerHTML = "";
    const message = document.createElement("strong");
    message.textContent = t(
      score === scenarios.length ? "lab.resultPerfect" : "lab.resultEncourage",
    );
    elements.feedback.append(message);
  }

  function answer(selected) {
    if (selectedAnswer || showingResult) return;
    selectedAnswer = selected;
    if (selected === scenarios[currentIndex].answer) score += 1;
    elements.next.hidden = false;
    renderScenario();
    elements.feedback.focus({ preventScroll: true });
  }

  function next() {
    if (!selectedAnswer) return;
    if (currentIndex === scenarios.length - 1) {
      renderResult();
      elements.restart.focus();
      return;
    }
    currentIndex += 1;
    selectedAnswer = null;
    elements.next.hidden = true;
    renderScenario();
    elements.question.focus({ preventScroll: true });
  }

  function restart() {
    currentIndex = 0;
    score = 0;
    selectedAnswer = null;
    showingResult = false;
    elements.answers.hidden = false;
    elements.next.hidden = true;
    elements.restart.hidden = true;
    renderScenario();
    answerButtons[0].focus();
  }

  answerButtons.forEach((button) => {
    button.addEventListener("click", () => answer(button.dataset.labAnswer));
  });
  elements.next.addEventListener("click", next);
  elements.restart.addEventListener("click", restart);
  window.addEventListener("atlas:languagechange", () => {
    if (showingResult) renderResult();
    else renderScenario();
  });

  elements.question.tabIndex = -1;
  elements.feedback.tabIndex = -1;
  renderScenario();
})();
