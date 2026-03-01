const form = document.getElementById("generator-form");
const numInput = document.getElementById("num-images");
const numRange = document.getElementById("num-range");
const numDisplay = document.getElementById("num-display");
const statusText = document.getElementById("status-text");
const statusPill = document.getElementById("status-pill");
const jobIdEl = document.getElementById("job-id");
const blinkLine = document.getElementById("blink-line");
const blinkCount = document.getElementById("image-count-blink");
const grid = document.getElementById("image-grid");
const errorText = document.getElementById("error-text");
const progressBar = document.getElementById("progress-bar");
const generateBtn = document.getElementById("generate-btn");

let pollTimer = null;
let activeJobId = null;
let activeCount = parseInt(numInput.value, 10);

const STATUS_COPY = {
  idle: "Choose a number and press generate.",
  pending: "Queued. Waiting for a worker to start.",
  processing: "Rendering your image batch.",
  completed: "Done. Images are ready.",
  failed: "Generation failed. Try again.",
  submitting: "Submitting job...",
};

function syncCount(value) {
  const count = Math.min(100, Math.max(1, Number(value) || 1));
  activeCount = count;
  numInput.value = count;
  numRange.value = count;
  numDisplay.textContent = count;
  blinkCount.textContent = count;
}

function setStatus(state) {
  statusText.textContent = STATUS_COPY[state] || STATUS_COPY.idle;
  statusPill.textContent =
    state === "idle"
      ? "Ready"
      : `${state.charAt(0).toUpperCase()}${state.slice(1)}`;
  statusPill.style.background =
    state === "failed" ? "rgba(239, 68, 68, 0.16)" : "rgba(61, 182, 255, 0.16)";
  statusPill.style.color = state === "failed" ? "#b91c1c" : "#13619a";

  if (state === "pending" || state === "processing" || state === "submitting") {
    blinkLine.hidden = false;
    progressBar.classList.add("indeterminate");
  } else {
    blinkLine.hidden = true;
    progressBar.classList.remove("indeterminate");
  }

  if (state === "completed") {
    progressBar.style.width = "100%";
    progressBar.style.background = "linear-gradient(90deg, #22c55e, #86efac)";
  } else if (state === "failed") {
    progressBar.style.width = "100%";
    progressBar.style.background = "linear-gradient(90deg, #ef4444, #fca5a5)";
  } else {
    progressBar.style.width = "30%";
    progressBar.style.background = "linear-gradient(90deg, #3db6ff, #ffd84f)";
  }
}

function clearError() {
  errorText.hidden = true;
  errorText.textContent = "";
}

function showError(message) {
  errorText.textContent = message;
  errorText.hidden = false;
}

function renderPlaceholders(count) {
  grid.innerHTML = "";
  for (let i = 0; i < count; i += 1) {
    const card = document.createElement("div");
    card.className = "image-card placeholder";
    const label = document.createElement("div");
    label.className = "placeholder-label";
    label.textContent = `Rendering ${i + 1}`;
    card.appendChild(label);
    grid.appendChild(card);
  }
}

function renderImages(urls) {
  grid.innerHTML = "";
  if (!urls.length) {
    const card = document.createElement("div");
    card.className = "image-card error";
    card.textContent = "No images returned.";
    grid.appendChild(card);
    return;
  }

  urls.forEach((url, index) => {
    const card = document.createElement("div");
    if (!url) {
      card.className = "image-card error";
      card.textContent = `Image ${index + 1} unavailable`;
      grid.appendChild(card);
      return;
    }

    card.className = "image-card";
    const img = document.createElement("img");
    img.alt = `Generated image ${index + 1}`;
    img.loading = "lazy";
    img.src = url;
    card.appendChild(img);
    grid.appendChild(card);
  });
}

async function pollStatus() {
  if (!activeJobId) return;

  try {
    const response = await fetch(`/job/${activeJobId}/details`);
    if (!response.ok) {
      throw new Error(`Status request failed (${response.status})`);
    }
    const data = await response.json();
    const status = data.status;

    if (status === "completed") {
      clearInterval(pollTimer);
      pollTimer = null;
      setStatus("completed");
      renderImages(data.output_paths || []);
      generateBtn.disabled = false;
      return;
    }

    if (status === "failed") {
      clearInterval(pollTimer);
      pollTimer = null;
      setStatus("failed");
      showError("The job failed. Please try again.");
      generateBtn.disabled = false;
      return;
    }

    setStatus(status);
  } catch (error) {
    clearInterval(pollTimer);
    pollTimer = null;
    setStatus("failed");
    showError(error.message);
    generateBtn.disabled = false;
  }
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  clearError();
  if (pollTimer) {
    clearInterval(pollTimer);
  }

  syncCount(numInput.value);
  renderPlaceholders(activeCount);
  setStatus("submitting");
  generateBtn.disabled = true;

  try {
    const response = await fetch("/generate/image", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ num_images: activeCount }),
    });

    if (!response.ok) {
      throw new Error(`Failed to start job (${response.status})`);
    }

    const data = await response.json();
    activeJobId = data.job_id;
    jobIdEl.textContent = `Job ${activeJobId.slice(0, 8)}…`;
    setStatus(data.status);

    pollTimer = setInterval(pollStatus, 2000);
    await pollStatus();
  } catch (error) {
    setStatus("failed");
    showError(error.message);
    generateBtn.disabled = false;
  }
});

numInput.addEventListener("input", (event) => {
  syncCount(event.target.value);
});

numRange.addEventListener("input", (event) => {
  syncCount(event.target.value);
});

syncCount(activeCount);
renderPlaceholders(activeCount);
setStatus("idle");
