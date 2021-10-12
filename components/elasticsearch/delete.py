import os
from fennec_core_dns.core_dns import CoreDNS
from fennec_executers.helm_executer import Helm
from fennec_execution.execution import Execution

execution = Execution(os.path.dirname(__file__))
es_url = execution.get_local_parameter('ES_DNS_RECORD')

namespace = execution.get_local_parameter('NAMESPACE')
core_dns = CoreDNS(os.path.dirname(__file__))
core_dns.delete_records(f"{es_url}=elasticsearch-master.{namespace}.svc.cluster.local")
elasticsearch_chart = Helm(os.path.dirname(__file__), namespace=namespace, chart_name="elasticsearch")
elasticsearch_chart.uninstall_chart()
if execution.get_local_parameter('INSTALL_KIBANA'):
    kibana_url = execution.get_local_parameter('KIBANA_DNS_RECORD')
    core_dns.delete_records(f"{kibana_url}=kibana-kibana.{namespace}.svc.cluster.local")
    kibana_chart = Helm(os.path.dirname(__file__), namespace=namespace, chart_name="kibana")
    kibana_chart.uninstall_chart()


