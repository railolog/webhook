import json

all_dicts = json.loads(open('russian_names.json', 'rb').read())
file = open('names.txt', 'w')
all_names = ''
for n_dict in all_dicts:
    name = n_dict['Name']
    if name.isalpha() and name[0] == name[0].upper():
        all_names += n_dict['Name'].lower() + ' '

print(len(all_names.split()))

file.write(all_names)
file.close()
