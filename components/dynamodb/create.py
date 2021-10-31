import os
from fennec_core_dns.core_dns import CoreDNS
from fennec_executers.helm_executer import Helm
from fennec_execution.execution import Execution
from fennec_helpers.helper import Helper
from fennec_nodegorup.nodegroup import Nodegroup
from fennec_executers.kubectl_executer import Kubectl

helm_chart = Helm(os.path.dirname(__file__),
                  chart_name="localstack")
dynamodb_url = helm_chart.execution.get_local_parameter('DYNAMO_DNS_RECORD')
dynamodb_admin_url = helm_chart.execution.get_local_parameter('DYNAMO_ADMIN_DNS_RECORD')
namespace = helm_chart.execution.get_local_parameter('NAMESPACE')
hostname = f"http://sns-localstack.{namespace}.svc.cluster.local:4566"
external_hostname = f"http://sns-localstack.{namespace}:4566"
if dynamodb_url:
    external_hostname = dynamodb_url

template_path = os.path.join(
    helm_chart.execution.templates_folder, "dynamodb-ng-template.json")
nodegroup = Nodegroup(os.path.dirname(__file__), template_path)
nodegroup.create()

helm_chart = Helm(os.path.dirname(__file__),
                  chart_name="localstack")
values_file_path = os.path.join(
    helm_chart.execution.execution_folder, "values.json")

values_file_object = Helper.file_to_object(values_file_path)
values_file_object['extraEnvVars'][1]['value'] = external_hostname
values_file_object['extraEnvVars'][2]['value'] = hostname
values_file_object['extraEnvVars'][3]['value'] = helm_chart.execution.cluster_region
if helm_chart.execution.domain_name:
    values_file_object['ingress']['enabled'] = True
    values_file_object['ingress']['hosts'][0][
        'host'] = f'dynamodb-{namespace}.{helm_chart.execution.domain_name}'

execution_file = os.path.join(
    os.path.dirname(__file__), "dynamodb-execute.values.json")
Helper.to_json_file(values_file_object, execution_file)

helm_chart.install_chart(release_name="localstack-charts",
                         chart_url="https://localstack.github.io/helm-charts",
                         deployment_name="dynamodb",
                         additional_values=[f"--values {execution_file}"])

kubectl = Kubectl(os.path.dirname(__file__))
values_to_replace = {
    'AWS_REGION': f'{kubectl.execution.cluster_region}'}
ui_deployment_template = os.path.join(
    kubectl.execution.templates_folder, "admin", "01.deployment.json")
ui_deployment_template_output = Helper.replace_in_file(
    ui_deployment_template, values_to_replace)
kubectl.install_folder(
    "admin", helm_chart.execution.templates_folder, namespace=namespace)


connection_info = f'dynamodb: \naws dynamodb --endpoint-url=http://dynamodb-localstack.{namespace}.svc.cluster.local:4566 list-tables'
connection_info += f'\nadmin - dynamodb-local-admin.{namespace}.svc.cluster.local'
if dynamodb_admin_url:
    connection_info += f'\nadmin - {dynamodb_admin_url}'
