import os
from fennec_core_dns.core_dns import CoreDNS
from fennec_executers.helm_executer import Helm
from fennec_execution.execution import Execution

execution = Execution(os.path.dirname(__file__))
kafka_url = execution.get_local_parameter('KAFKA_DNS_RECORD')
namespace = execution.get_local_parameter('NAMESPACE')
core_dns = CoreDNS(os.path.dirname(__file__))
core_dns.delete_records(f"{kafka_url}=kafka.{namespace}.svc.cluster.local")
kafka_chart = Helm(os.path.dirname(__file__), namespace=namespace, chart_name="kafka")
kafka_chart.uninstall_chart()
