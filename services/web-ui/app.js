// Determine API base URL:
// - In Docker Compose, the browser hits the host machine, so use port 8000
// - In local dev, same thing
const API_BASE = `${window.location.protocol}//${window.location.hostname}:8000`;

const history = [];

async function submitClaim() {
    const text = document.getElementById("claim-text").value.trim();
    if (!text) return;

    const btn = document.getElementById("submit-btn");
    btn.disabled = true;
    btn.textContent = "Scoring...";

    try {
        const resp = await fetch(`${API_BASE}/api/score`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ text }),
        });

        if (!resp.ok) {
            const err = await resp.json().catch(() => ({ detail: resp.statusText }));
            alert(`Error: ${err.detail || resp.statusText}`);
            return;
        }

        const result = await resp.json();
        displayResult(result);
        addToHistory(text, result);
    } catch (e) {
        alert(`Request failed: ${e.message}`);
    } finally {
        btn.disabled = false;
        btn.textContent = "Score Claim";
    }
}

function displayResult(r) {
    const section = document.getElementById("result-section");
    section.classList.remove("hidden");

    // Confidence score with color coding
    const pct = (r.confidence_score * 100).toFixed(1);
    const scoreEl = document.getElementById("score-display");
    scoreEl.textContent = `${pct}%`;
    scoreEl.style.color = r.confidence_score >= 0.8 ? "#166534"
        : r.confidence_score >= 0.4 ? "#854d0e" : "#991b1b";

    // Action badge
    const actionEl = document.getElementById("action-display");
    const labels = {
        auto_approve: "Auto-Approve",
        human_review: "Human Review",
        auto_flag: "Auto-Flag",
    };
    actionEl.textContent = labels[r.recommended_action] || r.recommended_action;
    actionEl.className = `action-display action-${r.recommended_action}`;

    // Component scores
    const compEl = document.getElementById("components-display");
    compEl.innerHTML = "";
    for (const breakdown of r.score_breakdown) {
        if (breakdown.component_scores.length === 0) continue;
        // Path header
        const header = document.createElement("div");
        header.className = "component-row";
        header.style.fontWeight = "600";
        header.style.background = "#e5e7eb";
        const pathLabel = breakdown.path === "vector_similarity" ? "Vector Similarity" : "ML Model";
        header.innerHTML = `<span>${pathLabel}</span><span>${(breakdown.overall_score * 100).toFixed(0)}%</span>`;
        compEl.appendChild(header);

        for (const cs of breakdown.component_scores) {
            const row = document.createElement("div");
            row.className = "component-row";
            row.innerHTML = `
                <span>&nbsp;&nbsp;${cs.component}</span>
                <span class="concern-${cs.concern_level}" title="${cs.explanation || ''}">${(cs.score * 100).toFixed(0)}%</span>
            `;
            compEl.appendChild(row);
        }
    }

    // Contributing factors
    const factorsEl = document.getElementById("factors-display");
    factorsEl.innerHTML = "";
    for (const f of r.contributing_factors) {
        const row = document.createElement("div");
        row.className = "factor-row";
        const label = f.concern_level.replace(/_/g, " ");
        row.innerHTML = `
            <span>${f.factor}</span>
            <span class="concern-${f.concern_level}">${label}</span>
        `;
        if (f.detail) {
            row.title = f.detail;
        }
        factorsEl.appendChild(row);
    }
}

function addToHistory(text, result) {
    history.unshift({ text, result, time: new Date() });
    renderHistory();
}

function renderHistory() {
    const list = document.getElementById("history-list");
    list.innerHTML = "";
    for (const entry of history) {
        const li = document.createElement("li");
        const score = entry.result.confidence_score;
        li.className = score >= 0.8 ? "score-high" : score >= 0.4 ? "score-medium" : "score-low";
        const preview = entry.text.substring(0, 60).replace(/\n/g, " ");
        li.textContent = `${(score * 100).toFixed(0)}% — ${preview}...`;
        li.onclick = () => {
            document.getElementById("claim-text").value = entry.text;
            displayResult(entry.result);
        };
        list.appendChild(li);
    }
}
