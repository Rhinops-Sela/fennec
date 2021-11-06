import json
import inspect
import time
import os
import shutil
import sys
from pathlib import Path
import datetime


class Helper:

    @staticmethod
    def create_lock(locks_folder: str, function_name: str):
        attempts = 10
        lock_file = os.path.join(locks_folder, function_name)
        while os.path.isfile(lock_file) and attempts > -1:
            file_age = (time.time()-os.path.getmtime(lock_file))/60
            if file_age > attempts:
                os.remove(lock_file)
            else:
                Helper.print_log('wating for ngnix update to complete')
                time.sleep(5)
                attempts -= 1
        if not os.path.exists(lock_file):
            Path(os.path.dirname(lock_file)).mkdir(parents=True, exist_ok=True)
        open(lock_file, "w")

    @staticmethod
    def release_lock(locks_folder: str, function_name: str):
        lock_file = os.path.join(locks_folder, function_name)
        os.remove(lock_file)

    @staticmethod
    def exit(exit_code: int, message: str):
        Helper.print_log(message)
        sys.exit(exit_code)

    @staticmethod
    def file_to_object(file_to_convert: str):
        try:
            file = open(file_to_convert)
            converted = Helper.json_to_object(file.read())
            return converted
        except ValueError:
            Helper.print_log(file_to_convert)

    @staticmethod
    def to_json_file(content: any, file_path: str):
        try:
            file = open(file_path, 'w')
            file.write(json.dumps(content))
            file.close()
        except ValueError:
            Helper.print_log(file_path)

    @staticmethod
    def json_to_object(string_to_convert: str):
        try:
            fixed_str = string_to_convert.replace('\n', '')
            converted = json.loads(fixed_str)
            return converted
        except ValueError:
            Helper.print_log(string_to_convert)

    @staticmethod
    def copy_file(source: str, target: str):
        Path(os.path.dirname(target)).mkdir(parents=True, exist_ok=True)
        shutil.copy(source, target)

    @staticmethod
    def replace_in_file(source_file: str, strings_to_replace: dict, max=1):
        output_file_name, output_file_extension = os.path.splitext(source_file)
        output_file = f"{output_file_name}-execute{output_file_extension}"
        fin = open(source_file, "rt")
        fout = open(output_file + "_temp",
                    "wt+") if source_file == output_file else open(output_file, "wt+")
        file_content = ""
        for line in fin:
            file_content += line
        for string_to_replace in strings_to_replace.keys():
            new_value = strings_to_replace[string_to_replace]
            file_content = file_content.replace(
                string_to_replace, new_value, max)
        fout.write(file_content)
        fin.close()
        fout.close()
        if source_file == output_file:
            os.rename(output_file + "_temp", output_file)
        return output_file

    @staticmethod
    def print_log(content):
        print(f'{content}\n')
        time.sleep(1)

    @staticmethod
    def set_permissions(command: str, permission):
        command_objects = command.split(' ')
        for command_object in command_objects:
            is_file = os.path.isfile(command_object)
            if is_file:
                os.chmod(command_object, permission)

    @staticmethod
    def num(s):
        try:
            return int(s)
        except:
            return s
