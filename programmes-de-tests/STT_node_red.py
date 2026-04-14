import json 
import time
import sys

texte = sys.stdin.readline()

time.sleep(2)
res = [texte]

sys.stdout.write(json.dumps(res))