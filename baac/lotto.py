"""Checker

BAAC Lotto Checker Module.
"""
import re
import requests
from pyquery import PyQuery
from requests import exceptions

class Checker():
    """Checker

    BAAC Lotto Checker.
    """

    API_URL = 'https://www.baac.or.th/salak/content-lotto.php'

    @classmethod
    def recent_result_date(cls):
        """recent_result_date

        Check recent lotto announcement date.
        """
        result_date = ""
        try:
            headers = {'Accept-Charset': 'utf-8'}
            response = requests.get(Checker.API_URL, headers=headers, verify=False)
            if response.status_code == 200:
                html_text = str(response.content.decode('utf-8'))
                pyq = PyQuery(html_text)
                recent_lotto_announcement_date = pyq('select[name="lotto_date"] > option:first-child')
                result_date = recent_lotto_announcement_date.text()
            else:
                raise Exception('HTTP Error: {}'.format(response.status_code))
        except Exception as exception:
            return (False, exception)
        return (True, result_date)

    def check_recent(self, lotto_config):
        """check_recent

        Check recent lotto result.
        """
        result = []
        try:
            payload = {
                'lotto_group': lotto_config['group'],
                'start_no': lotto_config['begin'],
                'stop_no': lotto_config['end'],
                'inside': 5
            }
            headers = {'Accept-Charset': 'utf-8'}
            response = requests.get(Checker.API_URL, params=payload, headers=headers, verify=False)
            if response.status_code == 200:
                result = self._parse_lotto_result(str(response.content.decode('utf-8')))
                result['tags'] = list(map(lambda tag: tag.strip(), lotto_config['tags'].split(',')))
            else:
                raise Exception('HTTP Error: {}'.format(response.status_code))
        except Exception as exception:
            return (False, exception)
        return (True, result)

    @classmethod
    def _parse_lotto_result(cls, content):
        """_parse_lotto_result

        Parse lotto result from recent result and return them in JSON.
        """
        pyq = PyQuery(content)
        table_header = pyq('table:first-child > tr:first-child > td:first-child')
        match_result = re.search(r'ผลการออกรางวัลออมทรัพย์ ชุด (.+) ระหว่างเลข (\d+) ถึง (\d+)', table_header.text())
        group_name = match_result.group(1)
        lotto_range_begin = match_result.group(2)
        lotto_range_end = match_result.group(3)
        table_sub_header = pyq('table:first-child > tr:nth-child(2) > td:first-child')
        match_result = re.search(r'ออกรางวัลครั้งที่ (\d+) :: วันที่ (\d+) (.+) (\d+)', table_sub_header.text())
        result_sequence = match_result.group(1)
        result_date = match_result.group(2)
        result_month = match_result.group(3)
        result_year = match_result.group(4)
        table_rows = pyq('table:first-child')
        row_count = table_rows.children().length
        table_total_earn = pyq('table:first-child > tr:nth-child({}) > td:last-child'.format(row_count - 1))
        total_earn = table_total_earn.text()
        table_grand_total_earn = pyq('table:first-child > tr:last-child > td:last-child')
        grand_total_earn = table_grand_total_earn.text()
        rows = []
        for row_index in range(4, row_count - 1):
            table_result_prize = pyq('table:first-child > tr:nth-child({}) > td:first-child'.format(row_index))
            table_result_number = pyq('table:first-child > tr:nth-child({}) > td:nth-child(2)'.format(row_index))
            table_result_earn = pyq('table:first-child > tr:nth-child({}) > td:last-child'.format(row_index))
            rows.append({
                'prize': table_result_prize.text(),
                'number': table_result_number.text(),
                'earn': table_result_earn.text()
            })
        result = {
            'group_name': group_name,
            'date': '{d} {m} {y}'.format(d=result_date, m=result_month, y=result_year),
            'sequence': result_sequence,
            'range': {
                'from': lotto_range_begin,
                'to': lotto_range_end
            },
            'grand_total_earn': grand_total_earn,
            'total_earn': total_earn,
            'result': rows
        }
        return result
