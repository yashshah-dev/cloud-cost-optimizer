from typing import List, Dict, Any, Optional
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import mean_absolute_error
from sklearn.preprocessing import StandardScaler
import joblib
from datetime import datetime, timedelta, timezone
import logging

logger = logging.getLogger(__name__)

class UsagePatternAnalyzer:
    """
    ML-powered usage pattern analyzer for cloud resources.
    Analyzes historical usage data to predict future patterns and detect anomalies.
    """

    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.feature_columns = [
            'hour_of_day', 'day_of_week', 'cpu_utilization',
            'memory_utilization', 'network_in', 'network_out',
            'rolling_avg_7d', 'rolling_std_7d', 'usage_trend'
        ]
        self.target_column = 'predicted_usage'

    def preprocess_data(self, usage_data: List[Dict[str, Any]]) -> pd.DataFrame:
        """
        Preprocess raw usage data into ML-ready features.

        Args:
            usage_data: List of usage records with timestamps and metrics

        Returns:
            DataFrame with engineered features
        """
        df = pd.DataFrame(usage_data)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.set_index('timestamp').sort_index()

        # Basic time features
        df['hour_of_day'] = df.index.hour
        df['day_of_week'] = df.index.dayofweek
        df['month'] = df.index.month

        # Rolling statistics
        df['rolling_avg_7d'] = df['cpu_utilization'].rolling(window='7D').mean()
        df['rolling_std_7d'] = df['cpu_utilization'].rolling(window='7D').std()
        df['rolling_avg_24h'] = df['cpu_utilization'].rolling(window='24h').mean()

        # Usage trend (slope over last 7 days)
        df['usage_trend'] = df['cpu_utilization'].rolling(window='7D').apply(
            lambda x: np.polyfit(range(len(x)), x, 1)[0] if len(x) > 1 else 0
        )

        # Fill NaN values
        df = df.bfill().ffill().fillna(0)

        return df

    def train_model(self, usage_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Train the usage pattern prediction model.

        Args:
            usage_data: Historical usage data

        Returns:
            Training metrics and model performance
        """
        try:
            df = self.preprocess_data(usage_data)

            if len(df) < 50:  # Minimum data requirement
                logger.warning("Insufficient data for training")
                return {"status": "insufficient_data", "samples": len(df)}

            # Prepare features and target
            X = df[self.feature_columns]
            y = df['cpu_utilization'].shift(-1).bfill().ffill()  # Predict next hour

            # Remove rows with NaN target
            valid_idx = ~y.isna()
            X = X[valid_idx]
            y = y[valid_idx]

            if len(X) < 20:
                return {"status": "insufficient_valid_data", "samples": len(X)}

            # Scale features
            X_scaled = self.scaler.fit_transform(X)

            # Time series cross-validation
            tscv = TimeSeriesSplit(n_splits=3)
            scores = []

            for train_idx, test_idx in tscv.split(X_scaled):
                X_train, X_test = X_scaled[train_idx], X_scaled[test_idx]
                y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]

                # Train model
                model = RandomForestRegressor(
                    n_estimators=100,
                    max_depth=10,
                    random_state=42,
                    n_jobs=-1
                )
                model.fit(X_train, y_train)

                # Evaluate
                y_pred = model.predict(X_test)
                mae = mean_absolute_error(y_test, y_pred)
                scores.append(mae)

            # Train final model on all data
            self.model = RandomForestRegressor(
                n_estimators=100,
                max_depth=10,
                random_state=42,
                n_jobs=-1
            )
            self.model.fit(X_scaled, y)

            return {
                "status": "trained",
                "mean_mae": np.mean(scores),
                "std_mae": np.std(scores),
                "samples": len(X),
                "features": len(self.feature_columns)
            }

        except Exception as e:
            logger.error(f"Error training usage pattern model: {e}")
            return {"status": "error", "error": str(e)}

    def predict_usage(self, current_data: Dict[str, Any], hours_ahead: int = 24) -> Dict[str, Any]:
        """
        Predict future usage patterns.

        Args:
            current_data: Current usage metrics
            hours_ahead: Hours to predict ahead

        Returns:
            Prediction results with confidence intervals
        """
        if self.model is None:
            return {"status": "model_not_trained"}

        try:
            # Create feature vector
            features = pd.DataFrame([current_data])
            features['timestamp'] = pd.to_datetime(features['timestamp'])
            features = features.set_index('timestamp')

            # Add time features
            features['hour_of_day'] = features.index.hour
            features['day_of_week'] = features.index.dayofweek

            # Add rolling features (use current values as proxy)
            features['rolling_avg_7d'] = features['cpu_utilization']
            features['rolling_std_7d'] = 0  # Simplified
            features['usage_trend'] = 0     # Simplified

            # Prepare for prediction
            X = features[self.feature_columns]
            X_scaled = self.scaler.transform(X)

            # Make prediction
            prediction = self.model.predict(X_scaled)[0]

            # Simple confidence interval (can be improved with quantile regression)
            confidence_interval = {
                "lower": max(0, prediction * 0.8),
                "upper": prediction * 1.2
            }

            return {
                "status": "success",
                "predicted_usage": prediction,
                "confidence_interval": confidence_interval,
                "hours_ahead": hours_ahead,
                "prediction_time": datetime.now(timezone.utc).isoformat()
            }

        except Exception as e:
            logger.error(f"Error predicting usage: {e}")
            return {"status": "error", "error": str(e)}

    def detect_anomalies(self, usage_data: List[Dict[str, Any]], threshold: float = 2.0) -> List[Dict[str, Any]]:
        """
        Detect anomalous usage patterns.

        Args:
            usage_data: Recent usage data
            threshold: Standard deviation threshold for anomaly detection

        Returns:
            List of detected anomalies
        """
        if not usage_data:
            return []

        try:
            df = self.preprocess_data(usage_data)

            # Calculate z-scores for CPU utilization
            mean_usage = df['cpu_utilization'].mean()
            std_usage = df['cpu_utilization'].std()

            if std_usage == 0:
                return []

            df['z_score'] = (df['cpu_utilization'] - mean_usage) / std_usage

            # Find anomalies
            anomalies = []
            for idx, row in df.iterrows():
                if abs(row['z_score']) > threshold:
                    anomalies.append({
                        "timestamp": idx.isoformat(),
                        "cpu_utilization": row['cpu_utilization'],
                        "z_score": row['z_score'],
                        "anomaly_type": "high_usage" if row['z_score'] > 0 else "low_usage",
                        "severity": "high" if abs(row['z_score']) > 3 else "medium"
                    })

            return anomalies

        except Exception as e:
            logger.error(f"Error detecting anomalies: {e}")
            return []

    def save_model(self, filepath: str) -> bool:
        """Save the trained model to disk."""
        if self.model is None:
            return False

        try:
            model_data = {
                'model': self.model,
                'scaler': self.scaler,
                'feature_columns': self.feature_columns,
                'trained_at': datetime.now(timezone.utc).isoformat()
            }
            joblib.dump(model_data, filepath)
            return True
        except Exception as e:
            logger.error(f"Error saving model: {e}")
            return False

    def load_model(self, filepath: str) -> bool:
        """Load a trained model from disk."""
        try:
            model_data = joblib.load(filepath)
            self.model = model_data['model']
            self.scaler = model_data['scaler']
            self.feature_columns = model_data['feature_columns']
            return True
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            return False
