import os
from fennec_executers.helm_executer import Helm

kafka_chart = Helm(os.path.dirname(__file__), chart_name="mongodb")
kafka_url = kafka_chart.execution.get_local_parameter('MONGODB_DNS_RECORD')
namespace = kafka_chart.execution.get_local_parameter('NAMESPACE')
kafka_chart.uninstall_chart()
