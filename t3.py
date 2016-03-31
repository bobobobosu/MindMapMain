import json

latest_file_list =[ {'NetworkDump': '', 'TrainDataDump': '', 'mnetwork': ''}]


with open("latest_file_json.json") as json_file:
    json.dump([], json_file, indent=4)
