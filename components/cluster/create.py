import os
from fennec_cluster.cluster import Cluster
from fennec_core_dns.core_dns import CoreDNS
from fennec_executers.helm_executer import Helm
from fennec_execution import execution
from fennec_helpers.helper import Helper
from fennec_nodegorup.nodegroup import Nodegroup

cluster = Cluster(os.path.dirname(__file__))
allow_skip = cluster.execution.get_local_parameter('SKIP_IF_EXISTS')
if not cluster.check_if_cluster_exists() or not allow_skip:
    cluster.create()
    # Install cert-manager
    cert_manater_chart = Helm(os.path.dirname(__file__), "cert-manager")
    values_file_path = os.path.join(
        cluster.execution.templates_folder, "05.cert-manager", "cert-manager_values.yaml")
    cert_manater_chart.install_chart(release_name="jetstack",  chart_url="https://charts.jetstack.io",
                                     additional_values=[f"--values {values_file_path}"],allow_skip=False)
    cluster.install_folder(folder='05.cert-manager/kubectl',
                           namespace="cert-manager")

    # Install HPA
    install_HPA = cluster.execution.get_local_parameter('INSTALL_CLUSTER_HPA')
    if install_HPA:
        hpa_instsllation = os.path.join(
            cluster.execution.templates_folder, "03.hpa", "hpa.yaml")
        cluster.create_namespace("horizontal-pod-scaler")
        cluster.install_file(hpa_instsllation, "horizontal-pod-scaler")

    # Install Cluster auto scaler
    install_cluster_autoscaler = cluster.execution.get_local_parameter(
        'INSTALL_CLUSTER_AUTOSCALER')
    if install_cluster_autoscaler:
        cluster_auto_scaler_chart = Helm(
            os.path.dirname(__file__), "cluster-autoscaler")
        values_file_path = os.path.join(
            cluster.execution.templates_folder, "04.cluster-autoscaler", "auto_scaler.yaml")
        cluster_auto_scaler_chart.install_chart(release_name="stable", chart_url="https://charts.helm.sh/stable",
                                                additional_values=[
                                                    f"--values {values_file_path}",
                                                    f"--set autoDiscovery.clusterName={cluster.execution.cluster_name}",
                                                    f"--set awsRegion={cluster.execution.cluster_region}",
                                                    "--version 7.0.0"
                                                ])
        # Install Nginx Controller
        install_ingress_controller = cluster.execution.get_local_parameter(
            'INSTALL_INGRESS_CONTROLER')
        if install_ingress_controller:
            cluster.install_folder(folder="06.nginx")

        # Install Cluster dashboard
        install_cluster_dashboard = cluster.execution.get_local_parameter(
        'INSTALL_CLUSTER_DASHBOARD')
    if install_cluster_dashboard:
        values_file_path = os.path.join(
            cluster.execution.templates_folder, "07.dashboard", "ingress.yaml")
        user_url = cluster.execution.get_local_parameter(
            'CLUSTER_DASHBOARD_URL')
        values_to_replace = {'CLUSTER_DASHBOARD_URL': f'{user_url}'}
        values_file_path_execution = Helper.replace_in_file(
            values_file_path, values_to_replace, 100)
        cluster.install_folder(folder="07.dashboard", namespace="kubernetes-dashboard")
        cluster.export_secret(secret_name="admin-user",
                                namespace="kube-system",
                                output_file_name="dashboard",
                                decode=True)
        ingress_address = cluster.get_ingress_address(
            'kubernetes-dashboard-ingress', 'kubernetes-dashboard')
        core_dns = CoreDNS(os.path.dirname(__file__))
        core_dns.add_records(f"{user_url}={ingress_address}")

# Install External DNS
install_cluster_external_dns = cluster.execution.get_local_parameter('ROUTE_53_ZONE_ID')
if install_cluster_external_dns:
    Helper.print_log("Will deploy external DNS component")
    deployment_file = os.path.join(
        cluster.execution.templates_folder, "09.external_dns", "deployment.yaml")
    deployment_file_execution = Helper.replace_in_file(deployment_file, {
        'CLUSTER_NAME': f'{cluster.execution.cluster_name}'})
    cluster.install_file(deployment_file_execution, namespace='external-dns')
install_vpn = cluster.execution.get_local_parameter('INSTALL_VPN')
if install_vpn:
    vpn_working_folder = os.path.join(
    cluster.execution.templates_folder, "08.openvpn")
    template_path = os.path.join(
            cluster.execution.templates_folder, "08.openvpn", "vpn-ng-template.json")
    nodegroup = Nodegroup(os.path.dirname(__file__), template_path)
    nodegroup.create()
    openvpn_chart = Helm(os.path.dirname(__file__), "openvpn")
    values_file_path = os.path.join(
        cluster.execution.templates_folder, "08.openvpn", "values.yaml")
    openvpn_chart.create_namespace("openvpn")
    openvpn_chart.install_file(file=os.path.join(
        vpn_working_folder, "prerequisites", "openvpn-pv-claim.yaml"), namespace="openvpn")
    openvpn_chart.install_chart(release_name="stable",
                                additional_values=[f"--values {values_file_path}"], timeout=600)
    keygen_script_path = os.path.join(
        vpn_working_folder, "keygen", "generate-client-key.sh")
    cluster.execution.run_command(
        f'{keygen_script_path} "{cluster.execution.local_parameters["USERS"]}" openvpn openvpn {cluster.execution.output_folder} 2>&1')
