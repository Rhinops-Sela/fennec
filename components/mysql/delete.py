import os
from fennec_executers.helm_executer import Helm

helm_chart = Helm(os.path.dirname(__file__), chart_name="mysql")
namespace = helm_chart.execution.get_local_parameter('NAMESPACE')
helm_chart.execution.delete_tcp_port_nginx('mysql-headless',3306)
helm_chart.uninstall_chart()