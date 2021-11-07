import json
from pathlib import Path
import subprocess
from collections import namedtuple
import os
import time
import inspect
import stat
import fcntl

from fennec_helpers.helper import Helper


class Execution:
    def __init__(self, working_folder: str):
        self.current_folder = os.path.abspath(
            os.path.join(working_folder, '..'))
        self.__kube_config_file = ""
        self.working_folder = working_folder
        self.local_parameters = {}
        self.default_values = ""
        self.global_parameters = {}
        self.__load_local_parameters__()
        self.__load_global_parameters__()
        self.set_aws_credentials()
        self.namespace = self.get_local_parameter('NAMESPACE')

    @property
    def output_folder(self):
        outputs_folder = self.global_parameters["FENNEC_OUTPUTS_FOLDER"]
        return os.path.abspath(os.path.join(self.working_folder, '..', f'{outputs_folder}'))

    @property
    def debug(self):
        return False if os.getenv('API_USER') else True

    @property
    def domain_name(self):
        return self.global_parameters["DOMAIN_NAME"]

    @property
    def execution_folder(self):
        return os.path.join(self.working_folder, "execution")

    @property
    def locks_folder(self):
        return os.path.join(self.execution_folder, '..', "locks")

    @property
    def templates_folder(self):
        return os.path.join(self.execution_folder, "templates")

    @property
    def cluster_name(self):
        return self.global_parameters["CLUSTER_NAME"]

    @property
    def cluster_region(self):
        return self.global_parameters["CLUSTER_REGION"]

    @property
    def kube_config_file(self):
        if not self.__kube_config_file:
            self.create_kubernetes_client()
        return self.__kube_config_file

    def __load_parameters__(self, default_values_file, local=True):
        with open(default_values_file) as default_values:
            self.default_values = json.load(default_values)
            if local:
                self.set_parameter(self.local_parameters)
            else:
                self.set_parameter(self.global_parameters, local=False)

    def __load_local_parameters__(self):
        default_values_file = os.path.join(
            self.execution_folder, "default.values.json")
        self.__load_parameters__(default_values_file)

    def __load_global_parameters__(self):
        for path in Path(self.current_folder).rglob('default.values.json'):
            self.__load_parameters__(path, local=False)
       # Helper.print_log(self.global_parameters)

        #path = os.path.join(self.current_folder, "global", "execution", "global.values.json")

    def set_parameter(self, working_dictionary: dict, local=True):
        for parameter_name, parameter_value in self.default_values.items():
            if not local and not parameter_value.get('global', False):
                continue
            calculated_value = self.calculate_variable_value(
                parameter_name, parameter_value)
            working_dictionary[parameter_name] = calculated_value

    def set_aws_credentials(self):
        # if not self.debug:
        #     os.environ['AWS_ACCESS_KEY_ID'] = f'{self.global_parameters["AWS_ACCESS_KEY_ID"]}'
        #     os.environ['AWS_SECRET_ACCESS_KEY'] = f'{self.global_parameters["AWS_SECRET_ACCESS_KEY"]}'
        os.environ['AWS_REGION'] = os.environ.get(
            'AWS_DEFAULT_REGION', self.get_local_parameter('AWS_DEFAULT_REGION'))

    def get_local_parameter(self, parameter_name: str):
        if parameter_name in self.local_parameters:
            return self.local_parameters[parameter_name]
        return ""

    def create_kubernetes_client(self):
        self.__kube_config_file = os.path.join(self.working_folder, '.kube')
        command = f'aws eks update-kubeconfig --name {self.cluster_name} --kubeconfig {self.kube_config_file}  --region {self.cluster_region}'
        if os.path.isfile(self.kube_config_file):
            os.remove(self.kube_config_file)
        self.run_command(command=command, kubeconfig=False)
        Helper.copy_file(self.kube_config_file,
                         os.path.join(self.output_folder, ".kube"))

    def calculate_variable_value(self, parameter_name, parameter_value):
        if self.debug:
            return parameter_value['debug']
        if os.getenv(parameter_name):
            if os.getenv(parameter_name) == 'true':
                return True
            if os.getenv(parameter_name) == 'false':
                return False
            return Helper.num(os.getenv(parameter_name))
        return ''

    def get_global_parameter(self):
        return self.default_values['global']

    def exeport_secret(self, file_name: str, content: str):
        full_path = os.path.join(self.output_folder, file_name)
        file = open(full_path, 'w+')
        file.write(content.decode('utf-8'))
        file.close()

    def nonBlockRead(self, output):
        fd = output.fileno()
        fl = fcntl.fcntl(fd, fcntl.F_GETFL)
        fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)
        try:
            return output.read()
        except:
            return ''

    def run_command(self, command: str, show_output=False, continue_on_error=False, kubeconfig=True):
        output_str = ""
        command_origingal = command
        if kubeconfig:
            Helper.set_permissions(self.kube_config_file, stat.S_IRWXU)
            command = f'export KUBECONFIG={self.kube_config_file} && {command}'
        Helper.set_permissions(command, 0o777)
        Helper.print_log(command_origingal)

        process = subprocess.Popen(
            ['/bin/bash', '-c', f'{command}'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        while True:
            output = process.stdout.readline()
            poll = process.poll()
            if output:
                output_str = output_str + output.decode('utf8')
                if show_output:
                    Helper.print_log(output.decode('utf8'))
            if poll is not None:
                    break
        command_result = namedtuple("output", ["exit_code", "log"])
        rc = process.poll()

        if rc != 0 and not continue_on_error:
            Helper.exit(rc, output_str)

        return command_result(rc, output_str)

    def write_connection_info(self, service_name: str, ingresses = [], aws_mock=False, http='http://'):
        Helper.print_log('Will Create Connection Info File')
        cwd = os.path.dirname(os.path.realpath(__file__))
        connection_info = ""
        card_file = os.path.join(cwd, "connection_info_card.html")
        page_file = os.path.join(cwd, "connection_info_page.html")
        output_file = os.path.join(self.output_folder, "connection_info.html")
        if os.path.exists(output_file):
            page_file = output_file
        connection_info = f'<p>You have installed the service in namespace: <mark class="red">{self.namespace}</mark>, in order to connect to the below urls<br>please connect to the <mark class="red">VPN</mark>.<br></p>'
        connection_info += f'<ul><mark class="red">URLS:</mark><ul>'
        for ingress in ingresses:
            connection_info += f' <li>{http}{ingress}</li>'
        connection_info += '</ul></ul>'
        if aws_mock:
            connection_info += f'<br><p>For connecting to AWS services you need to set <mark class="red">--endpoint-url</mark> to the service url listed above.<br>'
            connection_info += f'Command structure: aws <mark class="red">SERVICE_NMAE</mark> --endpoint-url=<mark class="red">URL</mark> <mark class="red">COMMAND</mark>'
            connection_info += f"<li>aws {service_name.lower()} --endpoint-url={ingresses[0]} ACTION</li></p>"
        values_to_replace = {
            'SERVICE_NAME': f'{service_name}', 'CONNECTION_INFO': connection_info}
        new_card = Path(Helper.replace_in_file(
            card_file, values_to_replace)).read_text()
        values_to_replace = {
            '<!--CARD_PLACE_HOLDER-->': new_card}
        new_page = Path(Helper.replace_in_file(
            page_file, values_to_replace)).read_text()
        f = open(output_file, "w")
        f.write(f'\n{new_page}')
        f.close()

    @staticmethod
    def get_avaliable_port(starting_port: int, port_list, inner_object: str = ''):
        find_avaliable_port = False
        while not find_avaliable_port:
            find_avaliable_port = True
            for port in port_list:
                if inner_object:
                    port = port[inner_object]
                if starting_port == int(port):
                    starting_port += 1
                    find_avaliable_port = False
                    continue

        return starting_port

    def open_tcp_port_nginx(self, service_name: str, service_port: int):
        try:
            self.delete_tcp_port_nginx(service_name, service_port)
            namespace = self.get_local_parameter('NAMESPACE')
            # Creates the lock because the nginx is relevent for all executions
            Helper.create_lock(locks_folder=self.locks_folder,
                               function_name=f'{service_name}-{namespace}')
            output_file = os.path.join(self.working_folder, 'output.json')
            config_map = Helper.json_to_object(self.run_command(
                'kubectl get configmap tcp-services -o json -n ingress-nginx')[1])
            port_to_use = Execution.get_avaliable_port(
                6000, config_map['data'])
            service_address = f'{namespace}/{service_name}:{service_port}'
            config_map['data'][f'{port_to_use}'] = service_address
            Helper.to_json_file(config_map, output_file)
            self.run_command(
                f'kubectl apply -f {output_file} -n ingress-nginx')

            ngnix_deployment = Helper.json_to_object(self.run_command(
                'kubectl get deployment ingress-nginx-controller -o json -n ingress-nginx')[1])
            ngnix_deployment_lb_port = {
                "containerPort": port_to_use,
                "hostPort": port_to_use,
                "name": f"{namespace}-{port_to_use}"
            }
            ngnix_deployment['spec']['template']['spec']['containers'][0]['ports'].append(
                ngnix_deployment_lb_port)
            Helper.to_json_file(ngnix_deployment, output_file)
            self.run_command(
                f'kubectl apply -f {output_file} -n ingress-nginx')

            ngnix_service = Helper.json_to_object(self.run_command(
                'kubectl get service ingress-nginx-controller -o json -n ingress-nginx')[1])
            node_port_to_use = Execution.get_avaliable_port(
                30000, ngnix_service['spec']['ports'], 'nodePort')
            ngnix_service_lb_port = {
                "name": f"{namespace}-{port_to_use}",
                "nodePort": node_port_to_use,
                "port": port_to_use,
                "protocol": "TCP",
                "targetPort": port_to_use
            }
            ngnix_service['spec']['ports'].append(
                ngnix_service_lb_port)
            Helper.to_json_file(ngnix_service, output_file)
            self.run_command(
                f'kubectl apply -f {output_file} -n ingress-nginx')
            return port_to_use
        except Exception as e:
            Helper.print_log('Unable to opoen ports in redis')
            Helper.print_log(e)
        finally:
            Helper.release_lock(locks_folder=self.locks_folder,
                                function_name=f'{service_name}-{namespace}')

    def delete_tcp_port_nginx(self, service_name: str, service_port: int):
        ports_to_use = []
        output_file = os.path.join(self.working_folder, 'output.json')
        namespace = self.get_local_parameter('NAMESPACE')
        service_address = f'{namespace}/{service_name}:{service_port}'
        config_map = Helper.json_to_object(self.run_command(
            'kubectl get configmap tcp-services -o json -n ingress-nginx')[1])
        for port in config_map['data']:
            port_value = config_map['data'][port]
            if port_value == service_address:
                ports_to_use.append(port)
        if not ports_to_use:
            Helper.print_log("No data to remove in nginx")
        ngnix_deployment_objects_to_remove = []
        ngnix_deployment = Helper.json_to_object(self.run_command(
            'kubectl get deployment ingress-nginx-controller -o json -n ingress-nginx')[1])
        for deployment_port in ngnix_deployment['spec']['template']['spec']['containers'][0]['ports']:
            for port_to_use in ports_to_use:
                if int(deployment_port['containerPort']) == int(port_to_use):
                    ngnix_deployment_objects_to_remove.append(deployment_port)
                    break
        for object_to_remove in ngnix_deployment_objects_to_remove:
            ngnix_deployment['spec']['template']['spec']['containers'][0]['ports'].remove(
                object_to_remove)
        Helper.to_json_file(ngnix_deployment, output_file)
        self.run_command(
            f'kubectl apply -f {output_file} -n ingress-nginx')
        ngnix_service = Helper.json_to_object(self.run_command(
            'kubectl get service ingress-nginx-controller -o json -n ingress-nginx')[1])
        ngnix_service_items_to_remove = []
        for port_object in ngnix_service['spec']['ports']:
            port_value = port_object['port']
            for port_to_use in ports_to_use:
                if int(port_value) == int(port_to_use):
                    ngnix_service_items_to_remove.append(port_object)

                    break
        for object_to_remove in ngnix_service_items_to_remove:
            ngnix_service['spec']['ports'].remove(
                object_to_remove)
        Helper.to_json_file(ngnix_service, output_file)
        self.run_command(
            f'kubectl apply -f {output_file} -n ingress-nginx')

        for port in ports_to_use:
            self.run_command(
                f'kubectl patch configmap tcp-services --type=json -p=\'[{{"op": "remove", "path": "/data/{port}"}}]\' -n ingress-nginx')

    def check_if_naemspace_exists(self, name: str) -> bool:
        namespaces = self.run_command(
            "kubectl get namespace -n all").log
        for namespace in namespaces.split('\n'):
            if name in namespace:
                return True
        return False
