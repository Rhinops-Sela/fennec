import { IInput } from './IInput';
import { ILogLine } from './ILogLine';

export interface IPage {
  name: string;
  displayName: string;
  image: string;
  description: string;
  inputs: IInput[];
  repeatable?: boolean;
  executer: string;
  valid?: boolean;
  id?: string;
  modified?: boolean;
  mandatory?: boolean;
  logs?: ILogLine[];
  icon?: string;
  deploymentIcon?: string;
  stderrFail?: boolean;
}
