import os
from fennec_executers.helm_executer import Helm
from fennec_helpers.helper import Helper
from fennec_nodegorup.nodegroup import Nodegroup

helm_chart = Helm(os.path.dirname(__file__), chart_name="localstack")
namespace = helm_chart.execution.get_local_parameter('NAMESPACE')
sns_url = helm_chart.execution.get_local_parameter('SNS_DNS_RECORD')
hostname = f"http://sns-localstack.{namespace}.svc.cluster.local:4566"
external_hostname = f"http://sns-localstack.{namespace}:4566"
if sns_url:
    external_hostname = sns_url

template_path = os.path.join(
    helm_chart.execution.templates_folder, "sns-ng-template.json")
nodegroup = Nodegroup(os.path.dirname(__file__), template_path)
nodegroup.create()


values_file_path = os.path.join(
    helm_chart.execution.execution_folder, "values.json")

values_file_object = Helper.file_to_object(values_file_path)
values_file_object['extraEnvVars'][1]['value'] = external_hostname
values_file_object['extraEnvVars'][2]['value'] = hostname
values_file_object['extraEnvVars'][3]['value'] = helm_chart.execution.cluster_region
if helm_chart.execution.domain_name:
    values_file_object['ingress']['enabled'] = True
    values_file_object['ingress']['hosts'][0]['host'] = f'sns-{namespace}.{helm_chart.execution.domain_name}'
execution_file = os.path.join(
    os.path.dirname(__file__), "sns-execute.values.json")
Helper.to_json_file(values_file_object, execution_file)

helm_chart.install_chart(release_name="localstack-charts",
                         chart_url="https://localstack.github.io/helm-charts",
                         deployment_name="sns",
                         additional_values=[f"--values {execution_file}"])
connection_info = f'sns: \naws --endpoint-url=http://sns-localstack.{namespace}.svc.cluster.local:4566 sns list-topics'
if helm_chart.execution.get_local_parameter('SNS_DNS_RECORD'):
    connection_info += f'\naws --endpoint-url={helm_chart.execution.get_local_parameter("SNS_DNS_RECORD")}:4566 sns list-topics'
