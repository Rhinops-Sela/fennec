import json
import os
import shutil
import sys
from pathlib import Path
class Helper:

    @staticmethod
    def exit(exit_code: int, message: str):
        print(message)
        sys.exit(exit_code)

    @staticmethod
    def file_to_object(file_to_convert: str):
        try:
            file = open(file_to_convert)
            converted = Helper.json_to_object(file.read())
            return converted
        except ValueError:
            print(file_to_convert)

    @staticmethod
    def to_json_file(content: any, file_path: str):
        try:
            file = open(file_path, 'w')
            file.write(json.dumps(content))
            file.close()
        except ValueError:
            print(file_path)

    @staticmethod
    def json_to_object(string_to_convert: str):
        try:
            fixed_str = string_to_convert.replace('\n', '')
            converted = json.loads(fixed_str)
            return converted
        except ValueError:
            print(string_to_convert)

    @staticmethod
    def copy_file(source: str, target: str):
        Path(os.path.dirname(target)).mkdir(parents=True, exist_ok=True)
        shutil.copy(source, target)

    @staticmethod
    def replace_in_file(source_file: str, output_file: str, strings_to_replace: dict, max=1):
        fin = open(source_file, "rt")
        fout = open(output_file + "_temp",
                    "wt") if source_file == output_file else open(output_file, "wt")
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
        return file_content

    @staticmethod
    def wirte_connection_info(connection_info:str, output_folder:str):
        output_file = os.path.join(output_folder, "connection_info.info")
        f = open(f'\n{output_file}', "a+")
        f.write(connection_info)
        f.close()

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
