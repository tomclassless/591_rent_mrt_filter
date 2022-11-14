with open('black_list.txt', 'r') as blacklist_file:
    blacklist = [int(x) for x in blacklist_file.read().splitlines()]

blacklist = set(blacklist)

with open('black_list.txt', 'w') as blacklist_file:
    for black in blacklist:
        blacklist_file.write(f'{black}\n')
