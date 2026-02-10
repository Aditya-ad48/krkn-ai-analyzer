from typing import List, Dict, Any, Tuple
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

class AnomalyDetector:
    """ML-based anomaly detection for chaos experiments"""
    
    def __init__(self, contamination: float = 0.1):
        self.contamination = contamination
        self.scaler = StandardScaler()
    
    def detect_fitness_anomalies(self, fitness_scores: List[float], generations: List[int]) -> Dict[str, Any]:
        """Detect unusual fitness drops using Isolation Forest"""
        if len(fitness_scores) < 3:
            return {"anomalies": [], "warning": "Insufficient data"}
        
        # Prepare features: fitness score + generation trend
        X = np.array([[gen, score] for gen, score in zip(generations, fitness_scores)])
        X_scaled = self.scaler.fit_transform(X)
        
        # Detect anomalies
        clf = IsolationForest(contamination=self.contamination, random_state=42)
        predictions = clf.fit_predict(X_scaled)
        
        # Extract anomalous indices
        anomaly_indices = [i for i, pred in enumerate(predictions) if pred == -1]
        
        return {
            "anomaly_indices": anomaly_indices,
            "anomaly_count": len(anomaly_indices),
            "anomalous_scores": [fitness_scores[i] for i in anomaly_indices],
            "anomalous_generations": [generations[i] for i in anomaly_indices]
        }
    
    def detect_cascade_failures(self, health_events: List[Dict]) -> Dict[str, Any]:
        """Identify temporal correlation in service failures"""
        from collections import defaultdict
        import pandas as pd
        
        if not health_events:
            return {"cascades": [], "correlation_matrix": None}
        
        # Convert to DataFrame
        df = pd.DataFrame(health_events)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['failed'] = df['status_code'] >= 400
        
        # Time-window based correlation (30-second windows)
        df['time_bucket'] = df['timestamp'].dt.floor('30s')
        
        # Find concurrent failures
        cascades = []
        for bucket, group in df[df['failed']].groupby('time_bucket'):
            services = group['service'].unique().tolist()
            if len(services) > 1:  # Multiple services failed together
                cascades.append({
                    "timestamp": str(bucket),
                    "services": services,
                    "count": len(services)
                })
        
        # Build correlation matrix
        pivot = df.pivot_table(
            index='time_bucket', 
            columns='service', 
            values='failed', 
            aggfunc='max',
            fill_value=0
        )
        
        correlation_matrix = pivot.corr().to_dict() if len(pivot.columns) > 1 else {}
        
        return {
            "cascades": cascades,
            "correlation_matrix": correlation_matrix,
            "total_cascade_events": len(cascades)
        }
    
    def detect_recovery_slowness(self, health_events: List[Dict], threshold_seconds: float = 60.0) -> List[Dict]:
        """Identify services with slow recovery times"""
        import pandas as pd
        
        if not health_events:
            return []
        
        df = pd.DataFrame(health_events)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['failed'] = df['status_code'] >= 400
        
        slow_recoveries = []
        
        for service, group in df.groupby('service'):
            group = group.sort_values('timestamp')
            
            # Find failure windows
            in_failure = False
            failure_start = None
            
            for idx, row in group.iterrows():
                if row['failed'] and not in_failure:
                    # Failure starts
                    in_failure = True
                    failure_start = row['timestamp']
                elif not row['failed'] and in_failure:
                    # Recovery detected
                    recovery_time = (row['timestamp'] - failure_start).total_seconds()
                    if recovery_time > threshold_seconds:
                        slow_recoveries.append({
                            "service": service,
                            "failure_start": str(failure_start),
                            "recovery_time_seconds": recovery_time,
                            "severity": "critical" if recovery_time > 120 else "warning"
                        })
                    in_failure = False
        
        return slow_recoveries