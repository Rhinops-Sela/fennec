import os
from fennec_executers.helm_executer import Helm

rabbitmq_chart = Helm(os.path.dirname(__file__), chart_name="rabbitmq")
rabbitmq_url = rabbitmq_chart.execution.get_local_parameter('RABBITMQ_DNS_RECORD')
namespace = rabbitmq_chart.execution.get_local_parameter('NAMESPACE')
rabbitmq_chart.execution.open_tcp_port_nginx(
    service_name='rabbitmq-headless', service_port=5672)
rabbitmq_chart.uninstall_chart()
