'''
This script creates the training and testing sets.
'''

import sys, csv, random

var_file = "./data/variables.txt"
range_file = "./data/ranges.txt"
input_file = "./data/src-data.csv"
training_file = "./data/training-data.csv"
testing_file = "./data/testing-data.csv"
   
def makesets(test_percentage = 75):
    model_variables = []
    with open(var_file, "rb") as vfile:
        for line in vfile.readlines():
            model_variables.append(line.split()[0])

    range_variables = [] 
    with open(range_file, "rb") as rfile:
        for line in rfile.readlines():
            parts = line.strip().split()        
            range_variables.append({"name":parts[0], "type":parts[1], "range":parts[2].split(",")})

    all_data = []
    complete_rows = []
    with open(input_file, "rb") as ifile:
        reader = csv.reader(ifile)
        titles = reader.next()
        model_idx = [titles.index(var) for var in model_variables]
        r = 0 
        for row in reader:
            all_missing = True
            some_missing = False
            missing_dvar = row[model_idx[0]] == "\\N"
            for i in range(1, len(model_variables)):
                var_idx = model_idx[i]
                if row[var_idx] == "\\N":
                    some_missing = True
                else:
                    all_missing = False
            
            inside_range = True
            for var in range_variables:
                idx = titles.index(var["name"])
                val = row[idx]
                if val == "\\N": continue
                vtype = var["type"]
                vrang = var["range"]   
                test = True
                if vtype == "category":
                    test = val in vrang
                else: 
                    test = float(vrang[0]) <= float(val) and float(val) < float(vrang[1])                    
                inside_range = inside_range and test
                   
            if not all_missing and not missing_dvar and inside_range:
                all_data.append([row[idx].replace("\\N", "?") for idx in model_idx])
                if not some_missing: complete_rows.append(r)
                r = r + 1 

    n = int(len(complete_rows) * (test_percentage / 100.0))
    test_idx = random.sample(complete_rows, n)
    training_data = []
    testing_data = []
    for r in range(0, len(all_data)):
        row = all_data[r]
        if r in test_idx:
            testing_data.append(row)
        else:
            training_data.append(row)    

    print "Writing train set..."
    with open(training_file, "wb") as trfile:
        writer = csv.writer(trfile, delimiter=",", quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(model_variables)
        for row in training_data:
            writer.writerow(row)
    print "Done, wrote",len(training_data),"rows."

    print "Writing test set..."
    with open(testing_file, "wb") as tefile:
        writer = csv.writer(tefile, delimiter=",", quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(model_variables)
        for row in testing_data:
            writer.writerow(row)
    print "Done, wrote",len(testing_data),"rows."

if __name__ == "__main__":
    test_percentage = 75
    if 1 < len(sys.argv):
        test_percentage = float(sys.argv[1])
    makesets(test_percentage)