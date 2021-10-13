import os
from fennec_core_dns.core_dns import CoreDNS
from fennec_executers.helm_executer import Helm
from fennec_execution.execution import Execution
from fennec_helpers.helper import Helper

execution = Execution(os.path.dirname(__file__))
dynamodb_url = execution.get_local_parameter('DYNAMO_DNS_RECORD')
dynamodb_admin_url = execution.get_local_parameter('DYNAMO_ADMIN_DNS_RECORD')
namespace = execution.get_local_parameter('NAMESPACE')
helm_chart = Helm(os.path.dirname(__file__), namespace=namespace, chart_name="dynamodb")
helm_chart.uninstall_chart()

helm_chart.uninstall_folder(base_folder=execution.templates_folder ,folder='admin', namespace=namespace)
core_dns = CoreDNS(os.path.dirname(__file__))
dynamodb_record = f"{dynamodb_url}=dynamodb-localstack.{namespace}.svc.cluster.local"
admin_record = f"{dynamodb_admin_url}=dynamodb-local-admin.{execution.get_local_parameter('NAMESPACE')}.svc.cluster.local"
dns_records = f"{admin_record};{dynamodb_record}"
core_dns = CoreDNS(os.path.dirname(__file__))
core_dns.delete_records(dns_records)