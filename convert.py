from functools import partial
import sys

def preceeding_backslashes(text, idx):
    backslashes_encountered = 0
    i = 0
    while True:
        i += 1
        if idx - i < 0:
            return backslashes_encountered
        try:
            char = text[idx-i]
        except IndexError:
            return backslashes_encountered
        if char != "\\":
            return backslashes_encountered
        backslashes_encountered += 1

def find_unescaped(text: str, target: str, offset=0, reverse=False):
    """Find first occurrence of str NOT escaped by backslash"""
    if not reverse:
        idx = text.index(target, offset)
    else:
        idx = text[:offset].rindex(target)
    if preceeding_backslashes(text, idx) % 2 != 0:
        if not reverse:
            return find_unescaped(text, target, idx+1, reverse=reverse)
        else:
            return find_unescaped(text, target, idx, reverse=reverse)
    return idx

find_square_bracket_start = partial(find_unescaped, target="[")
find_square_bracket_end = partial(find_unescaped, target="]")
find_curly_brace_end = partial(find_unescaped, target="}")

def between_delimiters(text: str, idx: int, start_delimiter: str, end_delimiter: str) -> bool:
    "Is position at idx between delimiters?"
    try:
        next_end_delimiter = find_unescaped(text, end_delimiter, idx)
    except ValueError:
        return False
    try:
        next_start_delimiter = find_unescaped(text, start_delimiter, idx)
        enclosed_on_right = next_end_delimiter < next_start_delimiter
    except ValueError:
        enclosed_on_right = True
    try:
        prev_start_delimiter = find_unescaped(text, start_delimiter, idx, reverse=True)
    except ValueError:
        return False
    try:
        prev_end_delimiter = find_unescaped(text, end_delimiter, idx, reverse=True)
        enclosed_on_left = prev_start_delimiter > prev_end_delimiter
    except ValueError:
        enclosed_on_left = True
    return enclosed_on_right and enclosed_on_left

between_square_brackets = partial(between_delimiters, start_delimiter="[", end_delimiter="]")
between_curly_braces = partial(between_delimiters, start_delimiter="{", end_delimiter="}")

def split_pandoc_text_on_lines(text):
    "Split on newlines, excluding newlines inside comment text or metadata"
    paragraph_text = ""
    paragraphs = []
    for i, char in enumerate(text):
        if char != "\n":
            paragraph_text += char
            continue
        if between_square_brackets(text, i) or between_curly_braces(text, i):
            paragraph_text += char
            continue
        paragraphs.append(paragraph_text)
        paragraph_text = ""
    paragraphs.append(paragraph_text)
    return paragraphs

def process_line(line):  # return (text, col_start, col_end) for each comment
    idx = 0
    trashed_chars = 0
    ret = []
    while True:
        try:
            idx = find_square_bracket_start(line, offset=idx)
        except ValueError:
            break
        end_idx = find_square_bracket_end(line, offset=idx)
        comment_text = line[idx+1:end_idx]
        # The +1's are to make it one-indexed for neovim
        col_start = (idx - trashed_chars) + 1
        col_end = ((idx + len(comment_text)) - trashed_chars) + 1
        ret.append((comment_text, col_start, col_end))
        first_curly_brace_end = find_curly_brace_end(line, offset=end_idx)
        second_square_bracket_start = find_square_bracket_start(line, offset=first_curly_brace_end+1)
        commented_text = line[first_curly_brace_end+1:second_square_bracket_start]
        second_curly_brace_end = find_curly_brace_end(line, offset=first_curly_brace_end+1)
        chars_to_trash = ((second_curly_brace_end - idx) + 1) - len(commented_text)
        idx = second_curly_brace_end + 1
        trashed_chars += chars_to_trash
    return ret

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: convert.py input_file")
        sys.exit()

    in_file = sys.argv[1]
    
    with open(in_file) as f:
        text = f.read()

    lines = split_pandoc_text_on_lines(text)
    all_comments = []
    for i, line in enumerate(lines):
        line_comments = process_line(line)
        for line_comment in line_comments:
            # comment text, row, col start, col end
            all_comments.append([line_comment[0], i, line_comment[1], line_comment[2]])
    print(all_comments)
