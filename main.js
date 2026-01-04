fetch("http://localhost:8000/predict", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    feature1: 1.0,
    feature2: 0.5,
    // add all features required
  }),
})
  .then(res => res.json())
  .then(data => console.log("Prediction:", data))
  .catch(err => console.error(err));
