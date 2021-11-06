import os
import pathlib
from fennec_executers.kubectl_executer import Kubectl
from fennec_helpers.helper import Helper
from fennec_core_dns.core_dns import CoreDNS


class Cluster(Kubectl):

    @property
    def name(self):
        return self.execution.global_parameters['CLUSTER_NAME']

    # @property
    # def admin_arn(self):
    #     return os.environ['ADMIN_ARN'] or self.execution.get_local_parameter('ADMIN_ARN')
        
    # @property
    # def username(self):
    #     return self.admin_arn.split('/')[1]


    @property
    def region(self):
        return self.execution.global_parameters["CLUSTER_REGION"]

    def __init__(self, working_folder: str):
        self.working_folder = working_folder
        Kubectl.__init__(self, working_folder)

    def check_if_cluster_exists(self):
        command = f'eksctl get clusters --region {self.region} -o json'
        clusters = self.execution.run_command(
            command, show_output=False, kubeconfig=False).log
        clusters_object = Helper.json_to_object(clusters)
        for cluster in clusters_object:
            if cluster['metadata']['name'] == self.name:
                return True
        return False

    def create(self):
        if not self.check_if_cluster_exists():
            command = f'eksctl create cluster -f "{self.__replace_cluster_values__()}"'
            Helper.print_log(command)
            self.execution.run_command(command, kubeconfig=False,show_output=True)
        else:    
            Helper.print_log(
                f"Cluster {self.name} already exists in region {self.execution.cluster_region}")
        # Helper.print_log(f'Adding user {self.admin_arn} as cluster admin')       
        # command = f'eksctl get iamidentitymapping --cluster {self.name} --arn {self.admin_arn} --region {self.region}'
        # self.execution.run_command(command, kubeconfig=False)
        # command = f'eksctl create iamidentitymapping --cluster {self.name} --arn {self.admin_arn} --group system:masters --username {self.username} --region {self.region}'
        # self.execution.run_command(command, kubeconfig=False)
        # self.execution.create_kubernetes_client()
        CoreDNS(self.working_folder).reset()

    def delete(self):
        if not self.check_if_cluster_exists():
            Helper.print_log(
                f"Cluster {self.name} doesn't exist in region {self.execution.cluster_region}")
            return
        self.__replace_cluster_values__()
        command = f'eksctl delete cluster -f "{self.__replace_cluster_values__()}"'
        self.execution.run_command(command, kubeconfig=False)

    def __replace_cluster_values__(self):
        cluster_file = os.path.join(
            self.execution.templates_folder, "00.cluster", "cluster.json")
        cluster_name = self.execution.global_parameters['CLUSTER_NAME']
        cluster_region = self.execution.global_parameters['CLUSTER_REGION']
        vpc_cidr = self.execution.global_parameters['VPC_CIDR']
        values_to_replace = {'CLUSTER_NAME': f'{cluster_name}',
                             'CLUSTER_REGION': f'{cluster_region}',
                             'VPC_CIDR': f'{vpc_cidr}'}
        cluster_output= Helper.replace_in_file(
            cluster_file, values_to_replace)
        return cluster_output
