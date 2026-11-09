"""A module for accessing e-Stat data available in the form of Excel files.

e-Stat provides two forms of Excel workbooks: pivot analytical and reporting. Neither are readily compatible with pandas.read_excel(). Pivot workbooks from e=Stat may be missing the cache (See [Reduce the file size of your Excel spreadsheets](https://support.microsoft.com/en-us/office/reduce-the-file-size-of-your-excel-spreadsheets-c4f69e3a-8eea-4e9d-8ded-0ac301192bf9)).

The main task is to produce a `pandas.DataFrame` object. See development notes as chronicled in Read the Docs pages [pivot-xslx-functions-01.ipynb](https://estatjp.readthedocs.io/en/latest/chronicle/pivot-xslx-functions-01.html).

"""

__all__ = ["xlsx","ctf","pvt"]
