#!/usr/bin/python3
import sys
import json
import os
import argparse

def process_line(line: str, row: int) -> str:
    last_comment_end = 0
    ret = ""
    for comment_id, comment in comments_dict.items():
        current_row = int(comment["row"])
        if current_row != row:
            continue
        ret += line[last_comment_end:comment["col"]]
        commented_text = line[comment["col"]:comment["end_col"]]
        to_insert = f'[{comment["text"]}]{{.comment-start id="{int(comment_id)-1}" author="Unknown Author" date="2023-05-16T12:27:16Z"}}{commented_text}[]{{.comment-end id="{int(comment_id)-1}"}}'
        ret += to_insert
        last_comment_end = comment["end_col"]
    ret += line[last_comment_end:]
    return ret

def change_file_extension(filename: str, new_ext: str):
    return filename[:filename.rindex(".")] + "." + new_ext

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("in_file")
    parser.add_argument("-o", required=False)
    parser.add_argument("-c", required=False)
    args = parser.parse_args()

    md_path = args.in_file
    md_file_head, md_filename = os.path.split(md_path)
    out_file_path = args.o if args.o else change_file_extension(md_filename, "docx")
    _, out_file = os.path.split(out_file_path)
    if not out_file.endswith(".docx"):
        print("Output filename must end with .docx", file=sys.stderr)
        sys.exit(1)
    comments_filename = f".{md_filename}_comments"
    comments_file_head = args.c if args.c else md_file_head
    comments_path = os.path.join(comments_file_head, comments_filename)

    with open(comments_path) as f:
        comments_dict = json.loads(f.read())

    with open(md_path) as f:
        md_text = f.read()

    md_lines = md_text.split("\n")[:-1]
    final_lines = []
    for row_num, line in enumerate(md_lines):
        final_lines.append(process_line(line, row_num))
    final_text = "\n".join(final_lines)
    commented_md_filename = "commented_md.md"
    with open(commented_md_filename, "w") as f:
        f.write(final_text)
    os.system(f"pandoc --wrap=none --track-changes all {commented_md_filename} -o {out_file_path}")
    os.system(f"rm {commented_md_filename}")

