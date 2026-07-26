Run the model build/train/eval notebook

1. Open JupyterLab or Jupyter Notebook on the machine that has Python 3.13 + TensorFlow installed.

2. From the repo root, you can launch JupyterLab and open the notebook with the provided launcher:

   scripts\open_run_all.bat

   This will start JupyterLab and open `notebooks/run_all_models.ipynb`.

3. In JupyterLab, select the kernel that corresponds to Python 3.13 (the kernel that has TensorFlow installed).

4. Run all cells in `notebooks/run_all_models.ipynb` in order. The notebook will:
   - Add the repo root to `sys.path` so `src` imports work.
   - Build baseline profiles.
   - Train the attack-type classifier (writes `trained_models/attack_type_classifier.pkl`).
   - Train the LSTM model if TensorFlow is available (writes `trained_models/lstm_model.keras`).
   - Run evaluation (writes `trained_models/evaluation_results.json`).

5. After the notebook completes, verify artifacts exist in `trained_models/` and then start the backend and frontend.

Notes:
- If TensorFlow is not installed in the selected kernel, the notebook will skip LSTM training and the backend will fall back to baseline + attack-type classifier.
- If you prefer to run commands manually from the terminal that has TF, use the commands in the project root as listed in the main README.