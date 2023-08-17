import csv

def get_worklist(file_path, user):
    userName = user["name"]
    data = []
    with open(file_path, 'r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            data.append(row)
        for row in data:
            if(row["alias"] == userName):
                return row['worklist']