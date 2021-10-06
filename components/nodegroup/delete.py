import os
from fennec_nodegorup.nodegroup import Nodegroup

working_folder = os.path.join(os.getcwd(), "nodegroup")
template_path = os.path.join(working_folder, "execution", "templates", "generic-nodegrpup.json")
nodegroup = Nodegroup(os.path.join(os.getcwd(), "nodegroup"), template_path)
nodegroup.delete()                            
