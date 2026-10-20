const messages = {
  success: ["success", "Thanks! Your anonymous feedback was submitted."],
  missing: ["error", "Choose a course and rate every question."],
  invalid: ["error", "Ratings must be 1–5 and comments must be at most 1,000 characters."],
  course: ["error", "Choose a valid course."],
  error: ["error", "Could not save feedback. Please try again in a moment."],
};

function showAlert(category, text) {
  const div = document.createElement("div");
  div.className = `alert ${category}`;
  div.textContent = text;
  document.getElementById("alerts").append(div);
}

const status = new URLSearchParams(location.search).get("status");
if (messages[status]) {
  showAlert(...messages[status]);
  history.replaceState(null, "", "/");
}

function renderQuestion(question, index) {
  const fieldset = document.createElement("fieldset");
  const legend = document.createElement("legend");
  const num = document.createElement("b");
  num.textContent = String(index + 1).padStart(2, "0");
  legend.append(num, " ", question.question_text);
  const ratings = document.createElement("div");
  ratings.className = "ratings";
  for (let r = 1; r <= 5; r++) {
    const label = document.createElement("label");
    label.innerHTML = `<input type="radio" name="rating_${question.question_id}" value="${r}" required><span>${r}</span>`;
    ratings.append(label);
  }
  const scale = document.createElement("div");
  scale.className = "scale";
  scale.innerHTML = "<span>Poor</span><span>Excellent</span>";
  fieldset.append(legend, ratings, scale);
  return fieldset;
}

fetch("/api/courses")
  .then((res) => (res.ok ? res.json() : Promise.reject(res)))
  .then(({ courses, questions }) => {
    const select = document.getElementById("course_id");
    for (const c of courses) select.add(new Option(c.course_name, c.course_id));
    document.getElementById("questions").append(...questions.map(renderQuestion));
    document.getElementById("loading").remove();
    document.getElementById("feedback-form").hidden = false;
  })
  .catch(() => {
    document.getElementById("loading").textContent = "The feedback form is temporarily unavailable. Please try again shortly.";
  });
