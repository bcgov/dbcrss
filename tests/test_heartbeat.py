import collections
import csv
import datetime
import os
import sys
import tempfile
import time

if sys.version_info > (3,):
    from io import StringIO
    from urllib.error import HTTPError, URLError
else:
    from StringIO import StringIO
    from urllib2 import HTTPError, URLError

import mock
import pytest

from heartbeat import heartbeat
from heartbeat.heartbeat import (
    HEADER_FIELDNAMES,
    MAX_ROWS,
    _get_current_date_and_time,
    _get_url_response_info,
    _parse_cmd_line_args,
    _read_csv,
    _write_csv
)

# #########
# Constants
# #########
TEST_ROW = {
    'chart': '2017/07/01',
    'date': '00:00:00',
    'executionTime': '0.552',
    'upstreamLatency': '10',
    'proxyLatency': '2',
    'responseCode': '200',
    'responseTime': '296.360969543'
}
TEST_URL = 'http://www2.gov.bc.ca/'


# ########
# Fixtures
# ########
@pytest.fixture
def datetime_now(monkeypatch):
    canada_day = datetime.datetime.strptime('2017/07/01', '%Y/%m/%d')

    class MyDateTime:
        @classmethod
        def now(cls):
            return canada_day

    monkeypatch.setattr(datetime, 'datetime', MyDateTime)
    return canada_day


@pytest.fixture
def mock_time_time(monkeypatch):
    m = mock.Mock(spec=time.time)
    monkeypatch.setattr('time.time', m)
    return m


@pytest.fixture
def mock_urlopen(monkeypatch):
    m = mock.Mock(spec=heartbeat.urlopen)
    monkeypatch.setattr(heartbeat, 'urlopen', m)
    return m


@pytest.fixture
def temp_csv_file():
    """
    Create a temporary csv file with ten rows of information.
    The temporary file will be deleted after fixture usage.
    """
    rows = [TEST_ROW] * 10

    with tempfile.NamedTemporaryFile(mode='w') as tmp_file:
        writer = csv.DictWriter(
            tmp_file,
            delimiter='|',
            fieldnames=HEADER_FIELDNAMES
        )
        writer.writeheader()
        writer.writerows(rows)
        tmp_file.flush()

        yield tmp_file.name


# #####
# Tests
# #####
class TestGetUrlResponseInfo:
    def test_http_error(self, mock_time_time, mock_urlopen):
        # Arrange
        error_info = dict(
            url=TEST_URL,
            code=404,
            msg='TEST_MSG',
            hdrs='TEST_HEADERS',
            fp=StringIO()
        )
        mock_urlopen.side_effect = HTTPError(**error_info)

        # Act
        result = _get_url_response_info('')

        # Assert
        mock_time_time.assert_called_once_with()
        assert result == {'responseCode': error_info['code']}

    @pytest.mark.parametrize('test_input', (URLError, ValueError))
    def test_other_url_errors(self, mock_time_time, mock_urlopen, test_input):
        # Arrange
        mock_urlopen.side_effect = test_input('')

        # Act
        result = _get_url_response_info('')

        # Assert
        mock_time_time.assert_called_once_with()
        assert result == {}

    def test_json_value_error(self, mock_time_time, mock_urlopen):
        # Arrange
        end_time = 10
        latency = 99
        invalid_json = '{1: 2'
        response_code = 200
        start_time = 0

        mock_time_time.side_effect = (start_time, end_time)
        (mock_urlopen.
         return_value.
         read.
         return_value) = invalid_json
        (mock_urlopen.
         return_value.
         info.
         return_value.
         getheader.
         return_value) = latency
        (mock_urlopen.
         return_value.
         getcode.
         return_value) = response_code

        # Act
        result = _get_url_response_info(TEST_URL)

        # Assert
        mock_time_time.assert_has_calls((
            mock.call(),
            mock.call()
        ))
        mock_urlopen.assert_called_once_with(TEST_URL)
        (mock_urlopen.
         return_value.
         info.
         return_value.
         getheader.
         assert_has_calls((
             mock.call('X-Kong-Proxy-Latency', default=''),
             mock.call('X-Kong-Upstream-Latency', default='')
         )))
        assert result == {
            'executionTime': '',
            'proxyLatency': latency,
            'responseCode': response_code,
            'responseTime': (end_time - start_time) * 1000,
            'upstreamLatency': latency
        }

    def test_no_error(self, mock_time_time, mock_urlopen):
        # Arrange
        end_time = 10
        execution_time = 77
        latency = 99
        response_code = 200
        start_time = 0
        valid_json = '{{"executionTime": {}}}'.format(execution_time)

        (mock_urlopen.
         return_value.
         read.
         return_value) = valid_json
        mock_time_time.side_effect = (start_time, end_time)
        (mock_urlopen.
         return_value.
         info.
         return_value.
         getheader.
         return_value) = latency
        (mock_urlopen.
         return_value.
         getcode.
         return_value) = response_code

        # Act
        result = _get_url_response_info(TEST_URL)

        # Assert
        mock_time_time.assert_has_calls((
            mock.call(),
            mock.call()
        ))
        print(mock_urlopen.call_args_list)
        # mock_urlopen.assert_called_once_with(TEST_URL)
        (mock_urlopen.
         return_value.
         info.
         return_value.
         getheader.
         assert_has_calls((
             mock.call('X-Kong-Proxy-Latency', default=''),
             mock.call('X-Kong-Upstream-Latency', default='')
         )))
        assert result == {
            'executionTime': execution_time,
            'proxyLatency': latency,
            'responseCode': response_code,
            'responseTime': (end_time - start_time) * 1000,
            'upstreamLatency': latency
        }


