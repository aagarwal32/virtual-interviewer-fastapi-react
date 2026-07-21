'''
This script calles create_tables to initialize database then
populates it through ingest_entries via the InitDatabaseIngest instance.
'''
import json
from pathlib import Path


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
    def ingest_entries(self) -> None:
        entries = self.__create_list_of_dicts()
        failed = []

        # handle each problem entry
        for i, entry in enumerate(entries):
            try:
                # TODO: instantiate problem, add to db, flush
                current_problem = None # replace with the created Problem object

                # handle each key-value to build
                # Tag, Problem, and TestCase tables
                for key, value in entry.items():
                    if key == 'tags' and isinstance(value, list):
                        self.__process_tags(value, current_problem)
                    
                    # TODO: process other key-values

                # TODO: db commit once tag, problem, and testcase tables added

            except Exception as e:
                identifier = entry.get("question_id", f'index {i}')
                failed.append((identifier, str(e)))
                continue
        
        # summary of run and any failures
        print(
            f"Processed {len(entries) - len(failed)}/{len(entries)} successfully."
            )
        if failed:
            print(f"{len(failed)} entries failed:")
            for identifier, error in failed:
                print(f"  {identifier}: {error}")


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
    

    # prints first problem entry from source jsonl file cleanly on console 
    def __print_entries(self) -> None:
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


    # populates Tag table and establishes link between Tag <-> Problem
    def __process_tags(self, tag_list: list[str], problem) -> None:
        for tag_name in tag_list:
            # TODO: activate code below once db setup

            # find existing tag by name, since the same tag name will be
            # shared across many problems (Tag.name is unique)
            # tag = db.query(Tag).filter(Tag.name == tag_name).first()

            # only create a new Tag row if one doesn't already exist
            # if tag is None:
            #     tag = Tag(name=tag_name)
            #     db.add(tag)
            #     db.flush()  # populates tag.id before it's used below

            # link this problem and tag - now that we have the live Problem
            # object (not just its id), this goes through the ORM
            # relationship instead of a raw insert into problem_tags.
            # SQLAlchemy handles the association-table row for us here.
            # problem.tags.append(tag)
            pass
                    

# TODO: execute create_tables() to instantiate database
ingest = InitDatabaseIngest('leetcode_problem_list_2.jsonl', 'problem_lists')
ingest.ingest_entries()