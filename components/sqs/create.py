import os
from fennec_core_dns.core_dns import CoreDNS
from fennec_executers.helm_executer import Helm
from fennec_execution.execution import Execution
from fennec_helpers.helper import Helper
from fennec_nodegorup.nodegroup import Nodegroup

execution = Execution(os.path.dirname(__file__))
sqs_url = execution.get_local_parameter('SQS_DNS_RECORD')
namespace = execution.get_local_parameter('NAMESPACE')
template_path = os.path.join(
    execution.templates_folder, "sqs-ng-template.json")
nodegroup = Nodegroup(os.path.dirname(__file__), template_path)
nodegroup.create()

helm_chart = Helm(os.path.dirname(__file__), namespace=namespace, chart_name="localstack")
values_file_path = os.path.join(
    execution.execution_folder, "values.json")

values_file_object = Helper.file_to_object(values_file_path)
values_file_object['extraEnvVars'][0]['value'] = helm_chart.execution.cluster_region
execution_file = os.path.join(
    os.path.dirname(__file__), "sqs-execute.values.json")
Helper.to_json_file(values_file_object, execution_file)    

helm_chart.install_chart(release_name="localstack-charts",
                                  chart_url="https://localstack.github.io/helm-charts",
                                  deployment_name="sqs",
                                  additional_values=[f"--values {execution_file}"])
core_dns = CoreDNS(os.path.dirname(__file__))
core_dns.add_records(f"{sqs_url}=sqs-localstack.{namespace}.svc.cluster.local")