import os
from fennec_core_dns.core_dns import CoreDNS
from fennec_executers.helm_executer import Helm
from fennec_execution.execution import Execution

execution = Execution(os.path.dirname(__file__))
namespace = execution.get_local_parameter('NAMESPACE')
execution.delete_tcp_port_nginx('redis-headless',6379)
helm_chart = Helm(os.path.dirname(__file__), namespace=namespace, chart_name="redis")
helm_chart.uninstall_chart()
helm_chart.uninstall_folder(base_folder=execution.templates_folder ,folder='ui', namespace=namespace)