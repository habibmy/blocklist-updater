if ("serviceWorker" in navigator) {
  navigator.serviceWorker.register("/addblockdomain/sw.js", {
    scope: "/addblockdomain",
  });
}

const params = new URLSearchParams(window.location.search);
const rawInput = params.get("url") || params.get("text") || "";
const statusEl = document.getElementById("status");

// Helper to extract domain client-side
function getDomain(input) {
  const match = input.match(/https?:\/\/([^\/\s:]+)/i);
  return match
    ? match[1].toLowerCase()
    : input.includes(".")
      ? input.trim().toLowerCase()
      : null;
}

if (rawInput) {
  const domain = getDomain(rawInput);

  if (!domain) {
    statusEl.className = "status error";
    statusEl.textContent = "Invalid link or domain received.";
  } else {
    statusEl.className = "status";
    statusEl.textContent = `Adding ${domain}...`;

    fetch("/addblockdomain/api", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ domain: domain }),
    })
      .then(async (res) => {
        const data = await res.json();
        if (!res.ok) throw new Error(data.message || "Failed to update");

        if (data.status === "exists") {
          statusEl.className = "status info";
          statusEl.textContent = `⚠️ Already blocked: ${domain}`;
        } else {
          statusEl.className = "status success";
          statusEl.textContent = `✅ Blocked: ${domain}`;
          if ("vibrate" in navigator) navigator.vibrate([40, 60, 40]);
        }

        setTimeout(() => window.close(), 1200);
      })
      .catch((err) => {
        statusEl.className = "status error";
        statusEl.textContent = `❌ ${err.message}`;
      });
  }
}
