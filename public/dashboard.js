const SVG = "http://www.w3.org/2000/svg";

function el(name, attrs = {}, text) {
  const node = document.createElementNS(SVG, name);
  for (const [k, v] of Object.entries(attrs)) node.setAttribute(k, v);
  if (text !== undefined) node.textContent = text;
  return node;
}

// Simple bar chart. horizontal=true draws bars left-to-right (used for long question labels).
function barChart({ items, max, horizontal = false, format = (v) => v }) {
  const W = 480, H = horizontal ? 40 + items.length * 44 : 260;
  const svg = el("svg", { viewBox: `0 0 ${W} ${H}`, role: "img", class: "bar-chart" });
  const scaleMax = max ?? Math.max(1, ...items.map((i) => i.value));
  if (horizontal) {
    const left = 110, right = 50, plotW = W - left - right;
    items.forEach((item, i) => {
      const y = 20 + i * 44, w = (item.value / scaleMax) * plotW;
      svg.append(el("text", { x: left - 10, y: y + 18, "text-anchor": "end", class: "label" }, item.label));
      svg.append(el("rect", { x: left, y, width: plotW, height: 26, rx: 4, class: "track" }));
      const bar = el("rect", { x: left, y, width: Math.max(w, 2), height: 26, rx: 4, class: "bar" });
      bar.append(el("title", {}, `${item.title ?? item.label}: ${format(item.value)}`));
      svg.append(bar);
      svg.append(el("text", { x: left + w + 8, y: y + 18, class: "value" }, format(item.value)));
    });
  } else {
    const top = 24, bottom = 40, plotH = H - top - bottom, slot = (W - 20) / items.length, bw = Math.min(56, slot * 0.6);
    svg.append(el("line", { x1: 10, x2: W - 10, y1: top + plotH, y2: top + plotH, class: "axis" }));
    items.forEach((item, i) => {
      const h = (item.value / scaleMax) * plotH, x = 10 + slot * i + (slot - bw) / 2;
      const bar = el("rect", { x, y: top + plotH - h, width: bw, height: Math.max(h, 1), rx: 4, class: "bar" });
      bar.append(el("title", {}, `${item.title ?? item.label}: ${format(item.value)}`));
      svg.append(bar);
      svg.append(el("text", { x: x + bw / 2, y: top + plotH - h - 6, "text-anchor": "middle", class: "value" }, format(item.value)));
      const label = item.label.length > 16 ? item.label.slice(0, 15) + "…" : item.label;
      svg.append(el("text", { x: x + bw / 2, y: H - 16, "text-anchor": "middle", class: "label" }, label));
    });
  }
  return svg;
}

function chartCard(title, caption, svg) {
  const card = document.createElement("article");
  card.className = "chart";
  const h = document.createElement("h3");
  h.textContent = title;
  svg.setAttribute("aria-label", title);
  const p = document.createElement("p");
  p.textContent = caption;
  card.append(h, svg, p);
  return card;
}

function fillTable(id, rows, labelKey, emptyText) {
  const body = document.getElementById(id);
  body.replaceChildren();
  if (!rows.length) {
    body.innerHTML = `<tr><td colspan="3">${emptyText}</td></tr>`;
    return;
  }
  for (const row of rows) {
    const tr = document.createElement("tr");
    const [a, b, c] = [document.createElement("td"), document.createElement("td"), document.createElement("td")];
    a.textContent = row[labelKey];
    const strong = document.createElement("strong");
    strong.textContent = row.mean.toFixed(2);
    b.append(strong);
    c.textContent = row.count;
    tr.append(a, b, c);
    body.append(tr);
  }
}

fetch("/api/summary")
  .then((res) => (res.ok ? res.json() : Promise.reject(res)))
  .then((s) => {
    document.getElementById("m-total").textContent = s.total_valid_ratings;
    document.getElementById("m-courses").textContent = s.course_summary.length;
    document.getElementById("m-questions").textContent = s.question_summary.length;
    document.querySelectorAll(".minimum").forEach((n) => (n.textContent = s.minimum_group_size));

    const cards = [];
    if (s.rating_distribution.length) {
      cards.push(chartCard("Overall rating distribution", "Counts of ratings from 1 (low) to 5 (high).",
        barChart({ items: s.rating_distribution.map((d) => ({ label: String(d.rating), title: `Rating ${d.rating}`, value: d.count })) })));
    }
    if (s.course_summary.length) {
      cards.push(chartCard("Average rating by course", "Average rating by course (1–5); small groups are suppressed.",
        barChart({ items: s.course_summary.map((c) => ({ label: c.course_name, value: c.mean })), max: 5, format: (v) => v.toFixed(2) })));
    }
    if (s.question_summary.length) {
      cards.push(chartCard("Average rating by question", "Average rating by feedback question (1–5).",
        barChart({ items: s.question_summary.map((q) => ({ label: `Question ${q.question_id}`, title: q.question_text, value: q.mean })), max: 5, horizontal: true, format: (v) => v.toFixed(2) })));
    }
    const charts = document.getElementById("charts");
    if (cards.length) {
      charts.className = "charts";
      charts.append(...cards);
    } else {
      charts.innerHTML = '<div class="empty"><h3>Not enough data to chart yet</h3><p>Submit feedback to see results. Reports suppress small groups.</p></div>';
    }

    fillTable("course-rows", s.course_summary, "course_name", "No course groups meet the privacy threshold.");
    fillTable("question-rows", s.question_summary, "question_text", "No question groups meet the privacy threshold.");
  })
  .catch(() => {
    const div = document.createElement("div");
    div.className = "alert error";
    div.textContent = "Unable to load reports right now. Please try again shortly.";
    document.getElementById("alerts").append(div);
    for (const id of ["course-rows", "question-rows"]) document.getElementById(id).innerHTML = '<tr><td colspan="3">Reports unavailable.</td></tr>';
  });
