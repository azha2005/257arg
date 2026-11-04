"""Registra la revisión de Hallmark sin tocar el registro de otros visores."""
from pathlib import Path
import subprocess
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
if __name__=='__main__':
 subprocess.run(['node',str(ROOT/'.claude/skills/hallmark/scripts/theme.mjs'),'log',
  '--entry',(HERE/'.hallmark/finish.json').read_text(encoding='utf8'),
  '--log',str(HERE/'.hallmark/log.json')],check=True)
