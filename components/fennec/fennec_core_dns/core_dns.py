
import sys
from fennec_core_dns.dns_record import DNSRecord
import os
from fennec_execution.execution import Execution
from fennec_helpers.helper import Helper


class CoreDNS():
    def __init__(self, working_folder: str):
        self.execution = Execution(working_folder)
        self.namespace = "kube-system"
        self.anchor_str_no_newline = "        rewrite name fennec.io fennec.io"
        self.anchor_str_with_newline = "    rewrite name fennec.io fennec.io"

    def add_records(self, dns_records: str, delimiter=";", inner_delimiter="="):
        dns_records = self.__init_dns_recotds(
            dns_records, delimiter, inner_delimiter)
        config_map = self.get_current_config()
        for dns_record in dns_records:
            if not dns_record.source or not dns_record.target:
                Helper.print_log(
                    f'Skipping dns record, source: {dns_record.source}; target: {dns_record.target}')
                continue
            anchor_str = self.anchor_str_with_newline
            if self.anchor_str_no_newline in config_map:
                anchor_str = self.anchor_str_no_newline
            line_to_add = f'{anchor_str}\n  rewrite name {dns_record.source} {dns_record.target}\n'
            if not line_to_add in config_map:
                config_map = config_map.replace(anchor_str, line_to_add, 1)
        output_file = os.path.join(
            self.execution.working_folder, 'config-map-execute.json')
        Helper.to_json_file(Helper.json_to_object(config_map), output_file)
        self.execution.run_command(
            f"kubectl apply -f {output_file} -n {self.namespace}")

    def delete_records(self, dns_records, delimiter=";", inner_delimiter="="):
        config_map = self.get_current_config()
        for dns_record in dns_records:
            if not dns_record.source or not dns_record.target:
                Helper.print_log(
                    f'Skipping dns record, source: {dns_record.source}; target: {dns_record.target}')
                continue
            line_to_delete = f'rewrite name {dns_record.source} {dns_record.target}\n'
            if line_to_delete in config_map:
                config_map = config_map.replace(line_to_delete, '', 1)
        output_file = os.path.join(
            self.execution.working_folder, 'config-map-execute.json')
        Helper.to_json_file(Helper.json_to_object(config_map), output_file)
        self.execution.run_command(
            f"kubectl apply -f {output_file} -n {self.namespace}")

    def add_records(self, dns_records: str, delimiter=";", inner_delimiter="="):
        dns_records = self.__init_dns_recotds(
            dns_records, delimiter, inner_delimiter)
        config_map = self.get_current_config()
        for dns_record in dns_records:
            if not dns_record.source or not dns_record.target:
                Helper.print_log(
                    f'Skipping dns record, source: {dns_record.source}; target: {dns_record.target}')
                continue
            anchor_str = self.anchor_str_with_newline
            if self.anchor_str_no_newline in config_map:
                anchor_str = self.anchor_str_no_newline
            line_to_add = f'{anchor_str}\n  rewrite name {dns_record.source} {dns_record.target}\n'
            if not line_to_add in config_map:
                config_map = config_map.replace(anchor_str, line_to_add, 1)
        output_file = os.path.join(
            self.execution.working_folder, 'config-map-execute.json')
        Helper.to_json_file(Helper.json_to_object(config_map), output_file)
        self.execution.run_command(
            f"kubectl apply -f {output_file} -n {self.namespace}")

    def add_records(self, dns_records: str, delimiter=";", inner_delimiter="="):
        dns_records = self.__init_dns_recotds(
            dns_records, delimiter, inner_delimiter)
        config_map = self.get_current_config()
        for dns_record in dns_records:
            if not dns_record.source or not dns_record.target:
                Helper.print_log(
                    f'Skipping dns record, source: {dns_record.source}; target: {dns_record.target}')
                continue
            anchor_str = self.anchor_str_with_newline
            if self.anchor_str_no_newline in config_map:
                anchor_str = self.anchor_str_no_newline
            line_to_add = f'{anchor_str}\n  rewrite name {dns_record.source} {dns_record.target}\n'
            if not line_to_add in config_map:
                config_map = config_map.replace(anchor_str, line_to_add, 1)
        output_file = os.path.join(
            self.execution.working_folder, 'config-map-execute.json')
        Helper.to_json_file(Helper.json_to_object(config_map), output_file)
        self.execution.run_command(
            f"kubectl apply -f {output_file} -n {self.namespace}")

    def delete_records(self, dns_records: str, delimiter=";", inner_delimiter="="):
        dns_records = self.__init_dns_recotds(
            dns_records, delimiter, inner_delimiter)
        config_map = self.get_current_config()
        for dns_record in dns_records:
            line_to_remove = f'  rewrite name {dns_record.source} {dns_record.target}\n'
            config_map = config_map.replace(line_to_remove, '')
        output_file = os.path.join(
            self.execution.working_folder, 'config-map-execute.json')
        Helper.to_json_file(Helper.json_to_object(config_map), output_file)
        self.execution.run_command(
            f"kubectl apply -f {output_file} -n {self.namespace}")

    # def delete_records(self, dns_records: str, delimiter=";", inner_delimiter="="):
    #     dns_records = self.__init_dns_recotds(
    #         dns_records, delimiter, inner_delimiter)
    #     consfig_map = self.get_current_config()
    #     new_config = [str]
    #     for config_line in consfig_map.splitlines():
    #         delete_line = False
    #         for dns_record in dns_records:
    #             if f"{dns_record.source} {dns_record.target}" in config_line:
    #                 Helper.print_log(
    #                     f"deleting dns record: source: {dns_record.source} target: {dns_record.target}")
    #                 delete_line = True
    #         if not delete_line:
    #             new_config.append(config_line)

    #     self.apply_changes(new_config)

    def __init_dns_recotds(self, dns_records_str: str, delimiter: str, inner_delimiter: str):
        try:
            dns_records = []
            for dns_record in dns_records_str.split(delimiter):
                source = dns_record.split(inner_delimiter)[0]
                target = dns_record.split(inner_delimiter)[1]
                dns_records.append(DNSRecord(source, target))
            return dns_records
        except:
            sys.exit(
                f"failed to parse dns_records_str, acceptable format: source{inner_delimiter}target{delimiter}source{inner_delimiter}target")

    def reset(self, file_path_custom: str = ""):
        file_path = file_path_custom if file_path_custom else os.path.join(self.execution.templates_folder,
                                                                           "01.coredns", "configmap.yaml")
        with open(file_path) as f:
            content = f.readlines()
        return self.apply_changes(content, False)

    def apply_changes(self, new_config, add_new_lines=True):
        output_file = os.path.join(self.execution.working_folder,
                                   "coredns-configmap-execute.yaml")
        outF = open(output_file, "w")
        for line in new_config:
            try:
                outF.write(line)
                if add_new_lines:
                    outF.write('\n')
            except:
                Helper.print_log("skipping line")
        outF.close()

        self.execution.run_command(
            f"kubectl apply -f {output_file} -n {self.namespace}")
        self.execution.run_command(
            f"kubectl delete pods -l k8s-app=kube-dns -n {self.namespace }", show_output=False)

    def get_current_config(self) -> str:
        command = f"kubectl get configmaps coredns -o json -n {self.namespace}"
        config_map = self.execution.run_command(command, show_output=False)
        return config_map.log
