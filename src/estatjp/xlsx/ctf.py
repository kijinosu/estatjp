"""This estatjp.xlsx.ctf submodule performs common tasks for working with xlsx files that are in cross tabulated format.

"""
import re
import datetime as dt
from openpyxl.workbook.workbook import Workbook
from openpyxl.worksheet.worksheet import Worksheet
from openpyxl.cell.cell import Cell
from openpyxl.cell.cell import MergedCell
from openpyxl.worksheet.cell_range import (MultiCellRange, CellRange)
from openpyxl.utils import (
    get_column_letter,
)
from treelib import Tree, Node
from functools import cmp_to_key
from openpyxl.utils.cell import coordinate_from_string, column_index_from_string

def parse_title_information(
        wsheet, 
        verbose = False):
    """Excel files from e-Stat in CTF and COF format contain title
    information in two locations. The sheet name is the same as the
    file name and contains release date and table name. A separate
    title at the top of the table usually contains the stub independent
    variable, the dependent variable(s) and the name of the values being 
    tabulated. parse_title_information extracts available attributes
    as a dictionary. 

    :param wsheet: active worksheet
    :type wsheet: Worksheet

    :param verbose: Provide messaging to track progress.
    :type verbose: bool

    :return: title_result
    :rtype: dict

    Examples:
        Sheet name: "20-12-01-1"

        Title string: "第１表　国籍・地域別　在留資格（在留目的）別　在留外国人"

        title_result: {
        'table_name': '20-12-01-1', 
        'time_code': 2020001212, 
        'stats_date': '2020年12月', 
        'title_population': '在留外国人', 
        'sub_population': '<NA>', 
        'cat01_label': '国籍・地域', 
        'cat02_label': '在留資格', 
        'cat02_sublabel': '在留目的'
        }

    """
    SHEETNAME_REGEX = re.compile(r"(?P<year>\d{2})-(?P<month>\d{2})-(?P<tableno>\d{1,2}(-[\da-zA-Z0-9_]+)?)")
    TITLE_REGEX = re.compile(r"第\d+表\S*\s+(?P<cat01_label>\S+)別\s+(?P<cat02_label>\S+)別\s+(?P<title_population>\w+)\s*(（(その\w+\s+)?(?P<sub_population>[\s\S]+)）)?")
    CAT_LABEL_REGEX = re.compile(r"(?P<cat_label>\w+)（(?P<sub_cat_label>\w+)）")
    title_result = {}
    mt = SHEETNAME_REGEX.match(wsheet.title) # this is the sheet name
    if mt != None:
        yr = int("20" + mt.group('year'))
        month = int(mt.group('month'))
        sd = dt.date(yr, month, 1)
        statsdtstr = str(sd.year) + "年" + str(sd.month) + "月"
        tcstr = "20" + mt.group('year') + "00" + mt.group('month') + mt.group('month')
        title_result['table_name'] = wsheet.title.strip()
        title_result['time_code'] = int(tcstr)
        title_result['stats_date'] = statsdtstr

    coord = wsheet.dimensions
    stated_range = CellRange(coord)
    allowed_rows = 5
    rowriter = wsheet.iter_rows(
                        min_row=stated_range.min_row, 
                        max_row=stated_range.min_row+allowed_rows, 
                        min_col=stated_range.min_col, 
                        max_col=stated_range.max_col)
    for idx, row in enumerate(rowriter):
        # Parse until we get the title
        m = None
        for cell in row:
            if cell.value != None:
                m = TITLE_REGEX.match(cell.value)
                if m != None:
                    title_result["title_population"] = m.group('title_population')
                    if m.group('sub_population') != None:
                        title_result["sub_population"] = re.sub(r'[\s\n\u3000]' , '', m.group('sub_population'))
                    else:
                        title_result["sub_population"] = '<NA>'
                    title_result["cat01_label"] = m.group('cat01_label')
                    title_result["cat02_label"] = m.group('cat02_label')
                    msub = CAT_LABEL_REGEX.match(title_result["cat02_label"])
                    if msub != None:
                        title_result.update({'cat02_label': msub.group('cat_label')})
                        title_result.update({'cat02_sublabel': msub.group('sub_cat_label')})
        if m != None:
            break

    return title_result

