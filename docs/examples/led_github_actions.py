from gpiozero import LED
from gpiozero.tools import negated
from signal import pause
import json
from urllib.request import urlopen

def build_passed(repo, workflow, branch='main'):
    url = (f'https://api.github.com/repos/{repo}/actions/workflows/{workflow}'
           f'/runs?branch={branch}&status=completed&per_page=1')
    while True:
        try:
            with urlopen(url) as response:
                runs = json.load(response)['workflow_runs']
            yield bool(runs) and runs[0]['conclusion'] == 'success'
        except OSError:
            yield False

red = LED(12)
green = LED(16)

green.source = build_passed('gpiozero/gpiozero', 'test.yml')
green.source_delay = 60 * 5  # check every 5 minutes
red.source = negated(green)

pause()
