# Doc Comments Conversion

[Video demo:](https://youtu.be/V_vfDR9o75c)

If you are not already familiar with the Doc Comments plugin, see [here](https://github.com/oxytocin/DocComments). It allows you to make inline annotations in Neovim that are stored in a separate file and signified by highlights.

This repository contains a couple scripts to convert a text file + its corresponding Doc Comments file into a docx file and vice versa. In theory, if someone sent you a commented docx file, you could convert and read it in Neovim, make your own comments with Doc Comments, and export back to docx.

## Requirements
- [Python 3](https://www.python.org)
- [Pandoc](https://pandoc.org)
- [Doc Comments](https://github.com/oxytocin/DocComments) if you want to actually see comments or make new comments in the converted text file.

## Scripts
- docx_to_text.py: `docx_to_text.py in_file -o out_file -c comment_file_dir` Convert docx to a text file and corresponding Doc Comments file. As with the original plugin, the Doc Comments file will be created with a name of `.[original_filename]_comments` and therefore will be hidden. If not specified, the output file will be the same as the input file but with a .md extension. If the comment file dir is not specified, the Doc Comments file will be saved in the same directory as the output file.
- text_to_docx.py: `text_to_docx.py in_file -o out_file -c comment_file_dir` Convert text to docx, preserving comments made in Doc Comments. If a directory for Doc Comments files is not specified, the script will look for one in the current working directory. If the output filename is not specified, it will be the same as the input filename but with a .docx extension.

## Limitations
- Comments will be converted with "Unknown Author" and a fixed date. I am not sure what will happen if you use these scripts on a docx file that has suggestions.
- docx_to_text.py botches the conversion if two comments are right next to one another with no space between them.
