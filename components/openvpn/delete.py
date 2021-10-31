import os
from fennec_executers.helm_executer import Helm
from fennec_nodegorup.nodegroup import Nodegroup

openvpn_chart = Helm(os.path.dirname(__file__), "openvpn")
template_path = os.path.join(
    openvpn_chart.execution.templates_folder, "vpn-ng-template.json")


openvpn_chart = Helm(os.path.dirname(__file__), "openvpn")
openvpn_chart.uninstall_file(os.path.join(os.path.dirname(__file__), "prerequisites", "openvpn-pv-claim.yaml"), "openvpn")
openvpn_chart.delete_namespace("openvpn")
nodegroup = Nodegroup(os.path.dirname(__file__), template_path)
nodegroup.delete()
