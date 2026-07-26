from pathlib import Path
import joblib
p = Path('trained_models/baseline_profile.pkl')
print('exists', p.exists())
if p.exists():
    print('size', p.stat().st_size)
    try:
        obj = joblib.load(p)
        print('type', type(obj))
        if hasattr(obj, 'keys'):
            print('keys', list(obj.keys())[:20])
        elif hasattr(obj, 'head'):
            print(obj.head())
        else:
            print(obj)
    except Exception as e:
        print('load_error', type(e).__name__, e)
