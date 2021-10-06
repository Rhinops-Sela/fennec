import { IDomain } from '../common/IDomain';

export interface IDeploymentInfo {
  domains: IDomain[];
  deleteMode: boolean;
  deploymentIdentifier?: string;
}
