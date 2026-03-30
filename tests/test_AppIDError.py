urltest1 = 'http://api.e-stat.go.jp/rest/3.0/app/getSimpleStatsData?lang=E&statsDataId=0003005798&metaGetFlg=Y&cntGetFlg=N&explanationGetFlg=Y&annotationGetFlg=Y&sectionHeaderFlg=1&replaceSpChars=0'
urltest2 = 'http://api.e-stat.go.jp/rest/3.0/app/getSimpleStatsData?appId=&lang=E&statsDataId=0003005798&metaGetFlg=Y&cntGetFlg=N&explanationGetFlg=Y&annotationGetFlg=Y&sectionHeaderFlg=1&replaceSpChars=0'

from estatjp import exceptions as xs
from estatjp import api

def CheckForAppIdString(url):
    url_split = url.split("appId=")
    if len(url_split) != 2:
        err_msg = "From CheckForAppIdString: " + url
        try:
            raise xs.AppIDError()
        except xs.AppIDError as e:
            e.add_note(err_msg)
            raise
    return True

def driver_function(url):
    result = False
    try:
        result = api.get_csv_data(url)
    except xs.AppIDError as ex:
        result = ex
    except Exception as xc:
        result = xc
    return result


def test_AppIDError_true():
    res = driver_function(urltest1)
    assert isinstance(res,xs.AppIDError) == True

    