import os
from fennec_executers.helm_executer import Helm
from fennec_execution.execution import Execution

from fennec_helpers.helper import Helper

datadog_chart = Helm(os.path.dirname(__file__))
values_file_path = os.path.join(
    datadog_chart.execution.execution_folder, "values.json")
values_file_object = Helper.file_to_object(values_file_path)
values_file_object['datadog']['apiKey'] = datadog_chart.execution.get_local_parameter('DD_API_KEY')
values_file_object['datadog']['appKey'] = datadog_chart.execution.get_local_parameter('DD_APP_KEY')
execution_file = os.path.join(
    os.path.dirname(__file__), "datadog-execute.values.json")
Helper.to_json_file(values_file_object, execution_file)
datadog_chart.install_chart(release_name="stable",
                            additional_values=[f"--values {execution_file}"])
