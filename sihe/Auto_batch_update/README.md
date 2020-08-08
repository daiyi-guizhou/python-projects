# Install

```bash
pip install -r requirements.txt
```

# Usage (demo)
```
python demo.py
```

auto_push_deb　的 测试 tag
        'flaw_checker': 'test-flawck',
        'detection-machine-daemon': 'test-daemon',
        'falcon_agent': 'test-falcon',
        'peripheral-daemon': 'test-peripheral',

##  push 测试包：　python3 auto_push_deb.py --deb 包名.deb --env prod --tag test-flawck-S6-jys

##  push 正式包：　python3 auto_push_deb.py --deb 包名.deb --env prod 

##  --dry-run  演习模式，打印信息，　并不推包．
