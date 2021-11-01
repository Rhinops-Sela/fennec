import os
from fennec_core_dns.core_dns import CoreDNS
from fennec_executers.helm_executer import Helm
from fennec_helpers.helper import Helper

helm_chart = Helm(os.path.dirname(__file__), chart_name="dynamodb")
helm_chart.uninstall_chart()
