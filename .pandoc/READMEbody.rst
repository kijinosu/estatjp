=======
estatjp
=======

.. image:: https://zenodo.org/badge/DOI/10.5281/zenodo.19124885.svg
  :target: https://doi.org/10.5281/zenodo.19124885

.. image:: https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/copier-org/copier/master/img/badge/badge-grayscale-inverted-border-teal.json
    :target: https://github.com/copier-org/copier
    :alt: Copier

`E-Stat <https://www.e-stat.go.jp/en>`__ is a widely used portal site
for accessing Japanese governmental statistical data. Began operation in
2008. e-Stat currently hosts `744 surveys (1,688,550 datasets) in
Japanese <https://www.e-stat.go.jp/stat-search?page=1>`__ from about 30
governmental agencies with `56 surveys (292,856 datasets) available in
English <https://www.e-stat.go.jp/en/stat-search?page=1>`__. These
collections contain 'databases' and files (mainly Excel files). The
'databases' can be accessed via an API. API urls can cover entire
databases or subsets that can be tailored to users' individual needs.

The objective of the estatjp Python package is to provide access to the
e-Stat portal and return datasets in pandas.DataFrame format.

For example, the e-Stat API returns CSV streams that contain headers
with metadata. These headers interfere with pandas.get_csv. The first
release of estatjp returns a dictionary that contains the header and
main table as separate dataframes.

Requirement
-----------

The e-Stat API requires an application ID that can be obtained from the
`E-Stat API <https://www.e-stat.go.jp/api/en>`__ page. Install this ID
into your project by setting your terminal to your project root and
running the following commands:

::

   pip install python-dotenv
   dotenv set ESTAT_APP_ID your-app-id

Install this package
--------------------

::

   pip install estatjp

Example
-------

This example downloads an English dataset, the `Labour Force Survey
Basic Tabulation Whole Japan Monthly table Population of 15 years old
and over by labour force
status <https://www.e-stat.go.jp/en/dbview?sid=0003005798>`__. The API
url for that table is assigned to enurl below.

.. code:: python

   import pandas
   from dotenv import load_dotenv
   from estatjp import api
   enurl = 'http://api.e-stat.go.jp/rest/3.0/app/getSimpleStatsData?appId=&lang=E&statsDataId=0003005798&metaGetFlg=Y&cntGetFlg=N&explanationGetFlg=Y&annotationGetFlg=Y&sectionHeaderFlg=1&replaceSpChars=0'
   dfs = api.get_csv_data(enurl)
   print(dfs.get('Header'))
   print(dfs.get('Main'))
   print(dfs.get('Description'))

References
==========
