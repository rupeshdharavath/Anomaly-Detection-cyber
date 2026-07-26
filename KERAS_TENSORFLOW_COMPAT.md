# Keras/TensorFlow Version Compatibility

## Issue
`app/backend/requirements.txt` had conflicting pins:
```
tensorflow>=2.13.0
keras==2.14.0
```

This could cause install failures because:
- TensorFlow 2.13 bundles Keras 2.13 internally
- TensorFlow 2.14 bundles Keras 2.14+ internally
- Explicitly pinning `keras==2.14.0` independently may conflict with TensorFlow's bundled version

## Solution
Updated to:
```
tensorflow>=2.14.0
# Keras 2.14+ is bundled with TensorFlow 2.14+
```

**Reason**: Let TensorFlow manage its own Keras version. TensorFlow 2.14+ includes Keras 2.14+ natively, so no separate pin is needed.

## Verification Steps

**Before Fresh Install**
```bash
# Clean existing installation
pip uninstall tensorflow keras -y
pip cache purge
```

**Fresh Install**
```bash
cd app/backend
pip install -r requirements.txt
```

**Verify Compatibility**
```python
import tensorflow as tf
print(f"TensorFlow: {tf.__version__}")

import keras
print(f"Keras: {keras.__version__}")
# Should be 2.14+ if TensorFlow is 2.14+
```

**Test LSTM Loading**
```bash
python -c "
import keras
model = keras.models.load_model('../../trained_models/lstm_model.keras')
print(f'✅ Model loaded successfully')
print(f'Model input shape: {model.input_shape}')
"
```

## Affected Files
- ✅ `app/backend/requirements.txt` - Updated TensorFlow pin to >= 2.14.0, removed keras==2.14.0

## Why This Matters
If a fresh environment fails to install with the original pin conflict, the demo would break before judges even saw the system. This fix ensures a clean installation path.
