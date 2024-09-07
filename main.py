import json
import random
import copy

# the objective of this program is to take the following field map whose
# keys are of the form (input field name) and values are of the form 
# (output field name), find the corresponding fields in the input schema,
# take the value of the field in the input data and, place it in the correct
# field in the output data.
field_map = {
    "f2": "field2",
    "f3": "field3",
    "f4": "field4",
    "f8": "field8",
}

# given input schema. Fields which map to unpackable types (see below) are mapped to fields
# in the output schema i.e. "f3" corresponds to "field3" in the output. Fields which ARE
# unpackable (i.e. dictionary/object types) do NOT have a corresponding field in the output
# schema i.e. "f6" is an object type in the input and therefore does not have a corresponding
# field in the output
input_schema = {
    "f1": {
        "f2": 3,
        "f3": "my string"
    },
    "f4": [1,2,3],
    "f5": {
        "f6": {
            "f7": {
                "f8":False
            }
        }
    }
}

# given output schema. Some of the fields do not have corresponding fields in the input schema. 
# i.e. "field6" doesn't have a corresponding input field
output_schema = {
    "field10": {
        "field1":None,
        "field2":None,
    },
    "field11": {
        "field12": {
            "field3":None
        }
    },
    "field4":None,
    "field5":None,
    "field6":None,
    "field7":None,
    "field8":None,
    "field9":None
}

#list of types which we do not "explode" further. Obvious stuff like primitives: ints, strings, bools. 
# But also things like lists. The algorithm could be modified to support expanding lists but ideally 
# the list is of a bounded size.
unpackable_types = {
    type(""):["abc","def","ghi","jkl","mno","pqr","stu","vwx","yz"],
    type(0):[0,1,2,3,4,5,6,7,8,9],
    type([1,2,3]):[[1,1,1],[2,2,2],[3,3,3],[4,4,4]],
    type(True):[True,False]
}

################### DATA GENERATION FUNCTIONS ########################
def generate_data(input_schema,num_records):
    data = []
    for _ in range(num_records):
        data_copy = copy.deepcopy(input_schema)
        _dfs_random_data_generator(data_copy)
        data.append(data_copy)
    return data

def _dfs_random_data_generator(data_dict):
    for key in data_dict:
        value = data_dict[key]
        if type(value) in unpackable_types:
            new_value = random.choice(unpackable_types[type(value)])
            data_dict[key] = new_value
        else:
            _dfs_random_data_generator(data_dict[key])

################## END DATA GENERATION FUNCTIONS ######################

################## PATH FINDING FUNCTIONS #########################

def find_path(schema,field):
    path = []
    
    def dfs(schema):

        if schema is None:
            return False

        for key in schema:
            if key == field:
                path.append(key)
                return True #True as in field found
            
            value = schema[key]

            if type(value) in unpackable_types:
                continue
            
            path.append(key)
            result = dfs(schema[key])

            if result:
                return result
            else:
                path.pop()
        
        return False
    
    dfs(schema)
    return tuple(path)

def generate_path_map(field_map):
    path_map = {}
    for input_field,output_field in field_map.items():
        path_map[find_path(input_schema,input_field)] = find_path(output_schema,output_field)

    return path_map

######################## END PATH FINDING FUNCTIONS ####################################


####################### DATA MOVEMENT FUNCTIONS #############################

def get_val_at_end_of_path(data,path):
    for step in path:
        data = data[step]
    return data

def put_val_at_end_of_path(data,path,val):
    for step in path[:-1]:
        data = data[step]
    
    data[path[-1]] = val

##################### END DATA MOVEMENT FUNCTIONS ##############################


# generate data
input_data = generate_data(input_schema,100)

# find paths for each field in field map within the input and output schemas
path_map = generate_path_map(field_map)

# generate output data
output_data = []
for data in input_data:
    out = copy.deepcopy(output_schema)
    for input_path,output_path in path_map.items():
        val = get_val_at_end_of_path(data,input_path)
        put_val_at_end_of_path(out,output_path,val)
    
    output_data.append(out)

# display results
print("INPUT")
print(json.dumps(input_data[0],indent=4))
print("")
print("FIELD MAP")
print(json.dumps(field_map,indent=4))
print("")
print("OUTPUT")
print(json.dumps(output_data[0],indent=4))
