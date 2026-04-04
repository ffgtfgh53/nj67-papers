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