import os
from fennec_core_dns.core_dns import CoreDNS
from fennec_executers.helm_executer import Helm
from fennec_execution.execution import Execution
from fennec_helpers.helper import Helper
from fennec_nodegorup.nodegroup import Nodegroup

rabbitmq_chart = Helm(os.path.dirname(__file__), chart_name="rabbitmq")
namespace = rabbitmq_chart.execution.get_local_parameter('NAMESPACE')
rabbitmq_url = rabbitmq_chart.execution.get_local_parameter('RABBITMQ_DNS_RECORD')
template_path = os.path.join(
    rabbitmq_chart.execution.templates_folder, "rabbitmq-ng-template.json")
nodegroup = Nodegroup(os.path.dirname(__file__), template_path)
nodegroup.create()

values_file_path = os.path.join(
    rabbitmq_chart.execution.execution_folder, "rabbitmq-values.json")
values_file_object = Helper.file_to_object(values_file_path)
values_file_object['cp-rabbitmq']['brokers'] = rabbitmq_chart.execution.get_local_parameter('BROKERS')
values_file_object['cp-rabbitmq']['imageTag'] = rabbitmq_chart.execution.get_local_parameter('RABBITMQ_IMAGE_TAG')
execution_file = os.path.join(
    os.path.dirname(__file__), "rabbitmq-execute.values.json")
Helper.to_json_file(values_file_object, execution_file)
rabbitmq_chart.install_chart(release_name="bitnami",
                                  chart_url="https://charts.bitnami.com/bitnami",
                                  additional_values=[f"--values {execution_file}"], 
                                  timeout = 360)
ingress_file = Helper.replace_in_file(os.path.join(rabbitmq_chart.execution.templates_folder, "ingress", "ingress.yaml"), {
    'HOSTNAME': f'rabbitmq-{namespace}.{rabbitmq_chart.execution.domain_name}'})
rabbitmq_chart.install_file(ingress_file, namespace)
ingress_port = rabbitmq_chart.execution.open_tcp_port_nginx(
    service_name='rabbitmq-headless', service_port=5672)
rabbitmq_chart.execution.write_connection_info(service_name='rabbitmq-rabbitmq',ingress_port=ingress_port)

