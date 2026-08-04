'''
This script calles create_tables to initialize database then
populates it through ingest_entries via the InitDatabaseIngest instance.
'''
import json
import re
from pathlib import Path
from sqlalchemy.orm import Session

from models.problem import Problem, Tag, TestCase, Difficulty
from db.database import SessionLocal, create_tables
from scripts.dataset_fix_lookup_tables import (
    SUPERSCRIPT_FIXES,
    BIGO_FIXES,
    TITLE_WORD_OVERRIDES,
    TASK_ID_OVERRIDES,
)

# matches a standalone roman numeral word (e.g. the "ii" in "...-queries-ii"),
# used to detect the "Part I / Part II" style suffixes LeetCode reuses across
# related problems -- str.title()/.capitalize() would otherwise give "Ii"
# instead of "II"
_ROMAN_NUMERAL_RE = re.compile(r'^(i|ii|iii|iv|v|vi|vii|viii|ix|x)$')


'''
InitDatabaseIngest is called only once to populate database with
Problem, Tag, and TestCase tables using leetcode problem list
jsonl files that are processed and added to the database.
'''
class InitDatabaseIngest:
    def __init__(self, filename, dir):
        self.filename = filename
        self.dir = dir


    # reads and processes problem rows line by line for proper database ingestion
    def ingest_entries(self, db: Session) -> None:
        entries = self.__create_list_of_dicts()
        failed = []

        # handle each problem entry
        for i, entry in enumerate(entries):
            try:
                current_problem = Problem()
                db.add(current_problem)

                # handle each key-value to build
                # Tag, Problem, and TestCase tables
                for key, value in entry.items():
                    if key == 'task_id' and isinstance(value, str):
                        current_problem.task_id = value
                        self.__process_problem_title(current_problem, value)

                    if key == 'question_id' and isinstance(value, int):
                        current_problem.question_id = value

                    if key == 'difficulty' and isinstance(value, str):
                        current_problem.difficulty = Difficulty(value)

                    if key == 'tags' and isinstance(value, list):
                        self.__process_tags(db, current_problem, value)

                    if key == 'problem_description' and isinstance(value, str):
                        self.__process_problem_description(current_problem, value)

                    if key == 'starter_code' and isinstance(value, str):
                        current_problem.starter_code = value

                    if key == 'prompt' and isinstance(value, str):
                        current_problem.execution_scaffold = value

                    if key == 'entry_point' and isinstance(value, str):
                        current_problem.entry_point = value

                    if key == 'completion' and isinstance(value, str):
                        current_problem.reference_solution = value

                    if key == 'test' and isinstance(value, str):
                        self.__process_test_cases(current_problem, value)

                    if key == 'response' and isinstance(value, str):
                        current_problem.solution_explanation = value

                db.commit()

            except Exception as e:
                identifier = entry.get("question_id", f'index {i}')
                failed.append((identifier, str(e)))
                db.rollback()
                continue
        
        # summary of run and any failures
        print(
            f"Processed {len(entries) - len(failed)}/{len(entries)} successfully."
            )
        if failed:
            print(f"{len(failed)} entries failed:")
            for identifier, error in failed:
                print(f"  {identifier}: {error}")


    # prints first problem entry from source jsonl file cleanly on console 
    def print_entries(self) -> None:
        entries = self.__create_list_of_dicts()
        first_entry = entries[0]
        for key, value in first_entry.items():
            print(f'KEY: {key}')

            if isinstance(value, str):
                value_lines = value.strip().split('\n')
                for line in value_lines:
                    print(f'{line}')
            else:
                print(f'{value}')

            print('\n')


    # processes each line to a dict and stores all in a list
    def __create_list_of_dicts(self) -> list[dict]:
        backend_path = Path(__file__).parent.parent
        full_path = f'{backend_path}/{self.dir}/{self.filename}'

        with open(full_path, "r", encoding='utf-8') as file:
            list_entries = []
            for line in file:
                problem_dict = json.loads(line)
                list_entries.append(problem_dict)

        return list_entries


    def __fix_superscripts(self, string: str) -> str:
        for incorrect, fix in SUPERSCRIPT_FIXES.items():
            pattern = re.compile(r'\b' + re.escape(incorrect) + r'\b')

            def replace_if_constraint_context(match: re.Match) -> str:
                start, end = match.start(), match.end()
                window = string[max(0, start - 10) : end + 10]
                return fix if ('<' in window or '=' in window) else match.group(0)

            string = pattern.sub(replace_if_constraint_context, string)

        for incorrect, fix in BIGO_FIXES.items():
            pattern = re.compile(r'\b' + re.escape(incorrect) + r'\b')

            def replace_if_bigo_context(match: re.Match) -> str:
                start = match.start()
                window = string[max(0, start - 2) : start]
                return fix if 'O(' in window else match.group(0)

            string = pattern.sub(replace_if_bigo_context, string)

        return string
    

    # populates Tag table and establishes link between Tag <-> Problem
    def __process_tags(self, db: Session, problem: Problem, tag_list: list[str]) -> None:
        for tag_name in tag_list:
            # shared across many problems (Tag.name is unique)
            tag = db.query(Tag).filter(Tag.name == tag_name).first()

            # only create a new Tag row if one doesn't already exist.
            # no explicit flush() here -- that would flush the whole session,
            # including this entry's still-incomplete current_problem (tags
            # is processed before other required Problem fields), causing a
            # premature NOT NULL failure. Not needed anyway: tag names don't
            # repeat within one entry, and each entry's db.commit() already
            # makes newly-created tags visible to later entries' lookups.
            if tag is None:
                tag = Tag(name=tag_name)
                db.add(tag)

            problem.tags.append(tag)


    # builds TestCase rows from the "test" field's check(candidate) function.
    # deliberately ignores the dataset's separate "input_output" field --
    # it includes reference-solution runs that timed out during dataset
    # generation and has no reliable index alignment with the assert lines
    # here, so assertion_code is the single source of truth for both grading
    # and display (sample examples + failed-case output).
    def __process_test_cases(self, problem: Problem, test: str) -> None:
        assertion_lines = [
            line.strip() for line in test.split('\n')
            if line.strip().startswith('assert ')
        ]

        for order_index, assertion_code in enumerate(assertion_lines):
            test_case = TestCase(
                assertion_code=assertion_code,
                is_sample=(order_index < 3),
                order_index=order_index,
            )
            problem.test_cases.append(test_case)


    def __process_problem_description(self, problem: Problem, description: str) -> None:
        fixed_description = self.__fix_superscripts(description)
        problem.description = fixed_description


    # derives a human-readable title from task_id (e.g. "two-sum" -> "Two Sum"),
    # since the dataset only provides the hyphenated slug, not a title field
    def __process_problem_title(self, problem: Problem, task_id: str) -> None:
        if task_id in TASK_ID_OVERRIDES:
            problem.title = TASK_ID_OVERRIDES[task_id]
            return

        titled_words = []
        for word in task_id.split('-'):
            if word in TITLE_WORD_OVERRIDES:
                titled_words.append(TITLE_WORD_OVERRIDES[word])
            elif _ROMAN_NUMERAL_RE.match(word):
                titled_words.append(word.upper())
            else:
                titled_words.append(word.capitalize())

        problem.title = ' '.join(titled_words)


if __name__ == "__main__":
    create_tables()

    db = SessionLocal()
    try:
        for filename in ('leetcode_problem_list_1.jsonl', 'leetcode_problem_list_2.jsonl'):
            ingest = InitDatabaseIngest(filename, 'problem_lists')
            ingest.ingest_entries(db)
    finally:
        db.close()