import os
from fennec_executers.helm_executer import Helm

helm_chart = Helm(os.path.dirname(__file__), chart_name="postgresql")
namespace = helm_chart.execution.get_local_parameter('NAMESPACE')
helm_chart.execution.delete_tcp_port_nginx('postgresql-headless',5432)
helm_chart.uninstall_chart()