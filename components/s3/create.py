import os
from fennec_core_dns.core_dns import CoreDNS
from fennec_executers.helm_executer import Helm
from fennec_execution.execution import Execution
from fennec_helpers.helper import Helper
from fennec_nodegorup.nodegroup import Nodegroup
from fennec_executers.kubectl_executer import Kubectl

execution = Execution(os.path.dirname(__file__))
s3_url = execution.get_local_parameter('S3_DNS_RECORD')
namespace = execution.get_local_parameter('NAMESPACE')
template_path = os.path.join(
    execution.templates_folder, "s3-ng-template.json")
nodegroup = Nodegroup(os.path.dirname(__file__), template_path)
nodegroup.create()

helm_chart = Helm(os.path.dirname(__file__),
                  namespace=namespace, chart_name="localstack")
values_file_path = os.path.join(
    execution.execution_folder, "values.json")

values_file_object = Helper.file_to_object(values_file_path)
values_file_object['extraEnvVars'][0]['value'] = helm_chart.execution.cluster_region
execution_file = os.path.join(
    os.path.dirname(__file__), "s3-execute.values.json")
Helper.to_json_file(values_file_object, execution_file)

helm_chart.install_chart(release_name="localstack-charts",
                         chart_url="https://localstack.github.io/helm-charts",
                         deployment_name="s3",
                         additional_values=[f"--values {execution_file}"])
s3_record = f"{s3_url}=s3-localstack.{namespace}.svc.cluster.local"
dns_records = f"{s3_record}"
core_dns = CoreDNS(os.path.dirname(__file__))

core_dns.add_records(dns_records)

connection_info = f's3: \naws s3 --endpoint-url=http://s3-localstack.{namespace}.svc.cluster.local:4566 ls'
if dns_records:
    connection_info += f'\naws s3 -endpoint-url={s3_url}:4566 s3 ls'
Helper.write_connection_info(connection_info, execution.output_folder)

