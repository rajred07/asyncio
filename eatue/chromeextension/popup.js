// PlaylistGenius - Watch Later Sync Extension
// =============================================
// Flow:
//   1. Read JWT from the PlaylistGenius tab's localStorage ("accessToken")
//   2. Inject scraper into the YouTube Watch Later tab
//   3. POST scraped video IDs directly to backend /api/watchlater/import-direct
//   4. Poll /api/watchlater/status/{job_id} every 3 seconds
//   5. Show live progress + completion stats in popup

const BACKEND_URL = "https://asyncio.onrender.com";   // ← Deployed Render Backend URL
const APP_URL = "http://localhost:3000";   // ← Change to your prod frontend URL later
const TOKEN_KEY = "accessToken";             // ← localStorage key from AuthContext.tsx
const POLL_INTERVAL = 3000;                      // Poll every 3 seconds

// DOM refs
let importBtn, statusBox, statusText, spinner, progressBar;
let progressLeft, progressRight, doneInfo, userAvatar, userName;
let mainUI, authError, notYouTubeWarning;

let pollTimer = null;

// ─── Init ────────────────────────────────────────────────────────────────────

document.addEventListener("DOMContentLoaded", async () => {
  importBtn = document.getElementById("importBtn");
  statusBox = document.getElementById("statusBox");
  statusText = document.getElementById("statusText");
  spinner = document.getElementById("spinner");
  progressBar = document.getElementById("progressBar");
  progressLeft = document.getElementById("progressLeft");
  progressRight = document.getElementById("progressRight");
  doneInfo = document.getElementById("doneInfo");
  userAvatar = document.getElementById("userAvatar");
  userName = document.getElementById("userName");
  mainUI = document.getElementById("mainUI");
  authError = document.getElementById("authError");
  notYouTubeWarning = document.getElementById("notYouTubeWarning");

  // Load saved settings
  const saved = await chrome.storage.local.get(["videoLimit", "lastJobId"]);
  if (saved.videoLimit) {
    document.getElementById("videoLimit").value = saved.videoLimit;
  }

  // Step 1 — Read JWT from localStorage of any open PlaylistGenius tab
  const token = await getTokenFromBrowser();

  if (!token) {
    showAuthError();
    return;
  }

  // Step 2 — Decode JWT to get username (payload is base64)
  const userInfo = decodeJWT(token);

  showMainUI(userInfo);

  // Step 3 — Check if we're on YouTube Watch Later
  await checkCurrentTab();

  // If a previous job was running, resume polling it
  if (saved.lastJobId) {
    resumePoll(saved.lastJobId, token);
  }

  // Bind buttons
  importBtn.addEventListener("click", () => startImport(token));
  document.getElementById("logoutBtn").addEventListener("click", () => {
    chrome.storage.local.remove(["lastJobId"]);
    showAuthError();
  });
  document.getElementById("openLoginBtn").addEventListener("click", () => {
    chrome.tabs.create({ url: `${APP_URL}/login` });
  });
  document.getElementById("viewPlaylistsBtn").addEventListener("click", () => {
    chrome.tabs.create({ url: `${APP_URL}/profile` });
  });
});

// ─── Get JWT from browser ────────────────────────────────────────────────────

async function getTokenFromBrowser() {
  // Read token from any tab that has the app open
  // Falls back to reading from any YouTube.com tab (since extension runs there)

  // Try to find an open PlaylistGenius tab and read localStorage
  const tabs = await chrome.tabs.query({ url: `${APP_URL}/*` });

  for (const tab of tabs) {
    try {
      const results = await chrome.scripting.executeScript({
        target: { tabId: tab.id },
        func: (key) => localStorage.getItem(key),
        args: [TOKEN_KEY],
      });
      if (results?.[0]?.result) {
        return results[0].result;
      }
    } catch (_) {
      // Tab might not allow scripting — skip
    }
  }

  // Fallback: check extension's own storage (in case we cached it)
  const stored = await chrome.storage.local.get([TOKEN_KEY]);
  return stored[TOKEN_KEY] || null;
}

// ─── Decode JWT payload (no verification needed client-side) ─────────────────

