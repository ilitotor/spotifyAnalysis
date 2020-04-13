from datetime import date, timedelta
import requests
from main import get_content

def test_get():
    retorno = get_content()
    assert 200 == retorno


if __name__ == '__main__':
    unittest.main()
