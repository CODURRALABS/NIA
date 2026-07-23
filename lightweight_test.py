import os
os.environ['NVIDIA_API_KEY'] = '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'
os.environ['SILICONFLOW_API_KEY'] = 'sk-czjtsuwsfobuuufxnanccacmmbvipaoiewsmkhztyzfmfddr'
os.environ['IFLOW_API_KEY'] = 'sk-99bce03d1533c3522d0f5990c856230b'

import sys
sys.path.insert(0, 'core/pulse/runtime')

print('Python path:', sys.path)
print('NIA lightweight boot complete')

from model_router import ModelRouter
router = ModelRouter()
router.initialize()
result = router.generate('Say hi')
print('Result:', result)