from pathlib import Path
import subprocess
import sys
HERE = Path(__file__).resolve().parent
PAIRS = [('1989p','1995p'),('1989d','1994c'),('1985d','1987d')]
PAIRS += [('1983p','1989p'),('1987d','1989p'),('1985d','1989p')]
PAIRS += [('1989p','1997d')]
PAIRS += [('1995p','1997d'),('1995p','1999p'),('1983p','1985d')]
if __name__ == '__main__':
    for a,b in (PAIRS[-3:] if '--tanda95' in sys.argv else PAIRS[6:7] if '--1997' in sys.argv else PAIRS[3:6] if '--ultimos' in sys.argv else PAIRS):
        with (HERE/f'log_{a}_{b}.txt').open('w',encoding='utf8') as log:
            subprocess.run([sys.executable,'-X','utf8',str(HERE/'estimar.py'),a,b],stdout=log,stderr=subprocess.STDOUT,check=True)
        print(a,b,'OK',flush=True)
