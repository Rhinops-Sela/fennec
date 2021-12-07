import os
from fennec_core_dns.core_dns import CoreDNS
from fennec_executers.helm_executer import Helm
from fennec_execution.execution import Execution
from fennec_helpers.helper import Helper
from fennec_nodegorup.nodegroup import Nodegroup

mongodb_chart = Helm(os.path.dirname(__file__), chart_name="mongodb")
namespace = mongodb_chart.execution.get_local_parameter('NAMESPACE')
mongodb_url = mongodb_chart.execution.get_local_parameter('MONGODB_DNS_RECORD')
template_path = os.path.join(
    mongodb_chart.execution.templates_folder, "mongodb-ng-template.json")
nodegroup = Nodegroup(os.path.dirname(__file__), template_path)
nodegroup.create()

values_file_path = os.path.join(
    mongodb_chart.execution.execution_folder, "mongodb-values.json")
values_file_object = Helper.file_to_object(values_file_path)
execution_file = os.path.join(
    os.path.dirname(__file__), "mongodb-execute.values.json")
Helper.to_json_file(values_file_object, execution_file)
mongodb_chart.install_chart(release_name="bitnami",
                                  chart_url="https://charts.bitnami.com/bitnami",
                                  additional_values=[f"--values {execution_file}"], 
                                  timeout = 360)
ingress_file = Helper.replace_in_file(os.path.join(mongodb_chart.execution.templates_folder, "ingress", "ingress.yaml"), {
    'HOSTNAME': f'mongodb-{namespace}.{mongodb_chart.execution.domain_name}'})
mongodb_chart.install_file(ingress_file, namespace)
ingress_port = mongodb_chart.execution.open_tcp_port_nginx(
    service_name='mongodb', service_port=27017)
mongodb_chart.execution.write_connection_info(service_name="mongodb", ingresses=[
    f'mongodb-{namespace}.{mongodb_chart.execution.domain_name}:{ingress_port}'])