def identify_table_ranges(
        wsheet, 
        verbose = False):
    """Excel files from e-Stat in CTF and COF format contain title
    information in two locations. The sheet name is the same as the
    file name and contains release date and table name. A separate
    title at the top of the table usually contains the stub independent
    variable, the dependent variable(s) and the name of the values being 
    tabulated. parse_title_information extracts available attributes
    as a dictionary. 

    :param wsheet: active worksheet
    :type wsheet: Worksheet

    :param verbose: Provide messaging to track progress.
    :type verbose: bool

    :return: ranges_result
    :rtype: dict

    Examples:
        ranges_result: {'valrange': <CellRange A4:BD208>, 
        'numrange': <CellRange B7:BD208>, 
        'colheadrange': <CellRange A4:BD6>, 
        'depvarheadrange': <CellRange B4:BD6>, 
        'stubcellrange': <CellRange A4:A6>, 
        'stubcolrange': <CellRange A7:A208>}

    """
    ranges_result = {
        'valrange' : None,
        'numrange' : None,
    }
    valcellrange = None
    numcellrange = None

    coord = wsheet.dimensions
    stated_range = CellRange(coord)
    found_max_col = stated_range.min_col
    startrow = stated_range.min_row
    if wsheet._print_rows != None:
        startrow = wsheet._print_rows.min_row
    rowiter = wsheet.iter_rows(
                        min_row=startrow, 
                        max_row=stated_range.max_row, 
                        min_col=stated_range.min_col, 
                        max_col=stated_range.max_col)
    for row in rowiter:
        hitcount = 0
        hitcellrange = None
        blankcellrange = None
        blankcount = 0
        max_val_col = 0
        ncellrange = None
        ncellcount = 0
        for idxcell, cell in enumerate(row):
            if (isinstance(cell, Cell) and cell.value != None):
                hitcount += 1
                thiscellrange = CellRange(cell.coordinate)
                if isinstance(hitcellrange, CellRange):
                    hitcellrange = hitcellrange.union(thiscellrange)
                else:
                    hitcellrange = thiscellrange
                if idxcell+1 > max_val_col:
                    max_val_col = cell.column
                    if max_val_col > found_max_col:
                        found_max_col = max_val_col
                if cell.data_type == 'n':
                    ncellcount += 1
                    if isinstance(ncellrange, CellRange):
                        ncellrange = ncellrange.union(thiscellrange)
                    else:
                        ncellrange = thiscellrange
            elif (isinstance(cell, Cell) and cell.value == None) or isinstance(cell, MergedCell):
                blankcount += 1
                thiscellrange = CellRange(cell.coordinate)
                if isinstance(blankcellrange, CellRange):
                    blankcellrange = blankcellrange.union(thiscellrange)
                else:
                    blankcellrange = thiscellrange
        if isinstance(numcellrange, CellRange) == True and blankcount > hitcount and max_val_col < found_max_col:
            break
        if isinstance(valcellrange, CellRange) and isinstance(hitcellrange, CellRange):
            valcellrange = valcellrange.union(hitcellrange)
        elif isinstance(hitcellrange, CellRange):
            valcellrange = hitcellrange
        if isinstance(numcellrange, CellRange) and isinstance(ncellrange, CellRange):
            numcellrange = numcellrange.union(ncellrange)
        elif isinstance(hitcellrange, CellRange):
            numcellrange = ncellrange
        if verbose == True:
            print(str(hitcount) + ' values out of ' + str(len(row)) + ' max column=' + str(max_val_col) + ' blanks: ' + str(blankcount))
            print(str(ncellcount) + ' numerical values out of ' + str(len(row)) + ' max column=' + str(max_val_col))
    if verbose == True:
        print('Value cell range: ' + str(valcellrange))
        print('Numerical cell range: ' + str(numcellrange))

    ranges_result.update({'valrange': valcellrange})
    ranges_result.update({'numrange': numcellrange})

    if isinstance(numcellrange, CellRange) == True:
        ncrsize = numcellrange.size
        if verbose == True:
            print(ncrsize)
        colheaderrange = valcellrange.__copy__()
        colheaderrange.shrink(bottom=ncrsize['rows'])
        if verbose == True:
            print('Column header range: ' + str(colheaderrange))

        rowindexrange = valcellrange.__copy__()
        rowindexrange.shrink(right=ncrsize['columns'])
        if verbose == True:
            print('Stub column range: ' + str(rowindexrange))
        stubcellrange = colheaderrange.intersection(rowindexrange)
        if verbose == True:
            print('Stub cell range: ' + str(stubcellrange))
        scrsize = stubcellrange.size
        rowindexrange.shrink(top=scrsize['rows'])
        colcount = rowindexrange.size['columns']
        if verbose == True:
            print('Stub row range: ' + str(rowindexrange))
        depvarheadrange = colheaderrange.__copy__()
        depvarheadrange.shrink(left=scrsize['columns'])
        if verbose == True:
            print('Dependent column header range: ' + str(depvarheadrange))

    ranges_result.update({'colheadrange': colheaderrange})
    ranges_result.update({'depvarheadrange': depvarheadrange})
    ranges_result.update({'stubcellrange': stubcellrange})
    ranges_result.update({'stubcolrange': rowindexrange})

    return ranges_result

