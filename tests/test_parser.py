from unittest.mock import patch, MagicMock
from app.utils import parse_hh

def test_parse_hh_empty():
    result = parse_hh('')
    assert result == []

@patch('app.utils.make_request')
def test_parse_hh_valid(mock_request):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        'items': [{
            'name': 'Developer',
            'salary': None,
            'employer': {'name': 'Company'},
            'alternate_url': 'https://hh.ru/vacancy/1',
            'published_at': '2026-06-18T12:00:00+0300'
        }],
        'pages': 1
    }
    mock_request.return_value = mock_response
    result = parse_hh('python')
    assert len(result) == 1
    assert result[0]['title'] == 'Developer'