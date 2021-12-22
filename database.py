from typing import List, Union


class Database(List[dict]):
    """Class that works as a list of dictionaries with attributes for each key

    Database class which inherits the properties of a list of dictionaries. It
    also has two extra methods and an attribute per key of the internal
    dictionaries. Each key attribute is a list of the values of those keys. The
    add_entry method is a wrapper for the append method that also appends the
    key values to the attributes. The search method returns the Database with
    only the dictionaries whose key values match the requested key values.
    """

    def __init__(self, *args: dict, index: str = None):
        """Initializes the Database class to be a list of dictionaries

        Initializes the Database class by calling the list __init__, setting
        the name attribute to the class name, and looping through the given
        dictionaries to append them to the database.

        :param args: dictionaries to add to the database
        :type args: dict
        """
        super().__init__()
        self.Name = self.__class__.__name__
        self.Index = index
        self.__dict__[index] = []
        for arg in args:
            self.add_entry(arg)

    def add_entry(self, entry: dict, **kwargs) -> dict:
        """Wrapper for the list append method that adds contents to attributes

        Wrapper for the append method with the added effect of appending to the
        attributes and returning the added dictionary for validation. Key word
        arguments may be added to add a key to the dictionary before appending
        it. This will be both appended and returned.

        :param entry: Dictionary to be appended to the database
        :type entry: dict
        :param kwargs: Optional key word arguments to append to each dictionary
        :type kwargs: dict
        :return: The appended dictionary
        :rtype: dict
        """
        # add extra args to the dict
        for key, value in kwargs.items():
            entry[key] = value

        # check if new entry index matches any existing entries and overwrite
        # as necessary, appending any list items within the dicts
        if self.Index is not None:
            if self.Index not in entry.keys():
                raise KeyError("{} index key {} not found in new entry".format(
                    type(self).__name__, self.Index))
            try:
                same_id = self.search(**{self.Index: entry[self.Index]})
                replace_index = self.index(same_id)
                for key, value in same_id.items():
                    # check for appendable items/update existing info
                    if key not in entry.keys():
                        entry[key] = value
                    elif isinstance(value, list):
                        entry[key] = value + entry[key]
                self[replace_index] = entry
            except IndexError:
                self.append(entry)
        else:
            self.append(entry)

        # make attributes TODO: fix attributes overwriting parent methods
        for key, value in entry.items():
            # attributes must be remade each time since elements are mutable
            vars(self)[key] = []
            for item in self:
                if key in item:
                    vars(self)[key].append(item[key])
                else:
                    vars(self)[key].append(None)
            vars(self)[key] = tuple(vars(self)[key])
        return entry

    def search(self, get: str = "latest", **kwargs) -> Union[dict, List[dict]]:
        """Method to return a subset of the database based on a key word value

        Search method for the database class. Takes a search 'mode' in the get
        parameter which can be either 'first', 'all', or 'latest' (default).
        It also takes at least one more key word argument to use as a search
        term. The key is the matching key in the database and the value matches
        the value of that key.

        :param get: Determines the search mode (first, all, latest)
        :type get: str
        :param kwargs: Key value pairs to search the database for
        :type kwargs: dict
        :return: Database subset that matches the search terms
        :rtype: Database
        """
        assert get in ["latest", "all", "first"]
        getvals = []
        if get == "latest":
            the_list = self.__reversed__()
        else:
            the_list = self
        for item in the_list:
            for key, value in kwargs.items():
                if key not in item.keys():
                    continue
                elif item[key] == value:
                    if get in ["latest", "first"]:
                        return item.copy()
                    elif get == "all":
                        getvals.append(item)

        if get == "all" and getvals:
            return self.__class__(*getvals).copy()
        else:
            raise IndexError(
                "No {} with the value {} found in {} database".format(
                    " or ".join([str(key) for key in kwargs.keys()]),
                    " or ".join([str(value) for value in kwargs.values()]),
                    type(self).__name__))


if __name__ == "__main__":
    mydb = Database({"a": 1, "b": 2}, {"a": 2, "b": 3, "c": [4]},
                    index="a")
    mydb.add_entry({"a": 1}, **{"c": [4]})
    mydb.add_entry({"a": 1, "b": 3})
    print(mydb.b)
    print(mydb)