function decodeJWT(token) {
  try {
    const parts = token.split(".");
    if (parts.length !== 3) return null;
    const payload = JSON.parse(atob(parts[1].replace(/-/g, "+").replace(/_/g, "/")));
    return payload;
  } catch (_) {
    return null;
  }
}

// ─── Check current tab is YouTube Watch Later ────────────────────────────────

async function checkCurrentTab() {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  const isWatchLater = tab?.url?.includes("youtube.com") && tab?.url?.includes("list=WL");
  const isYouTube = tab?.url?.includes("youtube.com");

  if (!isYouTube) {
    notYouTubeWarning.style.display = "block";
    importBtn.disabled = true;
  } else if (!isWatchLater) {
    notYouTubeWarning.style.display = "block";
    notYouTubeWarning.innerHTML = "⚠️ Make sure you're on your <strong>Watch Later</strong> playlist, not just YouTube.";
    importBtn.disabled = true;
  } else {
    notYouTubeWarning.style.display = "none";
    importBtn.disabled = false;
  }
}

// ─── Main Import Flow ─────────────────────────────────────────────────────────

async function startImport(token) {
  const limit = parseInt(document.getElementById("videoLimit").value, 10) || 310;

  // Save settings
  chrome.storage.local.set({ videoLimit: limit });

  try {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

    if (!tab.url.includes("youtube.com")) {
      showError("Please go to YouTube > Watch Later (youtube.com/playlist?list=WL)");
      return;
    }

    setBusy(true);
    setStatus("⏳ Scanning your Watch Later playlist...", 0, limit);

    // ── Step 1: Scrape video IDs from the page ──
    const results = await chrome.scripting.executeScript({
      target: { tabId: tab.id },
      func: scrapeWatchLaterVideos,
      args: [limit],
    });

    if (!results?.[0]?.result) {
      throw new Error("Could not scrape videos. Make sure you're on your Watch Later playlist page.");
    }

    const videos = results[0].result;

    if (videos.length === 0) {
      throw new Error("No videos found. Navigate to youtube.com/playlist?list=WL and try again.");
    }

    setStatus(`📡 Found ${videos.length} videos. Sending to PlaylistGenius...`, 5, videos.length);

    // ── Step 2: POST to backend ──
    const payload = {
      videos: videos,
      scrapedAt: new Date().toISOString(),
    };

    const response = await fetch(`${BACKEND_URL}/api/watchlater/import-direct`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${token}`,
      },
      body: JSON.stringify(payload),
    });

    if (response.status === 401) {
      showAuthError();
      throw new Error("Session expired. Please log in again.");
    }

    if (!response.ok) {
      const err = await response.json().catch(() => ({}));
      throw new Error(err.detail || `Server error: ${response.status}`);
    }

    const data = await response.json();
    const jobId = data.job_id;

    // Save job ID so we can resume polling if popup closes
    chrome.storage.local.set({ lastJobId: jobId });

    setStatus(`🤖 AI categorizing your videos (this takes 2–4 min for ${videos.length} videos)...`, 10, videos.length);

    // ── Step 3: Poll for status ──
    startPolling(jobId, token, videos.length);

  } catch (err) {
    showError(err.message);
  }
}

// ─── Injected scraper (runs in YouTube tab) ───────────────────────────────────

async function scrapeWatchLaterVideos(limit) {
  const seen = new Set();
  const videos = [];
  const maxAttempts = 60;
  let attempts = 0;

  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

  const selectors = [
    "ytd-playlist-video-renderer",
    "ytd-playlist-panel-video-renderer",
    "ytd-video-renderer",
    "ytd-grid-video-renderer",
  ].join(",");

  const extractId = (url) => {
    const m = url.match(/[?&]v=([^&]+)/);
    return m ? m[1] : null;
  };

  while (videos.length < limit && attempts < maxAttempts) {
    document.querySelectorAll(selectors).forEach((el) => {
      if (videos.length >= limit) return;
      const AnchorTitle = el.querySelector("a#video-title");
      if (!AnchorTitle?.href) return;
      const id = extractId(AnchorTitle.href);
      if (!id || seen.has(id)) return;

      seen.add(id);
      videos.push({
        videoId: id,
        url: AnchorTitle.href,
        title: AnchorTitle.title || AnchorTitle.textContent?.trim() || "",
        savedIndex: videos.length,
      });
    });

    if (videos.length >= limit) break;

    // Scroll down to load more
    const before = document.documentElement.scrollHeight;
    window.scrollTo(0, before);
    await sleep(1200);

    const after = document.documentElement.scrollHeight;
    if (after === before) attempts++;
    else attempts = 0;
  }

  return videos;
}

// ─── Status Polling ───────────────────────────────────────────────────────────

function startPolling(jobId, token, totalVideos) {
  if (pollTimer) clearInterval(pollTimer);

  pollTimer = setInterval(async () => {
    try {
      const res = await fetch(`${BACKEND_URL}/api/watchlater/status/${jobId}`, {
        headers: { "Authorization": `Bearer ${token}` },
      });

      if (!res.ok) return;

      const job = await res.json();
      const pct = totalVideos > 0
        ? Math.min(95, Math.round((job.videos_imported / totalVideos) * 100))
        : 50;

      if (job.status === "completed") {
        clearInterval(pollTimer);
        pollTimer = null;
        chrome.storage.local.remove(["lastJobId"]);
        showComplete(job);
      } else if (job.status === "failed") {
        clearInterval(pollTimer);
        pollTimer = null;
        chrome.storage.local.remove(["lastJobId"]);
        showError(job.error || "Pipeline failed. Please try again.");
      } else {
        setStatus(job.progress || "Processing...", pct, totalVideos);
        progressLeft.textContent = `${job.videos_imported}/${totalVideos} videos`;
        progressRight.textContent = `${job.playlists_created} playlists`;
      }
    } catch (_) {
      // Network error — keep trying
    }
  }, POLL_INTERVAL);
}

function resumePoll(jobId, token) {
  // Resume polling a previous job (in case popup was closed mid-import)
  setStatus("⏳ Checking previous import...", 10, 0);
  statusBox.classList.add("show");
  startPolling(jobId, token, 0);
}

// ─── UI Helpers ──────────────────────────────────────────────────────────────

function showAuthError() {
  authError.style.display = "flex";
  mainUI.style.display = "none";
}

function showMainUI(payload) {
  authError.style.display = "none";
  mainUI.style.display = "flex";

  // Show user info from JWT payload (sub = user_id, or check your token shape)
  const displayName = payload?.username || payload?.email || `User #${payload?.sub}` || "You";
  userName.textContent = displayName;
  userAvatar.textContent = displayName.charAt(0).toUpperCase();
}

function setBusy(busy) {
  importBtn.disabled = busy;
  importBtn.innerHTML = busy
    ? `<span class="spinner" style="width:16px;height:16px;border-width:2px;display:inline-block;vertical-align:middle;margin-right:6px"></span>Syncing...`
    : `<span>⚡</span> Sync Watch Later`;
}

function setStatus(message, pct = 0, total = 0) {
  statusBox.classList.add("show");
  statusBox.classList.remove("error", "success");
  spinner.classList.remove("hidden");
  statusText.textContent = message;
  progressBar.style.width = `${pct}%`;
  doneInfo.classList.remove("show");
}

function showError(message) {
  clearInterval(pollTimer);
  setBusy(false);
  statusBox.classList.add("show", "error");
  statusBox.classList.remove("success");
  spinner.classList.add("hidden");
  statusText.textContent = `❌ ${message}`;
  progressBar.style.width = "0%";
  doneInfo.classList.remove("show");
}

function showComplete(job) {
  setBusy(false);
  statusBox.classList.add("show", "success");
  statusBox.classList.remove("error");
  spinner.classList.add("hidden");
  statusText.textContent = "✅ Import complete! Your smart playlists are ready.";
  progressBar.style.width = "100%";

  document.getElementById("donePlaylistCount").textContent = job.playlists_created;
  document.getElementById("doneVideoCount").textContent = job.videos_imported;
  doneInfo.classList.add("show");
}
