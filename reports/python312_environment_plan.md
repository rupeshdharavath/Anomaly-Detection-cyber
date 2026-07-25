# Python 3.12 Environment Plan for a Real LSTM/GRU Model

## Goal
Use a Python 3.12 environment that supports TensorFlow so the project can replace the current sequence-aware XGBoost approximation with a true LSTM/GRU model.

## Why Python 3.12
- The current workspace interpreter is Python 3.13/3.14, which is not a good target for TensorFlow in this environment.
- Python 3.12 is available on this machine through Anaconda.
- TensorFlow wheels and supporting packages are more likely to install cleanly on Python 3.12.

## Target environment
- Interpreter: `C:\Users\umesh\anaconda3\python.exe`
- Recommended environment name: `anomaly-lstm`
- Project root: `D:\Anomaly-Detection`

## Setup steps
1. Create the environment.
   - `conda create -n anomaly-lstm python=3.12 -y`
2. Activate it.
   - `conda activate anomaly-lstm`
3. Install the core packages.
   - `pip install tensorflow pandas numpy scikit-learn joblib matplotlib shap xgboost`
4. Verify TensorFlow imports correctly.
   - `python -c "import tensorflow as tf; print(tf.__version__)"`
5. Point VS Code to the new interpreter.
   - Select the `anomaly-lstm` environment in the Python interpreter picker.
6. Reinstall notebook/kernel support if needed.
   - Ensure the notebook kernel uses Python 3.12, not 3.13/3.14.

## Implementation plan after environment switch
1. Build and maintain the real LSTM in `src/lstm_sequence_model.py` as the primary sequence model.
2. Build per-entity event sequences using rolling windows.
3. Encode categorical fields and pad sequences to a fixed length.
4. Train an LSTM or GRU classifier for attack vs normal detection.
5. Keep the current SHAP and dashboard layers on top of the new detector where possible.
6. Re-run evaluation with class imbalance metrics and alert-budget analysis.

## Validation checklist
- TensorFlow imports without error.
- The model trains on the processed sequence dataset.
- The detector produces attack probabilities for each event window.
- The report clearly states the architecture and the environment used.
