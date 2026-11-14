.. estatpy development chronicle master file, created by
   Engel on Fri Feb 20 11:59:11 2026.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

estatjp development chronicle
=============================

This folder contains Jupyter notebooks created in the development of `estatjp`.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   DevAPI01.ipynb
   DevAPI02.ipynb
   exceptions-dev-01.ipynb
   apiurl-functions-01.ipynb
   apiurl-functions-02.ipynb
   pivot-xlsx-functions-01.ipynb
   pivot-xlsx-functions-02.ipynb
   moj-isa-via-api.ipynb
   non-pivot-xlsx-01.ipynb
   non-pivot-xlsx-02.ipynb
   non-pivot-xlsx-03.ipynb
   xlsx-ctf-functions-01.ipynb
   xlsx-ctf-functions-02.ipynb
   xlsx-cft-alternate-stub-parser.ipynb
   standardization-01.ipynb

## DevAPI01.ipynb

This traces development of a working `get_data(url)` function that becomes `estatjp.api.get_csv_data()`.

## DevAPI02.ipynb

Add and test exception handling for the `get_data(url)` function that becomes `estatjp.api.get_csv_data()`.

## exceptions-dev-01.ipynb

Traces develpment of an exceptions module.

## apiurl-functions-01.ipynb

Developing functions for manipulating the API url

## apiurl-functions-02.ipynb

Testing the functions after building them into estatjp v0.1.5

## pivot-xlsx-functions-01.ipynb

Developing the excel module for accessing data in pivot workbooks.

## pivot-xlsx-functions-02.ipynb

Test the functions developed in the [previous notebook](pivot-xslx-functions-01.html) and added as module `excel`.

## moj-isa-via-api.ipynb

Access tables available via API for use as references for developing the excel module.

## non-pivot-xlsx-01.ipynb

Develop functions for accessing data in xlsx workbooks that do not contain pivot tables.

## non-pivot-xlsx-02.ipynb

Further develop and extend the functionality until it can handle all excel tables in the [ISA data release for December 2014](http://www.e-stat.go.jp/SG1/estat/List.do?lid=000001133760)

## non-pivot-xlsx-03.ipynb

Parsing the column headers using a tree data structure.

## xslx-ctf-functions-01.ipynb

Cross tabulated format (CTF) functions 1. Add the ctf module for converting cross tabulated sheets to column oriented format.

## standardization-01.ipynb

This notebook is for downloading and adapting global standards data for the purpose of providing compatability between Japanese government datasets and international datasets.

# References

.. bibliography::
    :filter: docname in docnames

   
