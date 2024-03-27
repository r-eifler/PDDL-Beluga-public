def format_number(i, max_val):
    return format_str(i, len(str(max(max_val,10))))


def format_str(no, digits):
    res = str(no)
    while len(res) < digits:
        res = "0" + res
    return res

def get_necessary_numbers(part_sizes, rack_size):
        
        numbers = set()
        numbers.add(0)
        numbers.update(part_sizes)
        changed = True

        while changed:
            new_numbers = set()
            for first in numbers:              
                for second in numbers:
                    new_number = first + second
                    if (new_number <= rack_size) and (new_number not in numbers):
                        new_numbers.add(new_number)

            changed = not new_numbers.issubset(numbers)
            numbers.update(new_numbers)            

        return numbers