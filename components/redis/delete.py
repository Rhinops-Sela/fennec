import os
from fennec_core_dns.core_dns import CoreDNS
from fennec_executers.helm_executer import Helm

helm_chart = Helm(os.path.dirname(__file__), chart_name="redis")
namespace = helm_chart.execution.get_local_parameter('NAMESPACE')
helm_chart.execution.delete_tcp_port_nginx('redis-headless',6379)
helm_chart = Helm(os.path.dirname(__file__), namespace=namespace, chart_name="redis")
helm_chart.uninstall_chart()
helm_chart.uninstall_folder(base_folder=helm_chart.execution.templates_folder ,folder='ui', namespace=namespace)