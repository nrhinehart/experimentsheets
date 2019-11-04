
from abc import ABCMeta
from functools import wraps, partial
import inspect
import pygsheets
import os
import pdb
import random
import six

# Your OAuth2 google sheets credentials. See the pygsheets README.md
secret_filename = os.path.realpath(os.path.dirname(__file__)) + '/client_secret.json'
client_singleton = pygsheets.authorize(client_secret=secret_filename)

def member_initialize(wrapped__init__):
    """Decorator to initialize members of a class with the named arguments. (i.e. so D.R.Y. principle is maintained
    for class initialization).

    Modified from http://stackoverflow.com/questions/1389180/python-automatically-initialize-instance-variables
    :param wrapped__init__: 
    :returns: 
    :rtype: 

    """

    names, varargs, keywords, defaults = inspect.getargspec(wrapped__init__)

    @wraps(wrapped__init__)
    def wrapper(self, *args, **kargs):
        for name, arg in list(zip(names[1:], args)) + list(kargs.items()):
            setattr(self, name, arg)

        if defaults is not None:
            for i in range(len(defaults)):
                index = -(i + 1)
                if not hasattr(self, names[index]):
                    setattr(self, names[index], defaults[index])

        wrapped__init__(self, *args, **kargs)
    return wrapper

@six.add_metaclass(ABCMeta)
class GSheetsResults:
    @member_initialize
    def __init__(self, sheet_name, worksheet_name='Sheet1', client=client_singleton):
        try:
            self.sheet = self.client.open(self.sheet_name)
        except pygsheets.exceptions.SpreadsheetNotFound:
            self.sheet = self.client.create(self.sheet_name)
        try:
            self.wks = self.sheet.worksheet_by_title(self.worksheet_name)
        except pygsheets.exceptions.WorksheetNotFound:
            self.wks = self.sheet.add_worksheet(self.worksheet_name, index=1)
        self.allocated_row = False
        self.row_claim_tag = None
        
    def __len__(self):
        count = 0
        for row in self.wks:
            count += 1
        return count

    def claim_row(self, tag):
        """Claim a row with a unique tag

        :param tag: str unique tag
        :param row_index: optional index 
        :returns: 
        :rtype: 

        """
        assert(self.row_claim_tag is None)
        if len(self.wks.find(tag)) > 0:
            raise ValueError("Cannot claim row with existing tag: '{}'".format(tag))
        self.row_claim_tag = tag
        self.wks.insert_rows(row=len(self), number=1, values=[[tag]])

    def update_claimed_row(self, row_data):
        """Update the claimed row with data.

        :param row_data: list of data to put in the row.
        :returns: 
        :rtype: 

        """
        assert(isinstance(row_data, list))
        assert(self.row_claim_tag is not None)
        matches = self.wks.find(self.row_claim_tag)
        assert(len(matches) == 1)
        # The updated values always include the tag.
        self.wks.update_values(crange='A{}'.format(matches[0].row), values=[[self.row_claim_tag] + row_data], extend=True)

def main():
    print("Instantiating")
    res = GSheetsResults("experimentsheets_example")
    unique_id = "experiment_{:08d}".format(int(random.random() * 1e6))
    print("Claiming row")
    res.claim_row(unique_id)
    experiment_result = ["data", 1, 2, 3.5, "gitid?", "foo"]
    print("Updating claimed row's data")
    res.update_claimed_row(experiment_result)
    experiment_result[-1] = "bar"
    print("Updating row again")
    res.update_claimed_row(experiment_result)

if __name__ == '__main__': main()
