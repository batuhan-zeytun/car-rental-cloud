const state = {
  allCars: [],
  cars: [],
  customers: [],
  rentals: []
};

const $ = (selector) => document.querySelector(selector);

const money = (value) =>
  new Intl.NumberFormat("tr-TR", {
    style: "currency",
    currency: "TRY",
    maximumFractionDigits: 0
  }).format(value || 0);

function toast(message, type = "ok") {
  const node = $("#toast");
  node.textContent = message;
  node.className = `toast show ${type}`;
  window.setTimeout(() => {
    node.className = "toast";
  }, 2800);
}

async function api(path, options = {}) {
  const response = await fetch(path, {
    headers: { "Content-Type": "application/json" },
    ...options
  });
  const contentType = response.headers.get("content-type") || "";
  const body = contentType.includes("application/json")
    ? await response.json()
    : await response.text();
  if (!response.ok) {
    throw new Error(body.error || body || "Request failed");
  }
  return body;
}

function formPayload(form) {
  return Object.fromEntries(new FormData(form).entries());
}

function statusBadge(status) {
  return `<span class="badge ${status}">${status}</span>`;
}

function updateStats() {
  const available = state.allCars.filter((car) => car.status === "available").length;
  const activeRentals = state.rentals.filter((rental) => rental.status === "active");
  const revenue = state.rentals
    .filter((rental) => rental.status !== "cancelled")
    .reduce((sum, rental) => sum + rental.total_price, 0);

  $("#availableCount").textContent = available;
  $("#activeRentalCount").textContent = activeRentals.length;
  $("#revenueTotal").textContent = money(revenue);
}

function renderCars() {
  const list = $("#carList");
  if (!state.cars.length) {
    list.innerHTML = `<li class="empty">No cars match this filter.</li>`;
    return;
  }

  list.innerHTML = state.cars
    .map(
      (car) => `
        <li class="fleet-row">
          <div>
            <strong>${car.make} ${car.model}</strong>
            <span>${car.year} · ${car.plate_number}</span>
            <small>${car.location} · ${money(car.daily_rate)} / day</small>
          </div>
          <div class="row-actions">
            ${statusBadge(car.status)}
            <select data-car-status="${car.id}" aria-label="Change status for ${car.plate_number}">
              <option value="available" ${car.status === "available" ? "selected" : ""}>Available</option>
              <option value="rented" ${car.status === "rented" ? "selected" : ""}>Rented</option>
              <option value="maintenance" ${car.status === "maintenance" ? "selected" : ""}>Maintenance</option>
            </select>
          </div>
        </li>
      `
    )
    .join("");

  document.querySelectorAll("[data-car-status]").forEach((select) => {
    select.addEventListener("change", async (event) => {
      try {
        await api(`/api/cars/${event.target.dataset.carStatus}/status`, {
          method: "PATCH",
          body: JSON.stringify({ status: event.target.value })
        });
        toast("Car status updated");
        await refresh();
      } catch (error) {
        toast(error.message, "error");
      }
    });
  });
}

function renderRentalOptions() {
  const cars = state.allCars.filter((car) => car.status === "available");
  $("#rentalCar").innerHTML = cars
    .map((car) => `<option value="${car.id}">${car.plate_number} · ${car.make} ${car.model}</option>`)
    .join("");
  $("#rentalCustomer").innerHTML = state.customers
    .map((customer) => `<option value="${customer.id}">${customer.full_name}</option>`)
    .join("");
}

function renderRentals() {
  const rows = $("#rentalRows");
  if (!state.rentals.length) {
    rows.innerHTML = `<tr><td colspan="6" class="empty">No rentals yet.</td></tr>`;
    return;
  }

  rows.innerHTML = state.rentals
    .map(
      (rental) => `
        <tr>
          <td>${rental.car.plate_number}<br><small>${rental.car.make} ${rental.car.model}</small></td>
          <td>${rental.customer.full_name}<br><small>${rental.customer.email}</small></td>
          <td>${rental.start_date} to ${rental.end_date}<br><small>${rental.days} day(s)</small></td>
          <td>${money(rental.total_price)}</td>
          <td>${statusBadge(rental.status)}</td>
          <td>
            ${
              rental.status === "active"
                ? `<button class="ghost" data-return="${rental.id}">Return</button>`
                : ""
            }
          </td>
        </tr>
      `
    )
    .join("");

  document.querySelectorAll("[data-return]").forEach((button) => {
    button.addEventListener("click", async (event) => {
      try {
        await api(`/api/rentals/${event.target.dataset.return}/return`, { method: "POST" });
        toast("Rental returned");
        await refresh();
      } catch (error) {
        toast(error.message, "error");
      }
    });
  });
}

async function loadReadiness() {
  try {
    await api("/readyz");
    $("#readyDot").className = "dot ok";
    $("#readyText").textContent = "ready";
  } catch (error) {
    $("#readyDot").className = "dot error";
    $("#readyText").textContent = "not ready";
  }
}

async function loadCars() {
  const filter = $("#fleetFilter").value;
  const payload = await api(`/api/cars${filter ? `?status=${filter}` : ""}`);
  state.cars = payload.items;
}

async function loadAllCarsForSelectors() {
  const payload = await api("/api/cars");
  state.allCars = payload.items;
}

async function loadCustomers() {
  const payload = await api("/api/customers");
  state.customers = payload.items;
}

async function loadRentals() {
  const filter = $("#rentalFilter").value;
  const payload = await api(`/api/rentals${filter ? `?status=${filter}` : ""}`);
  state.rentals = payload.items;
}

async function refresh() {
  await loadReadiness();
  await loadAllCarsForSelectors();
  await loadCustomers();
  renderRentalOptions();
  await loadCars();
  await loadRentals();
  renderCars();
  renderRentals();
  updateStats();
}

function bindForms() {
  $("#carForm").addEventListener("submit", async (event) => {
    event.preventDefault();
    try {
      await api("/api/cars", {
        method: "POST",
        body: JSON.stringify(formPayload(event.target))
      });
      event.target.reset();
      toast("Car saved");
      await refresh();
    } catch (error) {
      toast(error.message, "error");
    }
  });

  $("#customerForm").addEventListener("submit", async (event) => {
    event.preventDefault();
    try {
      await api("/api/customers", {
        method: "POST",
        body: JSON.stringify(formPayload(event.target))
      });
      event.target.reset();
      toast("Customer saved");
      await refresh();
    } catch (error) {
      toast(error.message, "error");
    }
  });

  $("#rentalForm").addEventListener("submit", async (event) => {
    event.preventDefault();
    try {
      await api("/api/rentals", {
        method: "POST",
        body: JSON.stringify(formPayload(event.target))
      });
      event.target.reset();
      toast("Rental created");
      await refresh();
    } catch (error) {
      toast(error.message, "error");
    }
  });

  $("#fleetFilter").addEventListener("change", refresh);
  $("#rentalFilter").addEventListener("change", refresh);
}

function setDefaultDates() {
  const today = new Date();
  const tomorrow = new Date(today);
  tomorrow.setDate(today.getDate() + 1);
  const format = (value) => value.toISOString().slice(0, 10);
  document.querySelector("[name='start_date']").value = format(today);
  document.querySelector("[name='end_date']").value = format(tomorrow);
}

bindForms();
setDefaultDates();
refresh().catch((error) => toast(error.message, "error"));
