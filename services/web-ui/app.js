const API_BASE = window.location.hostname === "localhost"
    ? "http://localhost:8000"
    : "";

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
            const err = await resp.json();
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

    // Confidence score
    const pct = (r.confidence_score * 100).toFixed(1);
    document.getElementById("score-display").textContent = `${pct}%`;

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
        for (const cs of breakdown.component_scores) {
            const row = document.createElement("div");
            row.className = "component-row";
            row.innerHTML = `
                <span>${cs.component}</span>
                <span class="concern-${cs.concern_level}">${(cs.score * 100).toFixed(0)}%</span>
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
        row.innerHTML = `
            <span>${f.factor}</span>
            <span class="concern-${f.concern_level}">${f.concern_level.replace("_", " ")}</span>
        `;
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
        li.textContent = `${(score * 100).toFixed(0)}% — ${entry.text.substring(0, 50)}...`;
        li.onclick = () => {
            document.getElementById("claim-text").value = entry.text;
            displayResult(entry.result);
        };
        list.appendChild(li);
    }
}