class TestParseCmdLineArgs:
    output_filename = '/path/to/output_file.txt'

    def test_output_file_and_url(self, monkeypatch):
        # Arrange
        monkeypatch.setattr('sys.argv', [
            '',
            '-o', self.output_filename,
            '-url', TEST_URL
        ])

        # Act
        args = _parse_cmd_line_args()

        # Assert
        assert args.output_filename == self.output_filename
        assert args.url == TEST_URL

    @pytest.mark.parametrize('test_input,expected', (
            (['', '-o', output_filename], '-url'),  # no url
            (['', '-url', TEST_URL], '-o'),  # no output filename
            ([''], '-url')  # no output filename or url
    ))
    def test_missing_arguments(
            self,
            capsys,
            expected,
            monkeypatch,
            test_input):
        # Arrange
        monkeypatch.setattr('sys.argv', test_input)

        # Act
        with pytest.raises(SystemExit):
            _parse_cmd_line_args()

        # Assert
        _, error_msg = capsys.readouterr()
        assert expected in error_msg.split('\n')[1]


def test_get_current_date_and_time(datetime_now):
    # Act
    result = _get_current_date_and_time()

    # Assert
    assert datetime_now.strftime('%Y/%m/%d') == result['chart']
    assert datetime_now.strftime('%H:%M:%S') == result['date']


def test_header_fieldnames():
    assert HEADER_FIELDNAMES == (
        'chart',  # TODO: should be 'date'?
        'date',  # TODO: should be 'time'?
        'executionTime',
        'upstreamLatency',
        'proxyLatency',
        'responseCode',
        'responseTime'
    )


def test_max_rows():
    """ 6 (10 minute chunks per hour) * 24 (hours per day) * 7 (days) """
    assert MAX_ROWS == 1008  # 6 * 24 * 7


def test_read_csv(monkeypatch, temp_csv_file):
    # Arrange
    tmp_max_rows = 5
    monkeypatch.setattr(heartbeat, 'MAX_ROWS', tmp_max_rows)

    # Act
    result = _read_csv(temp_csv_file)

    # Assert
    assert all(row == TEST_ROW for row in result)
    assert isinstance(result, collections.deque)
    assert len(result) == tmp_max_rows


def test_write_csv():
    # Arrange
    total_rows = 10
    rows = [TEST_ROW] * total_rows
    tmp_file = tempfile.NamedTemporaryFile(mode='w')

    # Act
    _write_csv(tmp_file.name, rows)
    result = _read_csv(tmp_file.name)

    # Assert
    assert all(row == TEST_ROW for row in result)
    assert len(result) == total_rows

    # Cleanup
    tmp_file.close()
    assert not os.path.exists(tmp_file.name)
