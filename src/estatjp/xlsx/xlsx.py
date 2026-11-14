"""This estatjp.xlsx.xlsx submodule performs common tasks for working with xlsx files downloaded from e-Stat.

"""
import re
import datetime as dt
import requests
import pyrfc6266
from pathlib import Path
import pandas as pd
from openpyxl import load_workbook
from estatjp import exceptions as xs
from estatjp.xlsx.ctf import dataframe_from_ctf_file
from estatjp.xlsx.pvt import pivot_to_dataframe

def dataframe_from_xlsx(xlsxpath, verbose=False):
    """Top level function for getting a pandas data frame from an Excel file.

    :param xlsxpath: Path to file.
    :type xlsxpath: Path

    :param verbose: Provide messaging to track progress.
    :type verbose: bool

    :return: Pandas dataframe if successful, None if not.
    :rtype: pandas.DataFrame

    """
    dataformat = get_dataformat(xlsxpath, verbose=verbose)
    if verbose == True:
        print('data format: ' + dataformat)

    df = None
    if dataformat == 'CTF':
        df = dataframe_from_ctf_file(xlsxpath=xlsxpath, verbose=verbose)
    elif dataformat == 'PVT':
        df = pivot_to_dataframe(xlsxpath=xlsxpath, verbose=verbose)
    elif dataformat == 'XLS':
        print("XLS files not handled: " + str(xlsxpath))
        return None
    else:
        print("File format not handled: " + str(xlsxpath))

    return df


def download_to_folder(
        url, 
        datapath = None,
        overwrite = False,
        verbose = False):
    """Download file from the given URL to a local path. 

    :param url: An url that downloads an 'excel' file from e-Stat, for example, the [December 2012 release of ISA data on foreign residents](http://www.e-stat.go.jp/SG1/estat/List.do?lid=000001111233)
    :type url: string

    :param datapath: Path to folder where file is to be saved. The file name will be taken from the response header.
    :type datapath: Path

    :param overwrite: True to overwrite existing file with same name.
    :type overwrite: bool

    :return: Path to saved file

    :raises HTTPError: Bad response to request.
    :raises RequestException: If request returns an exception.
    :raises Exception: If unhandled exception

    """
    try:
        # Stream download to avoid loading the whole file into memory
        with requests.get(url, stream=True, timeout=15) as response:
            response.raise_for_status()  # Raise HTTPError for bad responses

            if verbose == True:
                h = response.headers
                print(h)

            # Get file name
            content_disp = response.headers.get("Content-Disposition", "Unknown")
            attachedfile = pyrfc6266.parse_filename(content_disp)
            savepath = Path(datapath / attachedfile)
            with savepath.open(mode='bw') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:  # Filter out keep-alive chunks
                        f.write(chunk)
                
                f.close()
            return savepath

    except requests.exceptions.RequestException as e:
        print(f"Download failed: {e}")
        return None

def get_dataformat(xlsxpath, verbose=False):
    """There are four known dataformats among the xlsx files
    from E-Stat: cross tabulated format (CTF), column-oriented format
    (COF), pivot (PVT) (including pivot but no cache records). 
    Determine format from file.

    :param xlsxpath: Path to xlsx file
    :type xlsxpath: Path

    :param verbose: Provide messaging to track progress.
    :type verbose: bool

    :return: dataformat
    :rtype: string

    """
    p = Path(xlsxpath)
    if p.suffix == '.xls':
        return 'XLS'
    
    SHEETNAME_REGEX = re.compile(r"(?P<year>\d{2})-(?P<month>\d{2})-(?P<tableno>\d{1,2}(-[\da-zA-Z0-9_]+)?)")
    wb = load_workbook(xlsxpath, data_only=True)
    snames = wb.sheetnames
    if verbose == True:
        print(snames)
    has_pivot = False
    is_column_oriented = False
    for ws in wb.worksheets:
        if verbose == True:
            print('title: ' + ws.title)
            print('dimensions: ' + ws.dimensions)
            if ws.print_title_cols != None:
                print('print_title_cols: ' + ws.print_title_cols)
            if ws.print_title_rows != None:
                print('print_title_rows: ' + ws.print_title_rows)
            print('_pivots len: ' + str(len(ws._pivots)))
        if len(ws._pivots) > 0:
            has_pivot = True
            if verbose == True:
                print('pivot_table.cache.records: ' + str(ws._pivots[0].cache.records))
            if ws._pivots[0].cache.records != None:
                has_pivot_cache_records = True
        if verbose == True:
            print('merged_cells len: ' + str(len(ws.merged_cells.ranges)))
        # the year, month and table name are in ws.title. This is the name of the sheet if not a pivot table.
        mt = SHEETNAME_REGEX.match(ws.title)
        if mt != None:
            if verbose == True:
                print('tableno: ' + mt.group('tableno'))
            is_column_oriented = mt.group('tableno').endswith('m')
    dataformat = 'CTF'
    if has_pivot == True:
        dataformat = 'PVT'
    elif is_column_oriented == True:
        dataformat = 'COF'

    return dataformat
