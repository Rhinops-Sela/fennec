import os
from fennec_executers.helm_executer import Helm
from fennec_execution.execution import Execution

execution = Execution(os.path.dirname(__file__))
kafka_url = execution.get_local_parameter('KAFKA_DNS_RECORD')
namespace = execution.get_local_parameter('NAMESPACE')
execution.open_tcp_port_nginx(
    service_name='kafka-headless', service_port=9092)
kafka_chart = Helm(os.path.dirname(__file__),
                   namespace=namespace, chart_name="kafka")
kafka_chart.uninstall_chart()
