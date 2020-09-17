import yaml
import urllib3

from baac.lotto import Checker

if __name__ == "__main__":
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    checker = Checker()

    print(checker.recent_result_date())

    # Get recent lotto result
    with open('lotto.yml') as yaml_content:
        conf = yaml.safe_load(yaml_content)

        for lotto in conf['lottos']:
            result = checker.check_recent(lotto)
            print(result)