from flask import Flask, render_template, request

app = Flask(__name__)

def compute_bmi_details(weight_input, height_input, height_unit="cm", weight_unit="kg"):
    # Convert weight to kg
    weight_kg = float(weight_input)
    if weight_unit == "lbs":
        weight_kg = weight_kg * 0.45359237

    # Convert height to meters
    raw_height = float(height_input)
    if height_unit == "m":
        # If user entered something like 175 while unit is 'm', auto-correct
        if raw_height > 3.0:
            height_m = raw_height / 100.0
        else:
            height_m = raw_height
    else:  # 'cm'
        # If user entered something like 1.75 while unit is 'cm', auto-correct
        if raw_height < 3.0 and raw_height > 0:
            height_m = raw_height
        else:
            height_m = raw_height / 100.0

    if height_m <= 0.4 or height_m > 2.8 or weight_kg <= 2 or weight_kg > 400:
        raise ValueError("Measurements out of realistic human range")

    bmi = round(weight_kg / (height_m ** 2), 1)

    # Categorization and color coding
    if bmi < 18.5:
        category = "Underweight"
        category_color = "sky"
        category_desc = "Below standard healthy body weight. Consider a nutrient-dense diet."
        badge_bg = "#0284c7"
    elif bmi < 25.0:
        category = "Normal Weight"
        category_color = "emerald"
        category_desc = "Optimal balance. Your weight is well-aligned with your height."
        badge_bg = "#059669"
    elif bmi < 30.0:
        category = "Overweight"
        category_color = "amber"
        category_desc = "Slightly elevated body mass. Regular activity and portion care recommended."
        badge_bg = "#d97706"
    else:
        category = "Obese"
        category_color = "rose"
        category_desc = "Higher risk zone. Consultation with a healthcare provider advised."
        badge_bg = "#e11d48"

    # Healthy weight range for this height (BMI 18.5 to 24.9)
    min_healthy_kg = round(18.5 * (height_m ** 2), 1)
    max_healthy_kg = round(24.9 * (height_m ** 2), 1)

    # Position on a visual scale (15 to 35 BMI range -> 0% to 100%)
    gauge_percent = max(0, min(100, round(((bmi - 15) / (35 - 15)) * 100, 1)))

    bmi_prime = round(bmi / 25.0, 2)

    return {
        "bmi": bmi,
        "category": category,
        "category_color": category_color,
        "category_desc": category_desc,
        "badge_bg": badge_bg,
        "gauge_percent": gauge_percent,
        "weight_kg": round(weight_kg, 1),
        "height_m": round(height_m, 2),
        "height_cm": round(height_m * 100, 1),
        "min_healthy_kg": min_healthy_kg,
        "max_healthy_kg": max_healthy_kg,
        "bmi_prime": bmi_prime,
        "raw_weight": weight_input,
        "raw_height": height_input,
        "height_unit": height_unit,
        "weight_unit": weight_unit
    }

@app.route("/", methods=["GET", "POST"])
def index():
    data = None
    error = None
    
    if request.method == "POST":
        try:
            w = request.form.get("weight", "").strip()
            h = request.form.get("height", "").strip()
            h_unit = request.form.get("height_unit", "cm").strip()
            w_unit = request.form.get("weight_unit", "kg").strip()
            
            data = compute_bmi_details(w, h, h_unit, w_unit)
        except (ValueError, KeyError, ZeroDivisionError) as e:
            error = "Please enter valid, realistic numbers for weight and height."

    # Backwards compatibility for templates or simple tests
    bmi_val = data["bmi"] if data else None
    category_val = data["category"] if data else None

    return render_template(
        "index.html",
        data=data,
        error=error,
        bmi=bmi_val,
        category=category_val
    )

@app.route("/health")
def health():
    # Used by Kubernetes liveness/readiness probes
    return {"status": "ok"}, 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
