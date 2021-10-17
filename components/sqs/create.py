import os
from fennec_executers.helm_executer import Helm
from fennec_execution.execution import Execution
from fennec_helpers.helper import Helper
from fennec_nodegorup.nodegroup import Nodegroup

execution = Execution(os.path.dirname(__file__))
sqs_url = execution.get_local_parameter('SQS_DNS_RECORD')
namespace = execution.get_local_parameter('NAMESPACE')
hostname = f"http://sqs-localstack.{namespace}.svc.cluster.local:80"
external_hostname = f"http://sqs-localstack.{namespace}:80"
if sqs_url:
    external_hostname = sqs_url
template_path = os.path.join(
    execution.templates_folder, "sqs-ng-template.json")
nodegroup = Nodegroup(os.path.dirname(__file__), template_path)
nodegroup.create()

helm_chart = Helm(os.path.dirname(__file__),
                  namespace=namespace, chart_name="localstack")
values_file_path = os.path.join(
    execution.execution_folder, "values.json")

values_file_object = Helper.file_to_object(values_file_path)
values_file_object['extraEnvVars'][1]['value'] = external_hostname
values_file_object['extraEnvVars'][2]['value'] = hostname
values_file_object['extraEnvVars'][3]['value'] = helm_chart.execution.cluster_region
if helm_chart.execution.domain_name:
    ingress=f'sqs-{namespace}.{helm_chart.execution.domain_name}'
    Helper.print_log(f"Adding Ingress: {ingress}")
    values_file_object['ingress']['enabled'] = True
    values_file_object['ingress']['hosts'][0]['host'] = ingress

execution_file = os.path.join(
    os.path.dirname(__file__), "sqs-execute.values.json")
Helper.to_json_file(values_file_object, execution_file)

helm_chart.install_chart(release_name="localstack-charts",
                         chart_url="https://localstack.github.io/helm-charts",
                         deployment_name="sqs",
                         additional_values=[f"--values {execution_file}"])
connection_info = f'sqs: \naws --endpoint-url=http://sqs-localstack.{namespace}.svc.cluster.local:4566 sqs create-queue --queue-name fennec'
if sqs_url:
    connection_info += f'\naws --endpoint-url={sqs_url}:4566 sqs create-queue --queue-name fennec'
Helper.write_connection_info(connection_info, execution.output_folder)
