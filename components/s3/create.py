import os
from fennec_executers.helm_executer import Helm
from fennec_helpers.helper import Helper
from fennec_nodegorup.nodegroup import Nodegroup

helm_chart = Helm(os.path.dirname(__file__), chart_name="localstack")
s3_url = helm_chart.execution.get_local_parameter('S3_DNS_RECORD')
namespace = helm_chart.execution.get_local_parameter('NAMESPACE')
hostname = f"http://s3-localstack.{namespace}.svc.cluster.local:4566"
external_hostname = f"http://sns-localstack.{namespace}:4566"
if s3_url:
    external_hostname = s3_url
template_path = os.path.join(
    helm_chart.execution.templates_folder, "s3-ng-template.json")
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
    values_file_object['ingress']['hosts'][0]['host'] = f's3-{namespace}.{helm_chart.execution.domain_name}'

execution_file = os.path.join(
    os.path.dirname(__file__), "s3-execute.values.json")
Helper.to_json_file(values_file_object, execution_file)

helm_chart.install_chart(release_name="localstack-charts",
                         chart_url="https://localstack.github.io/helm-charts",
                         deployment_name="s3",
                         additional_values=[f"--values {execution_file}"])
s3_record = f"{s3_url}=s3-localstack.{namespace}.svc.cluster.local"
connection_info = f's3: \naws s3 --endpoint-url=http://s3-localstack.{namespace}.svc.cluster.local:4566 ls'
