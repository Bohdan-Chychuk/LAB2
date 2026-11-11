const $ = (id) => document.getElementById(id);
// Дані з сервера потрапляють у DOM лише через властивості та textContent — без HTML-рядків.
const el = (tag, props = {}, children = []) => {
  const node = Object.assign(document.createElement(tag), props);
  node.append(...children);
  return node;
};
let current = null;

async function api(url, options) {
  const response = await fetch(url, options);
  const body = await response.json().catch(() => ({}));
  if (!response.ok) throw Object.assign(new Error(body.detail || "Помилка запиту"), { status: response.status });
  return body;
}

const hhmm = (iso) => iso ? iso.slice(11, 16) : "";
const dayLabel = (iso) => {
  const d = new Date();
  const pad = (n) => String(n).padStart(2, "0");
  const today = `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`;
  return iso.slice(0, 10) === today ? "сьогодні" : "завтра";
};
const duration = (minutes) => {
  const h = Math.floor(minutes / 60), m = minutes % 60;
  return h ? `${h} год ${m} хв` : `${m} хв`;
};

$("street").addEventListener("input", async (event) => {
  const q = event.target.value.trim();
  if (q.length < 2) return;
  const streets = await api(`/streets?q=${encodeURIComponent(q)}`).catch(() => []);
  $("streets").replaceChildren(...streets.map((value) => el("option", { value })));
});

function renderSchedule(intervals) {
  const cell = (props) => el("td", props);
  const rows = intervals.length
    ? intervals.map((i) => el("tr", {}, [cell({ textContent: i.start }), cell({ textContent: i.end })]))
    : [el("tr", {}, [cell({ colSpan: 2, className: "empty", textContent: "Відключень не заплановано" })])];
  $("schedule").replaceChildren(...rows);
}

function renderStatus(s) {
  const on = s.planned === "on";
  const indicator = $("status-indicator");
  indicator.className = `indicator ${on ? "on" : "off"}`;
  indicator.textContent = on ? "Світло є" : "Світла немає";
  $("next-change").textContent = s.next_change
    ? `${on ? "Відключення" : "Увімкнення"} о ${hhmm(s.next_change)} (${dayLabel(s.next_change)})`
    : "Змін за графіком не очікується";
  $("next-outage").textContent = s.next_outage
    ? `Наступне відключення через ${duration(s.minutes_to_outage)}`
    : "Відключень не заплановано";
  $("actual").textContent = s.actual
    ? `Фактично за репортами сусідів: ${s.actual === "on" ? "світло є" : "світла немає"}`
    : "Фактичний стан: недостатньо репортів";
}

async function refreshStatus() {
  const params = new URLSearchParams(current);
  renderStatus(await api(`/status?${params}`));
}

$("address-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  $("error").textContent = "";
  const address = { street: $("street").value.trim(), house: $("house").value.trim() };
  try {
    const { queue, street, house } = await api(`/queue?${new URLSearchParams(address)}`);
    current = { street, house };
    $("queue").textContent = queue;
    const schedule = await api(`/schedule/${queue}`).catch(() => ({ intervals: [] }));
    renderSchedule(schedule.intervals);
    await refreshStatus();
    $("result").classList.remove("hidden");
  } catch (error) {
    $("result").classList.add("hidden");
    $("error").textContent = error.message;
  }
});

const userId = $("user-id");
try {
  userId.value = localStorage.getItem("svl-user-id") || `web-${Math.random().toString(36).slice(2, 8)}`;
} catch {
  userId.value = `web-${Math.random().toString(36).slice(2, 8)}`;
}

async function sendReport(event) {
  const status = event.currentTarget.dataset.status;
  const buttons = [$("btn-on"), $("btn-off")];
  buttons.forEach((b) => (b.disabled = true));
  try {
    try { localStorage.setItem("svl-user-id", userId.value); } catch {}
    await api("/reports", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ ...current, user_id: userId.value.trim(), status }),
    });
    $("report-message").textContent = `Дякуємо, ${userId.value}! Репорт «${status === "on" ? "світло є" : "світла немає"}» прийнято.`;
    await refreshStatus();
  } catch (error) {
    $("report-message").textContent = error.status === 429
      ? "Ви вже надсилали репорт для цієї адреси. Спробуйте за 10 хвилин."
      : error.message;
  } finally {
    buttons.forEach((b) => (b.disabled = false));
  }
}

$("btn-on").addEventListener("click", sendReport);
$("btn-off").addEventListener("click", sendReport);
