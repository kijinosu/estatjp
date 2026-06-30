"""A module for accessing e-Stat data using its API.

The API provides data in CSV, JSON and XML formats. This version provides for the CSV format only. It implements features of the [e-Stat API Version 4.4](https://www.e-stat.go.jp/api/api-info/e-stat-manual/#api_4_4).

The main task is to request and parse a CSV stream to produce a `pandas.DataFrame` object. The `pandas.read_csv()` cannot be used as-is because CSV streams from e-Stat start with a header of metadata which confuses pandas. For more detail see development notes as chronicled in Read the Docs pages [DevAPI01.ipynb](https://estatpy.readthedocs.io/en/latest/chronicle/DevAPI01.html) and [DevAPI02.ipynb](https://estatpy.readthedocs.io/en/latest/chronicle/DevAPI02.html).

"""
import pandas as pd
import os
import requests
import tempfile
import re
import datetime
from dotenv import dotenv_values
import urllib.parse as p
from estatjp import exceptions as xs

def get_csv_data(url, key=None, values=None, description = datetime.datetime.now()):
    """Retrieve a CSV stream from e-Stat using an API url and create a pandas.DataFrame.

    :param url: An API url obtained from e-Stat, for example, the [2020-base consumer price index](https://www.e-stat.go.jp/en/stat-search/database?page=1&layout=datalist&toukei=00200573&tstat=000001150147&cycle=0&tclass1val=0)
    :type url: string

    :param key: A filter key to be inserted into the API url call. An example is ``cdTime`` in the url ``http://api.e-stat.go.jp/rest/3.0/app/getSimpleStatsData?cdCat01=A1101&cdTime=&appId=&lang=E&statsDataId=0000020101&metaGetFlg=Y&cntGetFlg=N&explanationGetFlg=Y&annotationGetFlg=Y&sectionHeaderFlg=1&replaceSpChars=0``. If absent, a call to the function ``insert_filter_key(url, key)`` inserts it before the appId key. If the key is omitted, the API call returns all values for that key. Inserting the key and values restricts the call.
    :type key: string

    :param values: A list of value(s) to be inserted after the key.
    :type values: list

    :param description: An optional object that the user can supply to help document her search. The default is the time of running this function.
    :type description: object

    :return: Dictionary containing the Header in the form of a pandas.DataFrame, the Main table also in the form of a pandas.DataFrame, and the Description.
    :rtype: Dictionary containing a Description object; a Header (pandas.dataframe) with the metadata, and the Main pandas.dataframe

    :raises AppIDError: If request returns an error in the appId supplied by the user.
    :raises AppIDMissingError: If appId is not provided.
    :raises MissingVALUEError: If responses does not contain the VALUE keyword that marks the end of the metadata and the start of the main data table.
    :raises RequestException: If request returns an exception.
    :raises Exception: If unhandled exception.
    
    """
    try:
        url = insert_appid(url=url)
    except xs.AppIDError as e:
        raise
    except xs.AppIDMissingError as e:
        raise
    except Exception as e:
        e.add_note('Unhandled exception in insert_appid')
        raise

    if key != None:
        try:
            url = insert_filter(url=url, key=key, values=values)
        except xs.AppIDError as e:
            raise
        except xs.AppIDMissingError as e:
            raise
        except Exception as e:
            e.add_note('Unhandled exception in insert_filter')
            raise

    # the csv has several rows of metadata terminated by a row starting with "VALUE".
    # The data table starts on the next row.
    # Put the metadata in a StringIO.
    result = _get_csv_data_call(url = url, description=description)
    
    # Check for truncation of cells beyond 100,000-cell limit
    dfh = result.get('Header')
    filtered_dfh = dfh.query("@dfh[0] == 'NEXT_KEY'")
    
    while filtered_dfh.empty == False:
        nextkey = filtered_dfh[1].astype(str)
        loopurl = insert_filter(url, key='startPosition', values=nextkey)
        loopres = _get_csv_data_call(loopurl)
        loopdfh = loopres.get('Header')
        filtered_dfh = loopdfh.query("@loopdfh[0] == 'NEXT_KEY'")
        main1 = result['Main']
        mainloop = loopres['Main']
        main1 = pd.concat([main1, mainloop], ignore_index=True)
        result['Main']  =main1

    return result

