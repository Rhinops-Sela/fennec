import os
from fennec_executers.helm_executer import Helm
from fennec_helpers.helper import Helper
from fennec_nodegorup.nodegroup import Nodegroup

helm_chart = Helm(os.path.dirname(__file__), chart_name="localstack")
lambda_url = helm_chart.execution.get_local_parameter('LAMBDA_DNS_RECORD')
namespace = helm_chart.execution.get_local_parameter('NAMESPACE')
template_path = os.path.join(
    helm_chart.execution.templates_folder, "lambda-ng-template.json")
nodegroup = Nodegroup(os.path.dirname(__file__), template_path)
nodegroup.create()

values_file_path = os.path.join(
    helm_chart.execution.execution_folder, "values.json")

values_file_object = Helper.file_to_object(values_file_path)
values_file_object['extraEnvVars'][0]['value'] = helm_chart.execution.cluster_region
if helm_chart.execution.domain_name:
    values_file_object['ingress']['enabled'] = True
    values_file_object['ingress']['hosts'][0]['host'] = f'lambda-{namespace}.{helm_chart.execution.domain_name}'

execution_file = os.path.join(
    os.path.dirname(__file__), "lambda-execute.values.json")
Helper.to_json_file(values_file_object, execution_file)    

helm_chart.install_chart(release_name="localstack-charts",
                                  chart_url="https://localstack.github.io/helm-charts",
                                  deployment_name="lambda",
                                  additional_values=[f"--values {execution_file}"])