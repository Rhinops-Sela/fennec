from fennec_executers.kubectl_executer import Kubectl
from fennec_helpers.helper import Helper


class Namespace:

    def __init__(self, kubectl: Kubectl) -> None:
        self.kubectl = kubectl
        self.execution = self.kubectl.execution

    def create(self, name: str):
        if self.execution.check_if_naemspace_exists(name):
            Helper.print_log(f"namespace: {name} already exsits, skipping")
            return
        self.kubectl.create_namespace(name)

    def delete(self, name: str, force=True):
        if not self.execution.check_if_naemspace_exists(name):
            Helper.print_log(f"namespace: {name} doesn't exsit, skipping")
            return
        delete = force
        if not force:
            delete = self.verify_empty_before_delete(name)
        if delete:
            self.kubectl.delete_namespace(name)
        else:
            Helper.print_log(f"Namespace {name} contains resources, skipp deleting")

    def verify_empty_before_delete(self, name: str) -> bool:
        objects_in_namespace = self.kubectl.get_all(name)
        return True if not objects_in_namespace else False