def paths_to_leaves_data(atree, field=None, makeuniform=True, noneform=None):
    """The stub column and column headers are parsed using tree structures. Dictionaries in the data parameters of the nodes carry 
    parameters for the columns of the dataframe that will be created. This function is adapted from [treelib.tree.paths_to_leaves](https://treelib.readthedocs.io/en/latest/_modules/treelib/tree.html#Tree.paths_to_leaves). 

    Leaf order is not preserved.
    
    :param atree: tree structure that has node data in the form of dictionaries. 
    :type atree: treelib.tree

    :param field: name of the data_property to be collected. Every node must have this dictionary, even if it is empty.
    :type field: str

    :param makeuniform: `panda.DataFrame.from_dict()` requires dictionary rows with the same keys. If 'True', the function creates a template dictionary that contains the full set of keys. This template is copied and updated for each leaf.
    :type makeuniform: bool

    :param noneform: Value to be used for missing values.
    :type noneform: any

    :return: a list of data items, root being not omitted.

    """
    res = {}
    templatedict = {} # the dictionaries ptol must be equal length, so create a template
    if makeuniform == True:
        for leaf in atree.leaves():
            nids = [nid for nid in atree.rsearch(leaf.identifier)][::-1]
            # build templatedict
            for nid in nids:
                fdict = atree[nid].data[field]
                d = { k: noneform for k in list(fdict)}
                templatedict.update(d)

    for leaf in atree.leaves():
        nids = [nid for nid in atree.rsearch(leaf.identifier)][::-1]
        ptol = templatedict.copy()
        lid = leaf.identifier
        # sort by nid to put into column order
        for nid in nids:
            ptol.update(atree[nid].data[field])
        res.update({lid: ptol})

    return res

def _compare_columns(coord1, coord2):
    """For sort by xlsx column
    """
    collet1, row1 = coordinate_from_string(coord1)
    collet2, row2 = coordinate_from_string(coord2)
    idx1 = column_index_from_string(collet1)
    idx2 = column_index_from_string(collet2)
    return idx1-idx2

def _compare_rows(coord1, coord2):
    """For sorting by xlsx row"""
    collet1, row1 = coordinate_from_string(coord1)
    collet2, row2 = coordinate_from_string(coord2)
    return row1-row2

