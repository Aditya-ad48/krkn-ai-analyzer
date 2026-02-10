import numpy as np
from sklearn.ensemble import IsolationForest

class ChaosAnomalyDetector:
    """
    Detects abnormal fitness drops or slow recovery behavior.
    """

    def detect_fitness_anomalies(self, fitness_scores):
        if len(fitness_scores) < 5:
            return []

        X = np.array(fitness_scores).reshape(-1, 1)
        model = IsolationForest(contamination=0.2, random_state=42)
        labels = model.fit_predict(X)

        return [
            {"index": i, "fitness": fitness_scores[i]}
            for i, l in enumerate(labels) if l == -1
        ]
