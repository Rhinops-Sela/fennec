import os
from fennec_executers.helm_executer import Helm
from fennec_nodegorup.nodegroup import Nodegroup

openvpn_chart = Helm(os.path.dirname(__file__), "openvpn")
template_path = os.path.join(
    openvpn_chart.execution.templates_folder, "vpn-ng-template.json")
nodegroup = Nodegroup(os.path.dirname(__file__), template_path)
nodegroup.create()

values_file_path = os.path.join(
    openvpn_chart.execution.execution_folder, "values.yaml")
openvpn_chart.install_file(file=os.path.join(os.path.dirname(
    __file__), "prerequisites", "openvpn-pv-claim.yaml"), namespace="openvpn")
openvpn_chart.create_namespace("openvpn")
openvpn_chart.install_chart(release_name="stable",
                            additional_values=[f"--values {values_file_path}"], timeout=600)
keygen_script_path = os.path.join(os.path.dirname(
    __file__), "keygen", "generate-client-key.sh")
openvpn_chart.execution.run_command(
    f'{keygen_script_path} "{openvpn_chart.execution.local_parameters["USERS"]}" openvpn openvpn {openvpn_chart.execution.output_folder} 2>&1')
