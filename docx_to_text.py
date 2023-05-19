#!/usr/bin/python3
from functools import partial
import json
import os
import argparse

def count_preceeding_backslashes(text: str, idx: int) -> int:
    """Count backslashes immediately preceeding char at idx"""
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

def find_unescaped(text: str, target: str, offset=0, reverse=False) -> int:
    """Find first occurrence of str NOT escaped by backslash"""
    if not reverse:
        idx = text.index(target, offset)
    else:
        idx = text[:offset].rindex(target)
    if count_preceeding_backslashes(text, idx) % 2 != 0:
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

def split_pandoc_text_on_lines(text: str):
    "Split on newlines, excluding newlines inside pandoc comment text or metadata"
    paragraph_text = ""
    paragraphs = []
    for i, char in enumerate(text):
        if char != "\n" or between_square_brackets(text, i) or between_curly_braces(text, i):
            paragraph_text += char
            continue
        paragraphs.append(paragraph_text)
        paragraph_text = ""
    paragraphs.append(paragraph_text)
    return paragraphs

def extract_comments_from_line(line: str):
    """Return [text, col_start, col_end] for each comment"""
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
        first_curly_brace_end = find_curly_brace_end(line, offset=end_idx)
        second_square_bracket_start = find_square_bracket_start(line, offset=first_curly_brace_end+1)
        commented_text = line[first_curly_brace_end+1:second_square_bracket_start]
        second_curly_brace_end = find_curly_brace_end(line, offset=first_curly_brace_end+1)
        chars_to_trash = ((second_curly_brace_end - idx) + 1) - len(commented_text)
        idx = second_curly_brace_end + 1
        trashed_chars += chars_to_trash
        col_start = (idx - trashed_chars) - len(commented_text)
        col_end = idx - trashed_chars
        ret.append((comment_text, col_start, col_end))
    return ret

def change_file_extension(filename: str, new_ext: str):
    return filename[:filename.rindex(".")] + "." + new_ext

def append_before_extension(filename: str, text_to_append: str):
    dot_index = filename.rindex(".")
    return filename[:dot_index] + text_to_append + filename[dot_index:]

def comment_to_dict(comment):
    return {"text": comment[0], "row": comment[1], "col": comment[2], "end_row": comment[1], "end_col": comment[3]}

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("in_file")
    parser.add_argument("-o", required=False)
    parser.add_argument("-c", required=False)
    args = parser.parse_args()

    in_file_path = args.in_file
    in_file_head, in_file = os.path.split(in_file_path)
    clean_markdown_path = args.o if args.o else f'./{change_file_extension(in_file, "md")}'
    clean_markdown_head, clean_markdown_filename = os.path.split(clean_markdown_path)
    commented_markdown_filename = append_before_extension(clean_markdown_filename, "_commented")
    commented_markdown_path = os.path.join(in_file_head, commented_markdown_filename)
    comments_file_head = args.c if args.c else clean_markdown_head
    comments_file_path = os.path.join(comments_file_head, f".{clean_markdown_filename}_comments")

    os.system(f"pandoc --track-changes all --wrap=none {in_file_path} -o {commented_markdown_path}")
    os.system(f"pandoc --wrap=none {in_file_path} -o {clean_markdown_path}")
    
    with open(commented_markdown_path) as f:
        text = f.read()

    lines = split_pandoc_text_on_lines(text)
    comment_id = 1
    all_comments = {}
    for i, line in enumerate(lines):
        line_comments = extract_comments_from_line(line)
        for line_comment in line_comments:
            # comment text, row, col start, col end
            full_comment = [line_comment[0], i, line_comment[1], line_comment[2]]
            comment_as_dict = comment_to_dict(full_comment)
            all_comments[comment_id] = comment_as_dict
            comment_id += 1
    with open(comments_file_path, "w") as f:
        f.write(json.dumps(all_comments))
    os.system(f"rm {commented_markdown_path}")

