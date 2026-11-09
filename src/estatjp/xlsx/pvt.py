"""This estatjp.xlsx.pvt submodule performs common tasks for working with xlsx files that contain pivot tables.

"""
import pandas as pd
from openpyxl import worksheet
from openpyxl import load_workbook
from estatjp import exceptions as xs

def pivot_to_dataframe(xlsxpath, verbose=False):
    """Opens xlsx pivot workbook and returns a pandas DataFrame
    
    :param xlsxpath: Path to xlsx file
    :type xlsxpath: Path

    :param verbose: Provide messaging to track progress.
    :type verbose: bool

    :return: Pandas dataframe if successful, None if not.

    """
    # Load an Excel file
    wb = load_workbook(xlsxpath)
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
