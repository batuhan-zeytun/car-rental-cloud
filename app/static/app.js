const state = {
  allCars: [],
  cars: [],
  customers: [],
  rentals: [],
  carSearch: "",
  rentalSearch: ""
};

const $ = (sel) => document.querySelector(sel);

const money = (v) =>
  new Intl.NumberFormat("tr-TR", {
    style: "currency",
    currency: "TRY",
    maximumFractionDigits: 0
  }).format(v || 0);

function toast(msg, type = "ok") {
  const n = $("#toast");
  n.textContent = msg;
  n.className = `toast show ${type}`;
  setTimeout(() => { n.className = "toast"; }, 2800);
}

async function api(path, opts = {}) {
  const res = await fetch(path, {
    headers: { "Content-Type": "application/json" },
    ...opts
  });
  const ct = res.headers.get("content-type") || "";
  const body = ct.includes("application/json") ? await res.json() : await res.text();
  if (!res.ok) throw new Error(body.error || body || "Request failed");
  return body;
}

function formPayload(form) {
  return Object.fromEntries(new FormData(form).entries());
}

function badge(status) {
  return `<span class="badge ${status}">${status}</span>`;
}

/* ── Stats ──────────────────────────────────── */
function updateStats() {
  const available = state.allCars.filter((c) => c.status === "available").length;
  const active = state.rentals.filter((r) => r.status === "active").length;
  const revenue = state.rentals
    .filter((r) => r.status !== "cancelled")
    .reduce((s, r) => s + r.total_price, 0);

  $("#availableCount").textContent = available;
  $("#activeRentalCount").textContent = active;
  $("#revenueTotal").textContent = money(revenue);
}

/* ── Cars ───────────────────────────────────── */
function filteredCars() {
  const q = state.carSearch.toLowerCase();
  if (!q) return state.cars;
  return state.cars.filter((c) =>
    c.plate_number.toLowerCase().includes(q) ||
    c.make.toLowerCase().includes(q) ||
    c.model.toLowerCase().includes(q) ||
    (c.location || "").toLowerCase().includes(q)
  );
}

function renderCars() {
  const list = $("#carList");
  const cars = filteredCars();

  if (!cars.length) {
    list.innerHTML = `<li class="empty">${state.carSearch ? "No cars match your search." : "No cars match this filter."}</li>`;
    return;
  }

  list.innerHTML = cars.map((car) => `
    <li class="fleet-row status-${car.status}">
      <div>
        <strong>${car.make} ${car.model}</strong>
        <span>${car.year} · ${car.plate_number}</span>
        <small>${car.location} · ${money(car.daily_rate)} / day</small>
      </div>
      <div class="row-actions">
        ${badge(car.status)}
        <select data-car-status="${car.id}" aria-label="Change status for ${car.plate_number}">
          <option value="available" ${car.status === "available" ? "selected" : ""}>Available</option>
          <option value="rented"    ${car.status === "rented"    ? "selected" : ""}>Rented</option>
          <option value="maintenance" ${car.status === "maintenance" ? "selected" : ""}>Maintenance</option>
        </select>
      </div>
    </li>
  `).join("");

  list.querySelectorAll("[data-car-status]").forEach((sel) => {
    sel.addEventListener("change", async (e) => {
      try {
        await api(`/api/cars/${e.target.dataset.carStatus}/status`, {
          method: "PATCH",
          body: JSON.stringify({ status: e.target.value })
        });
        toast("Car status updated ✓");
        await refresh();
      } catch (err) {
        toast(err.message, "error");
      }
    });
  });
}

function renderRentalOptions() {
  const avail = state.allCars.filter((c) => c.status === "available");
  $("#rentalCar").innerHTML = avail
    .map((c) => `<option value="${c.id}">${c.plate_number} · ${c.make} ${c.model}</option>`)
    .join("");
  $("#rentalCustomer").innerHTML = state.customers
    .map((c) => `<option value="${c.id}">${c.full_name}</option>`)
    .join("");
}

/* ── Rentals ────────────────────────────────── */
function filteredRentals() {
  const q = state.rentalSearch.toLowerCase();
  if (!q) return state.rentals;
  return state.rentals.filter((r) =>
    r.customer.full_name.toLowerCase().includes(q) ||
    r.customer.email.toLowerCase().includes(q) ||
    r.car.plate_number.toLowerCase().includes(q) ||
    `${r.car.make} ${r.car.model}`.toLowerCase().includes(q)
  );
}

function renderRentals() {
  const tbody = $("#rentalRows");
  const rentals = filteredRentals();

  if (!rentals.length) {
    tbody.innerHTML = `<tr><td colspan="6" class="empty">${state.rentalSearch ? "No rentals match your search." : "No rentals yet."}</td></tr>`;
    return;
  }

  tbody.innerHTML = rentals.map((r) => `
    <tr>
      <td>${r.car.plate_number}<br><small>${r.car.make} ${r.car.model}</small></td>
      <td>${r.customer.full_name}<br><small>${r.customer.email}</small></td>
      <td>${r.start_date} → ${r.end_date}<br><small>${r.days} day(s)</small></td>
      <td>${money(r.total_price)}</td>
      <td>${badge(r.status)}</td>
      <td>${r.status === "active" ? `<button class="ghost" data-return="${r.id}">↩ Return</button>` : ""}</td>
    </tr>
  `).join("");

  tbody.querySelectorAll("[data-return]").forEach((btn) => {
    btn.addEventListener("click", async (e) => {
      try {
        await api(`/api/rentals/${e.target.dataset.return}/return`, { method: "POST" });
        toast("Rental returned ✓");
        await refresh();
      } catch (err) {
        toast(err.message, "error");
      }
    });
  });
}

