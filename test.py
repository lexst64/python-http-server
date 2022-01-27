# recursion
def __search_words_by_match(sorted_words: list | tuple, match: str) -> list:
    match = match.lower().strip()

    if not sorted_words:
        return sorted_words

    mid_index = len(sorted_words) // 2

    guess = sorted_words[mid_index]
    guess_part = guess[:len(match)].lower()

    if guess_part == match:
        sorted_words_copy = list(sorted_words)
        del sorted_words_copy[mid_index]
        return [guess] + __search_words_by_match(sorted_words_copy, match)
    elif guess_part > match:
        return __search_words_by_match(sorted_words[:mid_index], match)
    else:
        return __search_words_by_match(sorted_words[mid_index + 1:], match)


# cycle
def search_words_by_match(sorted_words: list | tuple, match: str) -> list:
    sorted_words = list(sorted_words)
    match = match.lower()

    found_words = []
    low = 0
    high = len(sorted_words) - 1

    while high >= low:
        mid = (high + low) // 2

        guess = sorted_words[mid].lower()
        guess_part = guess[:len(match)]

        if guess_part == match:
            found_words.append(sorted_words.pop(mid))
            high = len(sorted_words) - 1
        elif guess_part > match:
            high = mid - 1
        else:
            low = mid + 1
    return found_words


if __name__ == '__main__':
    words = sorted(['alex', 'daria', 'alexey', 'align', 'john'])
    print(__search_words_by_match(words, 'al'))
