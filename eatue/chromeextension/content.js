// TubeSort Scraper - Content Script
// Handles infinite scroll and data extraction from YouTube Watch Later

class TubeSortScraper {
  constructor() {
    this.videos = new Map(); // Use Map to avoid duplicates
    this.isScaping = false;
    this.scrollAttempts = 0;
    this.maxScrollAttempts = 50; // Safety limit
    this.lastHeight = 0;
  }

  // Utility: Sleep function for waiting
  sleep(ms) {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }

  // Check if we're on the Watch Later page
  isWatchLaterPage() {
    return (
      window.location.href.includes("/playlist?list=WL") ||
      window.location.href.includes("&list=WL")
    );
  }

  // Scroll to bottom and wait for content to load
  async scrollToBottom() {
    const currentHeight = document.documentElement.scrollHeight;

    // Scroll to bottom
    window.scrollTo({
      top: currentHeight,
      behavior: "smooth",
    });

    // Wait for content to load
    await this.sleep(1500);

    const newHeight = document.documentElement.scrollHeight;

    // Check if new content loaded
    if (newHeight > this.lastHeight) {
      this.lastHeight = newHeight;
      this.scrollAttempts = 0; // Reset attempts on successful load
      return true; // More content loaded
    } else {
      this.scrollAttempts++;
      return false; // No new content
    }
  }

  // Extract video data from the current DOM
  extractVideos() {
    // YouTube uses different selectors, we'll try multiple approaches
    const selectors = [
      "ytd-playlist-video-renderer",
      "ytd-playlist-panel-video-renderer",
      "ytd-video-renderer",
    ];

    let videoElements = [];

    for (const selector of selectors) {
      const elements = document.querySelectorAll(selector);
      if (elements.length > 0) {
        videoElements = elements;
        break;
      }
    }

    console.log(
      `[TubeSort] Found ${videoElements.length} video elements in DOM`,
    );

    videoElements.forEach((element) => {
      try {
        // Extract video title and URL
        const titleElement = element.querySelector("a#video-title");
        if (!titleElement) return;

        const title =
          titleElement.getAttribute("title") || titleElement.textContent.trim();
        const relativeUrl = titleElement.getAttribute("href");

        if (!title || !relativeUrl) return;

        // Build full URL
        const videoUrl = relativeUrl.startsWith("http")
          ? relativeUrl
          : `https://www.youtube.com${relativeUrl}`;

        // Extract video ID from URL
        const videoId = this.extractVideoId(videoUrl);
        if (!videoId) return;

        // Extract channel name
        let channelName = "Unknown";
        const channelElement =
          element.querySelector("ytd-channel-name a") ||
          element.querySelector("yt-formatted-string.ytd-channel-name a");

        if (channelElement) {
          channelName = channelElement.textContent.trim();
        }

        // Extract thumbnail
        let thumbnail = "";
        const thumbnailElement = element.querySelector("img");
        if (thumbnailElement) {
          thumbnail =
            thumbnailElement.src || thumbnailElement.getAttribute("data-thumb");
        }

        // Extract duration if available
        let duration = "";
        const durationElement =
          element.querySelector(
            "ytd-thumbnail-overlay-time-status-renderer span",
          ) ||
          element.querySelector(
            "span.ytd-thumbnail-overlay-time-status-renderer",
          );
        if (durationElement) {
          duration = durationElement.textContent.trim();
        }

        // Only add if we haven't seen this video ID before
        if (!this.videos.has(videoId)) {
          this.videos.set(videoId, {
            videoId,
            title,
            url: videoUrl,
            channelName,
            thumbnail,
            duration,
            scrapedAt: new Date().toISOString(),
          });
        }
      } catch (error) {
        console.error("[TubeSort] Error extracting video:", error);
      }
    });
  }

  // Extract video ID from YouTube URL
  extractVideoId(url) {
    const patterns = [
      /[?&]v=([^&]+)/,
      /\/embed\/([^?]+)/,
      /\/v\/([^?]+)/,
      /youtu\.be\/([^?]+)/,
    ];

    for (const pattern of patterns) {
      const match = url.match(pattern);
      if (match) return match[1];
    }
    return null;
  }

  // Main scraping function
  async startScraping() {
    if (this.isScaping) {
      console.log("[TubeSort] Scraping already in progress");
      return;
    }

    if (!this.isWatchLaterPage()) {
      alert("Please navigate to your YouTube Watch Later playlist first!");
      return;
    }

    this.isScaping = true;
    this.videos.clear();
    this.scrollAttempts = 0;
    this.lastHeight = 0;

    console.log("[TubeSort] Starting scrape...");

    // Send initial status
    window.postMessage(
      {
        type: "TUBESORT_STATUS",
        status: "Initializing scraper...",
      },
      "*",
    );

    try {
      // Initial extraction
      this.extractVideos();
      console.log(`[TubeSort] Initial extraction: ${this.videos.size} videos`);

      // Scroll and extract until we reach the bottom
      let hasMoreContent = true;
      let consecutiveNoContent = 0;

      while (hasMoreContent && this.scrollAttempts < this.maxScrollAttempts) {
        const previousCount = this.videos.size;

        window.postMessage(
          {
            type: "TUBESORT_STATUS",
            status: `Scrolling... Found ${this.videos.size} videos so far`,
          },
          "*",
        );

        hasMoreContent = await this.scrollToBottom();
        this.extractVideos();

        const newCount = this.videos.size;

        if (newCount === previousCount) {
          consecutiveNoContent++;
          if (consecutiveNoContent >= 3) {
            console.log(
              "[TubeSort] No new videos found after 3 scroll attempts. Finishing...",
            );
            break;
          }
        } else {
          consecutiveNoContent = 0;
          console.log(
            `[TubeSort] Found ${newCount - previousCount} new videos. Total: ${newCount}`,
          );
        }

        // Small delay between scrolls
        await this.sleep(500);
      }

      // Final extraction to be sure
      this.extractVideos();

      const videoArray = Array.from(this.videos.values());

      console.log(
        `[TubeSort] ✅ Scraping complete! Total videos: ${videoArray.length}`,
      );

      // Send completion message with data
      window.postMessage(
        {
          type: "TUBESORT_COMPLETE",
          data: videoArray,
          count: videoArray.length,
        },
        "*",
      );

      // Auto-download JSON
      this.downloadJSON(videoArray);
    } catch (error) {
      console.error("[TubeSort] Scraping error:", error);
      window.postMessage(
        {
          type: "TUBESORT_ERROR",
          error: error.message,
        },
        "*",
      );
    } finally {
      this.isScaping = false;
    }
  }

  // Download the scraped data as JSON
  downloadJSON(data) {
    const jsonContent = JSON.stringify(
      {
        scrapedAt: new Date().toISOString(),
        totalVideos: data.length,
        videos: data,
      },
      null,
      2,
    );

    const blob = new Blob([jsonContent], { type: "application/json" });
    const url = URL.createObjectURL(blob);

    const a = document.createElement("a");
    a.href = url;
    a.download = `watch-later-${new Date().toISOString().split("T")[0]}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);

    console.log("[TubeSort] JSON file downloaded!");
  }
}

// Initialize scraper
const scraper = new TubeSortScraper();

// Listen for messages from popup
window.addEventListener("message", (event) => {
  if (event.source !== window) return;

  if (event.data.type === "TUBESORT_START") {
    scraper.startScraping();
  }
});

console.log("[TubeSort] Content script loaded and ready!");
