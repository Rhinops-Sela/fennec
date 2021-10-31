import os
from fennec_executers.helm_executer import Helm
from fennec_execution.execution import Execution

execution = Execution(os.path.dirname(__file__))
namespace = execution.get_local_parameter('NAMESPACE')
execution.delete_tcp_port_nginx('mysql-headless',3306)
helm_chart = Helm(os.path.dirname(__file__), namespace=namespace, chart_name="mysql")
helm_chart.uninstall_chart()