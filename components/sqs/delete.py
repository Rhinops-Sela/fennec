import os
from fennec_core_dns.core_dns import CoreDNS
from fennec_executers.helm_executer import Helm
from fennec_execution.execution import Execution

execution = Execution(os.path.dirname(__file__))
redis_url = execution.local_parameters['SQS_DNS_RECORD']
namespace = execution.local_parameters['NAMESPACE']
helm_chart = Helm(os.path.dirname(__file__), namespace=namespace, chart_name="sqs")
helm_chart.uninstall_chart()
helm_chart.delete_namespace(namespace)