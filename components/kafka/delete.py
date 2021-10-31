import os
from fennec_executers.helm_executer import Helm

kafka_chart = Helm(os.path.dirname(__file__), chart_name="kafka")
kafka_url = kafka_chart.execution.get_local_parameter('KAFKA_DNS_RECORD')
namespace = kafka_chart.execution.get_local_parameter('NAMESPACE')
kafka_chart.execution.open_tcp_port_nginx(
    service_name='kafka-headless', service_port=9092)
kafka_chart.uninstall_chart()
