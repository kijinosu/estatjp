"""A module for accessing e-Stat data available in the form of Excel files.

e-Stat provides two forms of Excel workbooks: pivot analytical and reporting. Neither are readily compatible with pandas.read_excel(). Pivot workbooks from e=Stat may be missing the cache (See [Reduce the file size of your Excel spreadsheets](https://support.microsoft.com/en-us/office/reduce-the-file-size-of-your-excel-spreadsheets-c4f69e3a-8eea-4e9d-8ded-0ac301192bf9)).

The main task is to produce a `pandas.DataFrame` object. See development notes as chronicled in Read the Docs pages [pivot-xslx-functions-01.ipynb](https://estatjp.readthedocs.io/en/latest/chronicle/pivot-xslx-functions-01.html).

"""
import requests
import pyrfc6266
from pathlib import Path
from estatjp import exceptions as xs

def download_to_folder(
        url, 
        datapath = None,
        overwrite = False,
        verbose = False):
    """Download file from the given URL to a local path. 

    :param url: An API url obtained from e-Stat, for example, the [2020-base consumer price index](https://www.e-stat.go.jp/en/stat-search/database?page=1&layout=datalist&toukei=00200573&tstat=000001150147&cycle=0&tclass1val=0)
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


import pandas as pd
import openpyxl
from openpyxl import worksheet
def pivot_to_dataframe(xlsxpath, verbose=False):
    """Opens xlsx pivot workbook and returns a pandas DataFrame
    
    :param xlsxpath: Path to xlsx file
    :type xlsxpath: Path

    :param verbose: Provide messaging to track progress.
    :type verbose: bool

    :return: Pandas dataframe if successful, None if not.

    """
    # Load an Excel file
    wb = openpyxl.load_workbook(xlsxpath)
    snames = wb.sheetnames
    if verbose == True: 
        print("Worksheets: ")
        print(snames)

    if 'PVT' not in snames:
        print("No pivot worksheet")
        print("Not a pivot workbook.")
        return None

    ws = wb['PVT']
    # Identify the pivot table
    pivot_name = ""
    for p in ws._pivots:
        if verbose == True: 
            print("Pivot name: ")
            print(p.name)
        pivot_name=p.name #This assigns the name of the desired Pivot Table to the variable

    #extract the pivot table object
    pivot_table = [p for p in ws._pivots if p.name == pivot_name][0]
    if verbose == True: print("Extracted table: " + pivot_name)

    # Extract cache field information from pivot table
    fields_map = {}
    column_names = []
    rows = []
    if pivot_table.cache.records != None:
        for field in pivot_table.cache.cacheFields:
            if field.sharedItems != None:
                if field.sharedItems.count > 0:
                    l = []
                    for f in field.sharedItems._fields:
                        try:
                            l += [f.v]
                        except AttributeError:
                            l += [""]
                    fields_map[field.name] = l
        # Extract rows from pivot table cache into dict
        column_names = [field.name for field in pivot_table.cache.cacheFields]

        if verbose == True: 
            print("Columns: ")
            print(column_names)

        for field in pivot_table.cache.cacheFields:
            if field.sharedItems != None:
                if field.sharedItems.count > 0:
                    if verbose == True: print("Field: " + field.name)

            for record in pivot_table.cache.records.r:
                # If some field in the record is missing, replace it by NaN
                record_values = [
                    field.v if not isinstance(field, openpyxl.pivot.fields.Missing) else np.nan for field in record._fields
                ]

                row_dict = {k: v for k, v in zip(column_names, record_values)}

                # Shared fields are mapped as an Index, so we replace the field index by its value
                for key in fields_map:
                    row_dict[key] = fields_map[key][row_dict[key]]
                
                rows.append(row_dict)

    elif pivot_table != None:
        if verbose == True: print("No pivot cache.")
        # even without records, the pivot_table should include the location of the original table
        range = worksheet.cell_range.CellRange(range_string=pivot_table.location.ref)
        top_row = {k: v.value for k, v in ws._cells.items() if k in range.top}
        column_names = top_row.values()
        if verbose == True: 
            print("Columns: ")
            print(column_names)
        range.shrink(top=1)
        for row in range.rows:
            row_values = {k: v.value for k, v in ws._cells.items() if k in row }
            row_dict = {k: v for k, v in zip(column_names, row_values.values())}
            rows.append(row_dict)

    else: 
        if verbose == True: print("Not a pivot workbook.")
        return None

    df = pd.DataFrame.from_dict(rows)
    return df

import pandas as pd
import openpyxl
from openpyxl import worksheet
def xlsx_to_dataframe(xlsxpath, verbose=False):
    """Open an xlsx workbook and look for subtypes.
    
    :param xlsxpath: Path to xlsx file
    :type xlsxpath: Path

    :param verbose: Provide messaging to track progress.
    :type verbose: bool

    :return: Pandas dataframe if successful, None if not.

    """
    return "a"
