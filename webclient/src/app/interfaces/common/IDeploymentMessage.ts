import { IDploymentProgress } from './IDeplopymentProgress';
import { ILogLine } from './ILogLine';


export interface IDeploymentMessage {
  logs: ILogLine[];
  progress?: IDploymentProgress;
  final?: true;
  error?: boolean;
  domainName: string;
  pageName: string;
  completeLog?: ILogLine[];

}
