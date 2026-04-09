/* dashboard.js — Chart.js rendering + UI interactions */

"use strict";

// ─── Helpers ─────────────────────────────────────────────────
const fmt = (n) =>
  "₹" + Number(n).toLocaleString("en-IN", { minimumFractionDigits: 2, maximumFractionDigits: 2 });

// Shared Chart.js defaults (dark theme)
Chart.defaults.color          = "#7a8099";
Chart.defaults.borderColor    = "#2a2f3e";
Chart.defaults.font.family    = "'DM Mono', monospace";
Chart.defaults.font.size      = 11;

// ─── Toggle "Add Transaction" form ───────────────────────────
document.getElementById("toggle-form")?.addEventListener("click", () => {
  const form = document.getElementById("add-form");
  const btn  = document.getElementById("toggle-form");
  if (form.style.display === "none") {
    form.style.display = "block";
    btn.textContent    = "✕ Close";
    // Default date to today
    const dateInput = form.querySelector('input[type="date"]');
    if (dateInput && !dateInput.value) {
      dateInput.value = new Date().toISOString().split("T")[0];
    }
  } else {
    form.style.display = "none";
    btn.textContent    = "+ New";
  }
});

// ─── SQL tab switcher ─────────────────────────────────────────
document.querySelectorAll(".sql-tab").forEach((tab) => {
  tab.addEventListener("click", () => {
    document.querySelectorAll(".sql-tab").forEach((t) => t.classList.remove("active"));
    document.querySelectorAll(".sql-panel").forEach((p) => p.classList.remove("active"));
    tab.classList.add("active");
    document.getElementById("tab-" + tab.dataset.tab)?.classList.add("active");
  });
});

// ─── Fetch analytics from Flask API ──────────────────────────
async function loadAnalytics() {
  let data;
  try {
    const res = await fetch("/api/analytics");
    if (!res.ok) throw new Error("API error");
    data = await res.json();
  } catch (e) {
    console.error("Failed to load analytics:", e);
    return;
  }

  // KPI cards
  document.getElementById("kpi-income").textContent  = fmt(data.savings.gross_income);
  document.getElementById("kpi-expense").textContent = fmt(data.savings.gross_expense);
  const savings = data.savings.net_savings;
  const savingsEl = document.getElementById("kpi-savings");
  savingsEl.textContent = fmt(savings);
  savingsEl.style.color = savings >= 0 ? "var(--accent-green)" : "var(--accent-red)";

  // ── Bar Chart: Monthly Income vs Expense ──
  const monthly = data.monthly;
  new Chart(document.getElementById("chartMonthly"), {
    type: "bar",
    data: {
      labels: monthly.map((r) => r.month),
      datasets: [
        {
          label: "Income",
          data:  monthly.map((r) => r.total_income),
          backgroundColor: "rgba(45,212,160,0.75)",
          borderColor:     "rgba(45,212,160,1)",
          borderWidth: 1,
          borderRadius: 4,
        },
        {
          label: "Expense",
          data:  monthly.map((r) => r.total_expense),
          backgroundColor: "rgba(247,95,95,0.75)",
          borderColor:     "rgba(247,95,95,1)",
          borderWidth: 1,
          borderRadius: 4,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { position: "top" },
        tooltip: {
          callbacks: {
            label: (ctx) => ` ${ctx.dataset.label}: ${fmt(ctx.parsed.y)}`,
          },
        },
      },
      scales: {
        x: { grid: { color: "#1e2235" } },
        y: {
          grid:  { color: "#1e2235" },
          ticks: { callback: (v) => "₹" + (v / 1000).toFixed(0) + "k" },
        },
      },
    },
  });

  // ── Pie Chart: Category-wise expenses ──
  const cats = data.categories;
  const PALETTE = [
    "#f75f5f","#f7c25f","#4f6ef7","#2dd4a0",
    "#a78bfa","#fb923c","#34d399","#60a5fa",
    "#f472b6","#a3e635",
  ];
  new Chart(document.getElementById("chartCategory"), {
    type: "doughnut",
    data: {
      labels: cats.map((c) => c.category),
      datasets: [
        {
          data:            cats.map((c) => c.total_spent),
          backgroundColor: cats.map((_, i) => PALETTE[i % PALETTE.length]),
          borderColor:     "#141720",
          borderWidth: 2,
          hoverOffset: 8,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      cutout: "60%",
      plugins: {
        legend: { position: "right", labels: { boxWidth: 10, padding: 10 } },
        tooltip: {
          callbacks: {
            label: (ctx) => ` ${ctx.label}: ${fmt(ctx.parsed)}`,
          },
        },
      },
    },
  });
}

loadAnalytics();