def _get_csv_data_call(url, description = datetime.datetime.now()):
    """This core call takes a fully formed API url and requests a response from the e-Stat server.

    :param url: An API url obtained from e-Stat and modified locally to include the user's appId and other query keys and values
    :type url: string

    :param description: An optional object that the user can supply to help document her search. The default is the time of running this function.
    :type description: object

    :return: Dictionary containing the Header in the form of a pandas.DataFrame, the Main table also in the form of a pandas.DataFrame, and the Description.
    :rtype: Dictionary containing a Description object; a Header (pandas.dataframe) with the metadata, and the Main pandas.dataframe

    """
    result = {}
    try:
        with requests.get(url,stream=False) as estatresponse: # chunking in iter_lines doesn't work for stream=True
            estatresponse.raise_for_status()

            if estatresponse.encoding is None:
                estatresponse.encoding = 'utf-8'
            estatlines = estatresponse.iter_lines(chunk_size=1024, decode_unicode=True)
            with tempfile.NamedTemporaryFile(mode='w',delete_on_close=False,encoding = 'utf-8') as fheader:
                with tempfile.NamedTemporaryFile(mode='w',delete_on_close=False,encoding = 'utf-8') as fp:
                    inheader = True
                    colnum = 0
                    for line in estatlines:
                        if inheader == True:
                            #count columns
                            fields = re.split('","',line)
                            if len(fields) > colnum :
                                colnum = len(fields)
                            fheader.write(line)
                            fheader.write("\n")
                            if( line.startswith('"VALUE"')):
                                inheader = False
                                fheader.flush()
                                fheader.seek(0)
                        else:
                            fp.write(line)
                            fp.write("\n")
                    fheader.close()
                    fp.close()
                    if inheader == True:
                        errmsg = "The stream that e-Stat returned lacks a 'VALUE' line. See temp file: " + fheader.name
                        raise Exception(errmsg)
                    dfHeader = pd.read_csv(fheader.name, names = range(colnum), dtype=str)
                    dfHeader = dfHeader.dropna(axis=1, how = "all")
                    dfMain = pd.read_csv(fp.name, dtype=str)
                    result['Description'] = description
                    result['Header'] = dfHeader
                    result['Main'] = dfMain

    except requests.RequestException as e:
            raise

    return result

def insert_filter(url, key, values):
    """Insert a filter key and set of values to be applied.

    :param url: API url obtained from e-Stat.
    :type url: string

    :param key: A filter key to be inserted into the API url call.
    :type key: string

    :param values: A list of value(s) to be inserted after the key.
    :type values: list
    
    :return: url
    :rtype: string

    """
    if key != None:
        split = p.urlsplit(url)
        qs = p.parse_qs(split.query, keep_blank_values=True)
        vallist = list(map(str, values))
        valq = ",".join(vallist)
        qs[key] = [valq]
        qnew = p.urlencode(qs,doseq=True)
        splitnew = split._replace(query=qnew)
        urlrev = splitnew.geturl()
        return urlrev

from dotenv import load_dotenv
def insert_appid(url):
    """Insert the user's application id. The function expects that the user has previously stored this id in the project environment.

    :param url: API url obtained from e-Stat.
    :type url: string

    :return: url
    :rtype: string

    :raises FileNotFoundError,IOError: If environment variable file (.env) not found. See README.
    :raises AppIDMissingError: If environment variable ESTAT_APP_ID not found. See README.
    :raises AppIDError: If API url contains no or multiple ``appid`` keys.
   
    """
    try:
        load_dotenv()
    except (FileNotFoundError,IOError) as e:
        e.add_note('Environment variable file (.env) not found. See README.')
        raise Exception(e)
    
    try:
        app_id = os.environ['ESTAT_APP_ID']
    except KeyError as e:
        e.add_note('Environment variable ESTAT_APP_ID not found. See README.')
        raise xs.AppIDMissingError(e)

    if app_id == None:
        raise xs.AppIDMissingError("Value of environment variable 'ESTAT_APP_ID' not found. See README.")
    
    split = p.urlsplit(url)
    qs = p.parse_qs(split.query, keep_blank_values=True)
    qs['appId'] = [app_id]
    qnew = p.urlencode(qs,doseq=True)
    splitnew = split._replace(query=qnew)
    urlrev = splitnew.geturl()
    return urlrev

