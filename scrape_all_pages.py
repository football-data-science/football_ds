def json_loader(self):
    with open(str(self.storage_path), "r") as f:
        load_json = json.load(f)


"""
Process:
1. Load the links using a json loader.
2. for each dictionary in the list, dict['home'],dict['away'],dict['url'] need
to be passed in to create object of class match
3. 






"""
