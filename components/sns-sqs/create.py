import os
from fennec_executers.helm_executer import Helm
from fennec_helpers.helper import Helper
from fennec_nodegorup.nodegroup import Nodegroup

helm_chart = Helm(os.path.dirname(__file__), chart_name="localstack")
namespace = helm_chart.execution.get_local_parameter('NAMESPACE')
hostname = f"http://sns-sqs-localstack.{namespace}.svc.cluster.local:80"
external_hostname = f"http://sns-sqs-localstack.{namespace}:80"

template_path = os.path.join(
    helm_chart.execution.templates_folder, "sns-sqs-ng-template.json")
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
    values_file_object['ingress']['hosts'][0][
        'host'] = f'sns-sqs-{namespace}.{helm_chart.execution.domain_name}'
execution_file = os.path.join(
    os.path.dirname(__file__), "sns-sqs-execute.values.json")
Helper.to_json_file(values_file_object, execution_file)

helm_chart.install_chart(release_name="localstack-charts",
                         chart_url="https://localstack.github.io/helm-charts",
                         deployment_name="sns-sqs",
                         additional_values=[f"--values {execution_file}"])
values_to_replace = {
    'AWS_REGION_PLACEHOLDER': f'{helm_chart.execution.cluster_region}',
    'INGRESS_ENDPOINT': f'http://sns-sqs-{namespace}.{helm_chart.execution.domain_name}',
    'CLIENT_HOSTNAME': f'sns-sqs-client-{namespace}.{helm_chart.execution.domain_name}'}

deployment_file = Helper.replace_in_file(os.path.join(
    helm_chart.execution.templates_folder, "client", "deployment.json"), values_to_replace,max=2)
service_file = Helper.replace_in_file(os.path.join(
    helm_chart.execution.templates_folder, "client", "service.json"), values_to_replace)
ingress_file = Helper.replace_in_file(os.path.join(
    helm_chart.execution.templates_folder, "client", "ingress.yaml"), values_to_replace)

helm_chart.install_file(deployment_file,namespace)
helm_chart.install_file(service_file,namespace)
helm_chart.install_file(ingress_file,namespace)
helm_chart.execution.write_connection_info(service_name="SQS", ingresses=[
    f'sqs-{namespace}.{helm_chart.execution.domain_name}'],aws_mock=True)
helm_chart.execution.write_connection_info(service_name="SNS", ingresses=[
    f'sns-{namespace}.{helm_chart.execution.domain_name}'],aws_mock=True)    
