import os
from fennec_core_dns.core_dns import CoreDNS
from fennec_executers.helm_executer import Helm
from fennec_execution.execution import Execution
from fennec_helpers.helper import Helper
from fennec_nodegorup.nodegroup import Nodegroup

execution = Execution(os.path.dirname(__file__))
namespace = execution.get_local_parameter('NAMESPACE')
sns_url = execution.get_local_parameter('SNS_DNS_RECORD')
hostname = f"http://sns-localstack.{namespace}.svc.cluster.local:4566"
external_hostname = f"http://sns-localstack.{namespace}:4566"
if sns_url:
    external_hostname = sns_url

template_path = os.path.join(
    execution.templates_folder, "sns-ng-template.json")
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
execution_file = os.path.join(
    os.path.dirname(__file__), "sns-execute.values.json")
Helper.to_json_file(values_file_object, execution_file)

helm_chart.install_chart(release_name="localstack-charts",
                         chart_url="https://localstack.github.io/helm-charts",
                         deployment_name="sns",
                         additional_values=[f"--values {execution_file}"])
core_dns = CoreDNS(os.path.dirname(__file__))
core_dns.add_records(f"{sns_url}=sns-localstack.{namespace}.svc.cluster.local")
connection_info = f'sns: \naws --endpoint-url=http://sns-localstack.{namespace}.svc.cluster.local:4566 sns list-topics'
if execution.get_local_parameter('SNS_DNS_RECORD'):
    connection_info += f'\naws --endpoint-url={execution.get_local_parameter("SNS_DNS_RECORD")}:4566 sns list-topics'
Helper.write_connection_info(connection_info, execution.output_folder)
