import { useEffect, useState } from "react";

function PredictionComponent() {
  const [prediction, setPrediction] = useState(null);

  useEffect(() => {
    const fetchAndPredict = async () => {
      try {
        // Step 1: Get live flow features from Flask (which internally fetches Prometheus)
        const featureRes = await fetch("http://localhost:8000/live_features");
        const features = await featureRes.json();

        // Step 2: Send to /predict
        const predRes = await fetch("http://localhost:8000/predict", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(features),
        });
        const result = await predRes.json();
        setPrediction(result);
        console.log("Prediction:", result);
      } catch (err) {
        console.error("Error in prediction:", err);
      }
    };

    // Run once on mount
    fetchAndPredict();

    // Optional: refresh every 10 seconds
    const interval = setInterval(fetchAndPredict, 10000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div>
      {prediction ? (
        <p>Prediction: {prediction.label} ({prediction.probability}%)</p>
      ) : (
        <p>Fetching prediction...</p>
      )}
    </div>
  );
}

export default PredictionComponent;
