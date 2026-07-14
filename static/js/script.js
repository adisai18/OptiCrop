/* =========================================================
   OptiCrop - script.js
   Handles form submissions, AJAX calls and dynamic UI updates
   ========================================================= */

// ---------------------------------------------------------
// Utility helpers
// ---------------------------------------------------------
function showElement(el) {
  if (el) el.classList.add("show");
}

function hideElement(el) {
  if (el) el.classList.remove("show");
}

function setButtonLoading(button, spinner, isLoading) {
  if (!button) return;
  button.disabled = isLoading;
  if (spinner) {
    isLoading ? showElement(spinner) : hideElement(spinner);
  }
}

async function postJSON(url, payload) {
  const response = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.error || "Something went wrong. Please try again.");
  }
  return data;
}

// ---------------------------------------------------------
// Crop Recommendation Form
// ---------------------------------------------------------
function initCropForm() {
  const form = document.getElementById("crop-form");
  if (!form) return;

  const resultBox = document.getElementById("crop-result");
  const errorBox = document.getElementById("crop-error");
  const submitBtn = document.getElementById("crop-submit-btn");
  const spinner = document.getElementById("crop-spinner");

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    hideElement(errorBox);
    hideElement(resultBox);

    const payload = {
      N: form.N.value,
      P: form.P.value,
      K: form.K.value,
      temperature: form.temperature.value,
      humidity: form.humidity.value,
      ph: form.ph.value,
      rainfall: form.rainfall.value,
    };

    setButtonLoading(submitBtn, spinner, true);

    try {
      const data = await postJSON("/api/predict-crop", payload);

      document.getElementById("result-crop-name").textContent = data.recommended_crop;
      document.getElementById("result-confidence").textContent = data.confidence + "% confidence";

      if (data.estimated_yield_tonnes_per_ha !== null && data.estimated_yield_tonnes_per_ha !== undefined) {
        document.getElementById("result-yield").textContent =
          "Estimated yield: ~" + data.estimated_yield_tonnes_per_ha + " tonnes/hectare";
      } else {
        document.getElementById("result-yield").textContent = "";
      }

      const altList = document.getElementById("result-alternatives");
      altList.innerHTML = "";
      data.top_crops.forEach((item) => {
        const li = document.createElement("li");
        li.className = "list-group-item d-flex justify-content-between align-items-center";
        li.innerHTML = `<span class="text-capitalize">${item.crop}</span>
                        <span class="badge bg-success rounded-pill">${item.confidence}%</span>`;
        altList.appendChild(li);
      });

      showElement(resultBox);
      resultBox.scrollIntoView({ behavior: "smooth", block: "center" });
    } catch (err) {
      errorBox.textContent = err.message;
      showElement(errorBox);
    } finally {
      setButtonLoading(submitBtn, spinner, false);
    }
  });
}

// ---------------------------------------------------------
// Fertilizer Recommendation Form
// ---------------------------------------------------------
function initFertilizerForm() {
  const form = document.getElementById("fertilizer-form");
  if (!form) return;

  const resultBox = document.getElementById("fertilizer-result");
  const errorBox = document.getElementById("fertilizer-error");
  const submitBtn = document.getElementById("fertilizer-submit-btn");
  const spinner = document.getElementById("fertilizer-spinner");

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    hideElement(errorBox);
    hideElement(resultBox);

    const payload = {
      crop: form.crop.value,
      N: form.N.value,
      P: form.P.value,
      K: form.K.value,
    };

    setButtonLoading(submitBtn, spinner, true);

    try {
      const data = await postJSON("/api/recommend-fertilizer", payload);

      document.getElementById("fert-name").textContent = data.name;
      document.getElementById("fert-advice").textContent = data.advice;
      document.getElementById("fert-crop").textContent = data.crop;

      const idealTable = document.getElementById("fert-ideal-table");
      idealTable.innerHTML = `
        <tr><th>Nutrient</th><th>Your Value</th><th>Ideal Value</th></tr>
        <tr><td>Nitrogen (N)</td><td>${data.input_npk.N}</td><td>${data.ideal_npk.N}</td></tr>
        <tr><td>Phosphorus (P)</td><td>${data.input_npk.P}</td><td>${data.ideal_npk.P}</td></tr>
        <tr><td>Potassium (K)</td><td>${data.input_npk.K}</td><td>${data.ideal_npk.K}</td></tr>
      `;

      showElement(resultBox);
      resultBox.scrollIntoView({ behavior: "smooth", block: "center" });
    } catch (err) {
      errorBox.textContent = err.message;
      showElement(errorBox);
    } finally {
      setButtonLoading(submitBtn, spinner, false);
    }
  });
}

// ---------------------------------------------------------
// Weather Widget (used on Home page)
// ---------------------------------------------------------
function initWeatherWidget() {
  const form = document.getElementById("weather-form");
  if (!form) return;

  const resultBox = document.getElementById("weather-result");
  const errorBox = document.getElementById("weather-error");
  const submitBtn = document.getElementById("weather-submit-btn");
  const spinner = document.getElementById("weather-spinner");

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    hideElement(errorBox);
    hideElement(resultBox);

    const city = form.city.value.trim();
    if (!city) return;

    setButtonLoading(submitBtn, spinner, true);

    try {
      const response = await fetch(`/api/weather?city=${encodeURIComponent(city)}`);
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || "Could not fetch weather data.");
      }

      document.getElementById("weather-city").textContent = data.city;
      document.getElementById("weather-temp").textContent = data.temperature + "°C";
      document.getElementById("weather-humidity").textContent = data.humidity + "%";
      document.getElementById("weather-condition").textContent = data.condition;
      document.getElementById("weather-rainfall").textContent = data.rainfall + " mm";

      showElement(resultBox);
    } catch (err) {
      errorBox.textContent = err.message;
      showElement(errorBox);
    } finally {
      setButtonLoading(submitBtn, spinner, false);
    }
  });
}

// ---------------------------------------------------------
// Init on page load
// ---------------------------------------------------------
document.addEventListener("DOMContentLoaded", () => {
  initCropForm();
  initFertilizerForm();
  initWeatherWidget();
});
