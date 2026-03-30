"""A module for accessing e-Stat data using its API.

The API provides data in CSV, JSON and XML formats. This version provides for the CSV format only.

The main task is to request and parse a CSV stream to produce a `pandas.DataFrame` object. The `pandas.read_csv()` cannot be used as-is because CSV streams from e-Stat start with a header of metadata which confuses pandas. For more detail see development notes as chronicled in Read the Docs pages [DevAPI01.ipynb](https://estatpy.readthedocs.io/en/latest/chronicle/DevAPI01.html) and [DevAPI02.ipynb](https://estatpy.readthedocs.io/en/latest/chronicle/DevAPI02.html).



"""
import pandas as pd
import os
import requests
import tempfile
import re
import datetime
from dotenv import dotenv_values
import os
from estatjp import exceptions as xs

def get_csv_data(url, description = datetime.datetime.now()):
    """Retrieve a CSV stream from e-Stat using an API url and create a pandas.DataFrame.

    :param url: An API url obtained from e-Stat, for example, the [2020-base consumer price index](https://www.e-stat.go.jp/en/stat-search/database?page=1&layout=datalist&toukei=00200573&tstat=000001150147&cycle=0&tclass1val=0)

    :param description: An optional object that the user can supply to help document her search. The default is the time of running this function.

    :return: Dictionary containing the Header in the form of a pandas.DataFrame, the Main table also in the form of a pandas.DataFrame, and the Description.
    
    """
    try:
        dotenv_values()
    except (FileNotFoundError,IOError) as e:
        e.add_note('Environment variable file (.env) not found. See README.')
        raise

    try:
        app_id = os.environ['ESTAT_APP_ID']
    except KeyError as ek:
        e = xs.AppIDMissingError
        e.add_note('Environment variable ESTAT_APP_ID not found. See README.')
        raise e

    if app_id == None:
        e = xs.AppIDMissingError
        e.add_note("Value of environment variable 'ESTAT_APP_ID' is 'none'. See README.")
        raise e

    url_split = url.split("appId=")
    if len(url_split) != 2:
        err_msg = "From CheckUrl: " + url
        try:
            raise xs.AppIDError()
        except xs.AppIDError as e:
            e.add_note(err_msg)
            raise
    url = url_split[0] + "appId=" + app_id + url_split[1]

    # the csv has several rows of metadata terminated by a row starting with "VALUE".
    # The data table starts on the next row.
    # Put the metadata in a temporary file.
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
                        raise xs.MissingVALUEError(errmsg)
                    dfHeader = pd.read_csv(fheader.name, names = range(colnum))
                    dfHeader = dfHeader.dropna(axis=1, how = "all")
                    dfMain = pd.read_csv(fp.name)
                    result['Description'] = description
                    result['Header'] = dfHeader
                    result['Main'] = dfMain

    except requests.exceptions.RequestException as e:
            e.add_note(f'Request Exception from estatjp.api.get_csv_data for url: {url}')
            raise

    return result
