import os
from fennec_core_dns.core_dns import CoreDNS
from fennec_executers.helm_executer import Helm
from fennec_execution.execution import Execution
from fennec_helpers.helper import Helper
from fennec_nodegorup.nodegroup import Nodegroup

kafka_chart = Helm(os.path.dirname(__file__), chart_name="kafka")
namespace = kafka_chart.execution.get_local_parameter('NAMESPACE')
kafka_url = kafka_chart.execution.get_local_parameter('KAFKA_DNS_RECORD')
zookeeper_url = kafka_chart.execution.get_local_parameter('ZOOKEEPER_DNS_RECORD')
template_path = os.path.join(
    kafka_chart.execution.templates_folder, "kafka-ng-template.json")
nodegroup = Nodegroup(os.path.dirname(__file__), template_path)
nodegroup.create()

values_file_path = os.path.join(
    kafka_chart.execution.execution_folder, "kafka-values.json")
values_file_object = Helper.file_to_object(values_file_path)
values_file_object['cp-kafka']['brokers'] = kafka_chart.execution.get_local_parameter('BROKERS')
values_file_object['cp-kafka']['imageTag'] = kafka_chart.execution.get_local_parameter('KAFKA_IMAGE_TAG')
values_file_object['cp-zookeeper']['enabled'] = kafka_chart.execution.get_local_parameter('INSTALL_ZOOKEEPER')
values_file_object['cp-zookeeper']['imageTag'] = kafka_chart.execution.get_local_parameter('ZOOKEEPR_IMAGE_TAG')
execution_file = os.path.join(
    os.path.dirname(__file__), "kafka-execute.values.json")
Helper.to_json_file(values_file_object, execution_file)
kafka_chart.install_chart(release_name="bitnami",
                                  chart_url="https://charts.bitnami.com/bitnami",
                                  additional_values=[f"--values {execution_file}"], 
                                  timeout = 360)
ingress_file = Helper.replace_in_file(os.path.join(kafka_chart.execution.templates_folder, "ingress", "ingress.yaml"), {
    'HOSTNAME': f'kafka-{namespace}.{kafka_chart.execution.domain_name}'})
kafka_chart.install_file(ingress_file, namespace)
ingress_port = kafka_chart.execution.open_tcp_port_nginx(
    service_name='kafka-headless', service_port=9092)
kafka_chart.execution.write_connection_info(service_name="Kafka", ingresses=[
    f'kafka-{namespace}.{kafka_chart.execution.domain_name}'])

