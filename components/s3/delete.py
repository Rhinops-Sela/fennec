import os
from fennec_executers.helm_executer import Helm

helm_chart = Helm(os.path.dirname(__file__), chart_name="localstack")
helm_chart.uninstall_chart()