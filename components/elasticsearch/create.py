import os
from fennec_executers.helm_executer import Helm
from fennec_execution.execution import Execution
from fennec_helpers.helper import Helper
from fennec_nodegorup.nodegroup import Nodegroup

execution = Execution(os.path.dirname(__file__))
namespace = execution.get_local_parameter('NAMESPACE')
template_path = os.path.join(
    execution.templates_folder, "elk-ng-template.json")
nodegroup = Nodegroup(os.path.dirname(__file__), template_path)
nodegroup.create()

elasticsearch_chart = Helm(os.path.dirname(__file__), namespace=namespace, chart_name="elasticsearch")
values_file_path = os.path.join(
    execution.execution_folder, "es-values.json")
values_file_object = Helper.file_to_object(values_file_path)
values_file_object['replicas'] = execution.get_local_parameter('REPLICAS')
values_file_object['minimumMasterNodes'] = execution.get_local_parameter('NUMBER_MASTERS')
Helper.print_log(f'!!!!!!!!!!!{elasticsearch_chart.execution.domain_name}!!!!!!!!!!')
if elasticsearch_chart.execution.domain_name:
    values_file_object['ingress']['enabled'] = True
    values_file_object['ingress']['hosts'][0]['host'] = f'es-{namespace}.{elasticsearch_chart.execution.domain_name}'

execution_file = os.path.join(
    os.path.dirname(__file__), "elasticsearch-execute.values.json")
Helper.to_json_file(values_file_object, execution_file)
elasticsearch_chart.install_chart(release_name="elastic",
                                  chart_url="https://helm.elastic.co",
                                  additional_values=[f"--values {execution_file}"], 
                                  timeout = 360)

if execution.get_local_parameter('INSTALL_KIBANA'):
    kibana_chart = Helm(os.path.dirname(__file__), namespace, "kibana")
    values_file_path = os.path.join(
        execution.execution_folder, "kibana-values.json")
    values_file_object = Helper.file_to_object(values_file_path)
    values_file_object[
        'elasticsearchHosts'] = f"http://elasticsearch-master-headless:9200"
    if kibana_chart.execution.domain_name:
        values_file_object['ingress']['enabled'] = True
        values_file_object['ingress']['hosts'][0]['host'] = f'kibana-{namespace}.{elasticsearch_chart.execution.domain_name}'
    execution_file = os.path.join(
        os.path.dirname(__file__), "kibana-execute.values.json")
    Helper.to_json_file(values_file_object, execution_file)
    kibana_chart.install_chart(release_name="elastic",
                                      chart_url="https://helm.elastic.co",
                                      additional_values=[f"--values {execution_file}"])
