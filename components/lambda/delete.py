import os
from fennec_core_dns.core_dns import CoreDNS
from fennec_executers.helm_executer import Helm

helm_chart = Helm(os.path.dirname(__file__), chart_name="lambda")
lambda_url = helm_chart.execution.get_local_parameter('LAMBDA_DNS_RECORD')
namespace = helm_chart.execution.get_local_parameter('NAMESPACE')
helm_chart.uninstall_chart()
core_dns = CoreDNS(os.path.dirname(__file__))
core_dns.delete_records(lambda_url)
#helm_chart.delete_namespace(namespace)