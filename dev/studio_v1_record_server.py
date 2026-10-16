"""Record the verified measurement listener for safe, specific shutdown."""
import json
from studio_v1_measure import identity, ROOT
record=identity()
(ROOT/'tmp/v1-definitive-server-current.json').write_text(json.dumps(record,indent=2),encoding='utf-8')
print(json.dumps(record))
