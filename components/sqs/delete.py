import os
from fennec_core_dns.core_dns import CoreDNS
from fennec_executers.helm_executer import Helm
from fennec_execution.execution import Execution

execution = Execution(os.path.dirname(__file__))
sqs_url = execution.get_local_parameter('SQS_DNS_RECORD')
namespace = execution.get_local_parameter('NAMESPACE')
helm_chart = Helm(os.path.dirname(__file__), namespace=namespace, chart_name="sqs")
helm_chart.uninstall_chart()
core_dns = CoreDNS(os.path.dirname(__file__))
core_dns.delete_records(f"{sqs_url}=sqs-localstack.{namespace}.svc.cluster.local")
#helm_chart.delete_namespace(namespace)