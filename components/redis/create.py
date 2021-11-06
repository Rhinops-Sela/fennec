import os
from fennec_executers.helm_executer import Helm
from fennec_helpers.helper import Helper
from fennec_nodegorup.nodegroup import Nodegroup

helm_chart = Helm(os.path.dirname(__file__), chart_name="redis")

redis_url = helm_chart.execution.get_local_parameter('REDIS_DNS_RECORD')
redis_admin_url = helm_chart.execution.get_local_parameter(
    'REDIS_ADMIN_DNS_RECORD')
namespace = helm_chart.execution.get_local_parameter('NAMESPACE')
template_path = os.path.join(
    helm_chart.execution.templates_folder, "redis-ng-template.json")
nodegroup = Nodegroup(os.path.dirname(__file__), template_path)
nodegroup.create()

helm_chart = Helm(os.path.dirname(__file__),
                  namespace=namespace, chart_name="redis")
values_file_path = os.path.join(
    helm_chart.execution.execution_folder, "values.json")

values_file_object = Helper.file_to_object(values_file_path)
# if helm_chart.execution.domain_name:
#     values_file_object['master']['hostAliases'][0] = f'dynamodb-{namespace}.{helm_chart.execution.domain_name}'

# values_file_object['master']['extraFlags'] = str(helm_chart.execution.get_local_parameter('EXTRA_FLAGS']).split(',')
# values_file_object['cluster']['slaveCount'] = helm_chart.execution.get_local_parameter('NUMBER_SLAVES']

# if helm_chart.execution.get_local_parameter('DISABLED_COMMANDS']:
#     values_file_object['master']['disableCommands'] = helm_chart.execution.get_local_parameter('DISABLED_COMMANDS'].split(',')
#     values_file_object['slave']['disableCommands'] = helm_chart.execution.get_local_parameter('DISABLED_COMMANDS'].split(',')
values_file_object['replica']['replicaCount'] = helm_chart.execution.get_local_parameter('REPLICAS')
execution_file = os.path.join(
    os.path.dirname(__file__), "redis-execute.values.json")
Helper.to_json_file(values_file_object, execution_file)

helm_chart.install_chart(release_name="bitnami",
                         chart_url="https://charts.bitnami.com/bitnami",
                         additional_values=[f"--values {execution_file}"])
ingress_port = helm_chart.execution.open_tcp_port_nginx('redis-headless', 6379)
ingress_file = Helper.replace_in_file(os.path.join(helm_chart.execution.templates_folder, "ingress", "ingress.yaml"), {
    'HOSTNAME': f'redis-{namespace}.{helm_chart.execution.domain_name}'})
helm_chart.install_file(ingress_file, namespace)

ui_foler = os.path.join(helm_chart.execution.templates_folder, 'ui')


values_to_replace = {
    'REDIS_HOST_PLACEHOOLDER': f'redis-master.{namespace}.svc.cluster.local',
    'HOSTNAME': f'redis-ui-{namespace}.{helm_chart.execution.domain_name}'}

deployment_file = Helper.replace_in_file(os.path.join(
    helm_chart.execution.templates_folder, "client", "deployment.json"), values_to_replace, max=2)
service_file = Helper.replace_in_file(os.path.join(
    helm_chart.execution.templates_folder, "client", "service.yaml"), values_to_replace)
ingress_file = Helper.replace_in_file(os.path.join(
    helm_chart.execution.templates_folder, "client", "ingress.yaml"), values_to_replace)

helm_chart.install_file(deployment_file, namespace)
helm_chart.install_file(service_file, namespace)
helm_chart.install_file(ingress_file, namespace)

helm_chart.execution.write_connection_info(service_name="Redis", ingresses=[
    f'redis-{namespace}.{helm_chart.execution.domain_name}',f'redis-ui-{namespace}.{helm_chart.execution.domain_name}'])
