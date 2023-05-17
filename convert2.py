import sys
import json
import os

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
    in_file = sys.argv[1]

    with open(in_file) as f:
        comments_dict = json.loads(f.read())

    md_filename = in_file[1:-9]

    with open(md_filename) as f:
        md_text = f.read()

    md_lines = md_text.split("\n")[:-1]
    final_lines = []
    for row_num, line in enumerate(md_lines):
        final_lines.append(process_line(line, row_num))
    final_text = "\n".join(final_lines)
    out_file = change_file_extension(md_filename, "docx")
    os.system(f"pandoc --wrap=none --track-changes all {md_filename} -o {out_file}")