def create_stub_column_rows(
        wsheet,
        title_result,
        ranges_result ):
    """Parse the stub column and generate a dictionary of the respective rows.

    :param wsheet: Active worksheet containing subject table
    :type wsheet: Worksheet

    :param titleresult: Dictionary of table information
    :type titleresult: dictionary

    :param rangesresult: Dictionary of ranges for table
    :type rangesresult: dictionary

    :return: Ordered dictionary of dictionaries to be incorporated into dataframe
    :rtype: dictionary

    """
    stubtree = Tree()
    # put title derived parameters in the root
    stubtree.create_node(title_result['table_name'], 'root',data={'dfdict':{}})
    # create children for stub column (cat01) and dependent columns (cat02)
    stubtree.create_node(
        title_result["cat01_label"], 
        'cat01',      
        parent='root', 
        data={'value': '<NV>', 
              'dfdict':{
                'table_name': title_result['table_name'], 
                'time_code': title_result['time_code'],
                'stats_date': title_result['stats_date'],
                'title_population': title_result["title_population"],
                'sub_population': title_result["sub_population"],
                'cat01': title_result["cat01_label"] }})

    # create stub level dict
    stubdict = {}
    stubcellrange = ranges_result['stubcellrange']
    previousrow = [None] * stubcellrange.size['columns']
    for idxrow, row in enumerate(wsheet.iter_rows(
            min_col=stubcellrange.min_col, 
            min_row=stubcellrange.min_row, 
            max_col=stubcellrange.max_col, 
            max_row=stubcellrange.max_row)):
        for idxcell, cell in enumerate(row):
            # some tests for "merged cells" that may not be in the <mergeCells> element
            # this first test is for vertical alignment set to be centered in a selected range
            isDistributed = cell.alignment.vertical == "distributed"
            hasValue = cell.value != None # mimics merge by checking for no value
            # this second is for cells merged by selecting "Merge cells"
            inMergedCells = wsheet.merged_cells.__contains__(cell.coordinate)
            isMergeHead = hasValue == True and (isDistributed == True or inMergedCells)
            isMergedCell = hasValue == False and (isDistributed == True or inMergedCells)
        
            if cell.value == None:
                val = str('階級' + str(idxcell))
            else:
                val = re.sub(r'[\s\n\u3000]' , '', cell.value)

            stubdict.update({'cat01lvl' + str(idxcell) + '_label': val})
        
    # level by level transfer children of MergedCells to Cell preceeding MergeCell run
    max_depth = max(stubtree.level(node.identifier)
                for node in stubtree.all_nodes())
    # for cells that have only one child, append child's value to self and remove child with link_past_node
    for i in range(2,max_depth+1):
        level_nodes = [node for node in stubtree.all_nodes() if stubtree.level(node.identifier) == i]
        for node in level_nodes:
            kids = stubtree.children(node.identifier)
            thisval = '<NA>'
            thisdata = node.data.copy()
            thisdfdict = thisdata['dfdict'].copy()
            if 'value' in thisdata:  
                thisval = thisdata['value']
            if len(kids) == 0 and thisval == '<NA>':
                if stubcellrange.__contains__(cell.coordinate) == False:
                    stubtree.remove_node(node.identifier)
            if len(kids) == 1:
                kidval = kids[0].data['value']
                newval = '<NA>'
                if thisval == '<NA>' and kidval == '<NA>':
                    newval = '<NA>'
                elif thisval != '<NA>' and kidval == '<NA>':
                    newval = thisval
                elif kidval != '<NA>' and thisval == '<NA>':
                    newval = kidval
                else:
                    newval = thisval + kidval
                thisdata['value'] = newval
                thesekeys = thisdfdict.keys()
                thesevalues = thisdfdict.values()
                stubtree.update_node(node.identifier, 
                                tag=node.identifier + ' ' + newval)
                stubtree.link_past_node(kids[0].identifier)
  
    # The 1st item is the parent of all first column row labels
    stubleaves = paths_to_leaves_data(stubtree, field='dfdict')
    stubparent = list(stubleaves)[0]    
    # Iterate the rows and in each row iterate the stub columns
    row_head = []
    colcount = stubcellrange.size['columns']
    carriednodes = [None] * colcount
    # the stub column heads are for cat01. The rest are for cat02. 
    cat01_levels = ['cat01lvl' + str(n) for n in range(colcount)]
    lvl0node = stubparent
    rowindexrange = ranges_result['stubcolrange']
    for idxrow, row in enumerate(wsheet.iter_rows(
            min_row=rowindexrange.min_row, 
            max_row=rowindexrange.max_row, 
            min_col=rowindexrange.min_col,
            max_col=rowindexrange.max_col)):
        attachnode = lvl0node
        for idxcell, c in enumerate(row):
            if c.value == None:
                val = '<NA>'
            else:
                val = re.sub(r'[\s\n\u3000]' , '', c.value)
            dfdictentry = {'cat01lvl' + str(idxcell): val}
            dfdictentry.update(stubdict)
            stubtree.create_node(c.coordinate + val, 
                            c.coordinate, 
                            parent=attachnode, 
                            data={'value': val, 'dfdict': dfdictentry})
            attachnode = c.coordinate
    
    # level by level transfer children of MergedCells to Cell preceeding MergeCell run
    max_depth = max(stubtree.level(node.identifier)
                for node in stubtree.all_nodes())
    toRemove = []
    for i in range(1,max_depth):
        accumhead = None 
        level_nodes = [node for node in stubtree.all_nodes() if stubtree.level(node.identifier) == i]
        for node in level_nodes:
            if node.data['value'] != '<NA>':
                accumhead = node.identifier
            else:
                for child in stubtree.children(node.identifier):
                    stubtree.move_node(child.identifier, accumhead)
                toRemove.append(node.identifier)

    for n in toRemove:
        stubtree.remove_node(n)

    stubleaves = paths_to_leaves_data(stubtree, field='dfdict', makeuniform=True)
    row_keys = list(stubleaves)
    sortedrowkeys = sorted(row_keys, key=cmp_to_key(_compare_rows))
    row_leaves = {k: stubleaves[k] for k in sortedrowkeys}
    return row_leaves
