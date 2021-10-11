import os
from fennec_core_dns.core_dns import CoreDNS
from fennec_executers.helm_executer import Helm
from fennec_execution.execution import Execution
from fennec_helpers.helper import Helper
from fennec_nodegorup.nodegroup import Nodegroup
from fennec_executers.kubectl_executer import Kubectl

execution = Execution(os.path.dirname(__file__))
dynamodb_url = execution.get_local_parameter('DYNAMO_DNS_RECORD')
dynamodb_url = execution.get_local_parameter('DYNAMO_DNS_RECORD')
dynamodb_admin_url = execution.get_local_parameter('DYNAMO_ADMIN_DNS_RECORD')
namespace = execution.get_local_parameter('NAMESPACE')
template_path = os.path.join(
    execution.templates_folder, "dynamodb-ng-template.json")
nodegroup = Nodegroup(os.path.dirname(__file__), template_path)
nodegroup.create()

helm_chart = Helm(os.path.dirname(__file__), namespace=namespace, chart_name="localstack")
values_file_path = os.path.join(
    execution.execution_folder, "values.json")

values_file_object = Helper.file_to_object(values_file_path)
values_file_object['extraEnvVars'][0]['value'] = helm_chart.execution.cluster_region
execution_file = os.path.join(
    os.path.dirname(__file__), "dynamodb-execute.values.json")
Helper.to_json_file(values_file_object, execution_file)    

helm_chart.install_chart(release_name="localstack-charts",
                                  chart_url="https://localstack.github.io/helm-charts",
                                  deployment_name="dynamodb",
                                  additional_values=[f"--values {execution_file}"])
dynamodb_record = f"{dynamodb_url}=dynamodb-localstack.{namespace}.svc.cluster.local"                                 

kubectl = Kubectl(os.path.dirname(__file__))
kubectl.install_folder("admin", namespace=nodegroup.execution.get_local_parameter('NAMESPACE'))
admin_record  = f"{dynamodb_admin_url}=dynamodb-local-admin.{nodegroup.execution.get_local_parameter('NAMESPACE')}.svc.cluster.local"


core_dns = CoreDNS(os.path.dirname(__file__))
dns_records = f"{admin_record};{dynamodb_record}"
core_dns.add_records(dns_records)