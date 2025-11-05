import re
def run():
    original_str = "PastEvent 90877077"
    new = original_str.split(' ')
    str = new[1]
    print(str)
    match = re.search(r'\d+', original_str)
    if match:
        str = match.group(0)
        print(str)

def test():
    str_list = ['apple', 'b', 'candy', '|', '0']
    pattern = re.compile(r"^[\w\S]$")
    new_list = [t for t in str_list if pattern.match(t)]
    for t in new_list:
        print(t)

test()
    