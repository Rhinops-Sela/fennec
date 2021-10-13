from fennec_executers.kubectl_executer import Kubectl
from fennec_helpers import Helper


class Helm(Kubectl):
    def __init__(self, working_folder: str, namespace: str = "NAMESPACE", chart_name: str = "") -> None:
        Kubectl.__init__(self, working_folder)
        self.namespace_name = self.execution.local_parameters[
            namespace] if namespace in self.execution.local_parameters else namespace
        self.chart_name = chart_name if chart_name else self.namespace_name

    @property
    def installed(self) -> bool:
        command = "helm ls --all-namespaces -o json"
        installed_charts = self.execution.run_command(
            command, show_output=False).log
        for installed_chart in Helper.json_to_object(installed_charts):
            if installed_chart['name'] == self.chart_name and installed_chart['namespace'] == self.namespace_name:
                Helper.print_log(
                    f"chart: {self.chart_name} in namespace: {self.namespace_name} already installed, upgrading...")
                return True
        Helper.print_log(
            f"chart: {self.chart_name} in namespace: {self.namespace_name} not installed")
        return False

    def install_chart(self, release_name: str, chart_url: str = "", additional_values=[], timeout=300, deployment_name = ""):
        verb = "upgrade --install"
        self.execution.run_command(
            "helm repo add stable https://charts.helm.sh/stable")
        if chart_url:
            self.execution.run_command(
                f"helm repo add {release_name} {chart_url}")
        if not deployment_name:
            deployment_name = self.chart_name
        self.execution.run_command("helm repo update")
        self.create_namespace(self.namespace_name)
        install_command = f"helm {verb} --wait --timeout {timeout}s {deployment_name} {release_name}/{self.chart_name} -n {self.namespace_name} {self.combine_additoinal_values(additional_values)}"
        Helper.print_log("Installing Chart")
        self.execution.run_command(install_command)

    def uninstall_chart(self, delete_namespace=False):
        if self.installed:
            Helper.print_log("uninstalling...")
            uninstall_command = f"helm uninstall {self.chart_name} -n {self.namespace_name}"
            self.execution.run_command(uninstall_command)
            if delete_namespace:
                self.delete_namespace(self.namespace_name, force=False)
        else:
            Helper.print_log(f"skipping...")
