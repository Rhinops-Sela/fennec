import os
from fennec_executers.helm_executer import Helm
from fennec_execution.execution import Execution
from fennec_helpers.helper import Helper
from fennec_nodegorup.nodegroup import Nodegroup


execution = Execution(os.path.dirname(__file__))
ingress_port = execution.open_tcp_port_nginx('mysql-headless', 3306)
namespace = execution.get_local_parameter('NAMESPACE')
template_path = os.path.join(
    execution.templates_folder, "mysql-ng-template.json")
nodegroup = Nodegroup(os.path.dirname(__file__), template_path)
nodegroup.create()

helm_chart = Helm(os.path.dirname(__file__),
                  namespace=namespace, chart_name="mysql")
ingress_file = Helper.replace_in_file(os.path.join(execution.templates_folder, "ingress", "ingress.yaml"), {
    'HOSTNAME': f'mysql-{namespace}.{execution.domain_name}'})
helm_chart.install_file(ingress_file,namespace)            
values_file_path = os.path.join(
    execution.execution_folder, "values.json")

execution_file = os.path.join(
    os.path.dirname(__file__), "mysql-execute.values.json")
Helper.copy_file(values_file_path, execution_file)
root_password = execution.get_local_parameter("MYSQL_ROOT_PASSWORD")
password = execution.get_local_parameter("MYSQL_PASSWORD")
username = execution.get_local_parameter("MYSQL_USERNAME")
database = execution.get_local_parameter("MYSQL_DB_NAME")
helm_chart.install_chart(release_name="bitnami",
                         chart_url="https://charts.bitnami.com/bitnami",
                         deployment_name="mysql",
                         additional_values=[f"--values {execution_file} \
                             --set auth.username={username} \
                             --set auth.rootPassword={root_password} \
                             --set auth.password={password} \
                             --set auth.database={database}"])
ingress_file = Helper.replace_in_file(os.path.join(execution.templates_folder, "ingress", "ingress.yaml"), {
    'HOSTNAME': f'mysql-{namespace}.{execution.domain_name}'})
helm_chart.install_file(ingress_file,namespace)
ingress_port = execution.open_tcp_port_nginx('mysql-headless', 3306)
# connection_info = f'mysql: \n mysql.{namespace}.svc.cluster.local:3306\DB name: {database}\nusername: {username}\nroot password:{root_password}\npassword:{password}'
# Helper.write_connection_info(connection_info, execution.output_folder)
