# NJ67 Papers

Includes testcases

Main documentation can be found at [nj67-server](https://github.com/garethlearnscoding/nj67-server)

Directory structure:
 - original/
    - \[paper_name\]/
        - resources/
        - task_n.ipynb
- sample-answers/
    - \[paper_name\]/
        - resources/
        - task_n.ipynb
- testcases/
    - python_testcase_function/
        - \_\_init\_\_.py
        - functions.py
    - \[paper_name\]/
        - \_\_init\_\_.py (Allow unittest to import from testcases/)
        - resources/
        - outfile_n.py (temp file)
        - test_task_n.py

## Definitions:
- `paper`      -> name of the directory
- `task`       -> notebook file
- `subtask`    -> code cell in the notebook file
<!-- seperate -->
- `no_subtask` -> Number of subtasks in the file
- `subtask_no` -> Position of the subtask in the file
<br> ...and likewise for `no_task`, `task_no`

- `notebook-hash-dict.json` -> dictionary to convert from hash string of the task to get the metadata
- `notebooks.json` -> list of all the papers inside `original/`, with metadata for the paper including no_task, and also the hashes of the task files