/* ── Readiness ──────────────────────────────── */
async function loadReadiness() {
  try {
    await api("/readyz");
    $("#readyDot").className = "dot ok";
    $("#readyText").textContent = "online";
  } catch {
    $("#readyDot").className = "dot error";
    $("#readyText").textContent = "not ready";
  }
}

/* ── Data loaders ───────────────────────────── */
async function loadCars() {
  const f = $("#fleetFilter").value;
  const data = await api(`/api/cars${f ? `?status=${f}` : ""}`);
  state.cars = data.items;
}

async function loadAllCars() {
  const data = await api("/api/cars");
  state.allCars = data.items;
}

async function loadCustomers() {
  const data = await api("/api/customers");
  state.customers = data.items;
}

async function loadRentals() {
  const f = $("#rentalFilter").value;
  const data = await api(`/api/rentals${f ? `?status=${f}` : ""}`);
  state.rentals = data.items;
}

/* ── Metrics ────────────────────────────────── */
function parsePrometheus(text) {
  const out = {};
  for (const line of text.split("\n")) {
    if (line.startsWith("#") || !line.trim()) continue;
    const m = line.match(/^(\w+)\{(\w+)="([^"]+)"\}\s+(\d+)/);
    if (m) {
      const [, metric, , value, count] = m;
      if (!out[metric]) out[metric] = {};
      out[metric][value] = parseInt(count, 10);
    }
  }
  return out;
}

function metricBars(statuses, data, total) {
  return statuses.map((s) => {
    const n = data[s] || 0;
    const pct = total > 0 ? Math.round((n / total) * 100) : 0;
    return `
      <div class="metric-bar-row">
        <span class="metric-bar-label">${s}</span>
        <div class="metric-bar-track">
          <div class="metric-bar-fill ${s}" style="width:${pct}%"></div>
        </div>
        <span class="metric-bar-value">${n}</span>
      </div>`;
  }).join("");
}

async function loadMetrics() {
  const grid = $("#metricsGrid");
  try {
    const text = await fetch("/metrics").then((r) => r.text());
    const data = parsePrometheus(text);

    const cars = data["car_rental_cars_total"] || {};
    const rents = data["car_rental_rentals_total"] || {};
    const carTotal = Object.values(cars).reduce((s, v) => s + v, 0);
    const rentTotal = Object.values(rents).reduce((s, v) => s + v, 0);

    grid.innerHTML = `
      <div class="metric-group">
        <h3>🚗 Cars by status</h3>
        ${metricBars(["available", "rented", "maintenance"], cars, carTotal || 1)}
        <p class="metric-total">${carTotal} total vehicles</p>
      </div>
      <div class="metric-group">
        <h3>📋 Rentals by status</h3>
        ${metricBars(["active", "completed", "cancelled"], rents, rentTotal || 1)}
        <p class="metric-total">${rentTotal} total rentals</p>
      </div>`;
  } catch {
    grid.innerHTML = `<p class="empty">Could not load metrics.</p>`;
  }
}

/* ── Refresh ────────────────────────────────── */
async function refresh() {
  await loadReadiness();
  await loadAllCars();
  await loadCustomers();
  renderRentalOptions();
  await loadCars();
  await loadRentals();
  renderCars();
  renderRentals();
  updateStats();
}

/* ── Bind ───────────────────────────────────── */
function bindAll() {
  $("#carForm").addEventListener("submit", async (e) => {
    e.preventDefault();
    try {
      await api("/api/cars", { method: "POST", body: JSON.stringify(formPayload(e.target)) });
      e.target.reset();
      toast("Car saved ✓");
      await refresh();
    } catch (err) { toast(err.message, "error"); }
  });

  $("#customerForm").addEventListener("submit", async (e) => {
    e.preventDefault();
    try {
      await api("/api/customers", { method: "POST", body: JSON.stringify(formPayload(e.target)) });
      e.target.reset();
      toast("Customer saved ✓");
      await refresh();
    } catch (err) { toast(err.message, "error"); }
  });

  $("#rentalForm").addEventListener("submit", async (e) => {
    e.preventDefault();
    try {
      await api("/api/rentals", { method: "POST", body: JSON.stringify(formPayload(e.target)) });
      e.target.reset();
      toast("Rental created ✓");
      await refresh();
    } catch (err) { toast(err.message, "error"); }
  });

  $("#fleetFilter").addEventListener("change", refresh);
  $("#rentalFilter").addEventListener("change", refresh);

  $("#carSearch").addEventListener("input", (e) => {
    state.carSearch = e.target.value;
    renderCars();
  });

  $("#rentalSearch").addEventListener("input", (e) => {
    state.rentalSearch = e.target.value;
    renderRentals();
  });

  $("#refreshMetrics").addEventListener("click", loadMetrics);
}

function setDefaultDates() {
  const today = new Date();
  const tomorrow = new Date(today);
  tomorrow.setDate(today.getDate() + 1);
  const fmt = (d) => d.toISOString().slice(0, 10);
  document.querySelector("[name='start_date']").value = fmt(today);
  document.querySelector("[name='end_date']").value = fmt(tomorrow);
}

bindAll();
setDefaultDates();
refresh().catch((err) => toast(err.message, "error"));
loadMetrics();
