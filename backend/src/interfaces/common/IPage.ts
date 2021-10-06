import { IInput } from './IInput';
export interface IPage {
  name: string;
  executer: string;
  global: boolean;
  displayName: string;
  image: string;
  description: string;
  inputs: IInput[];
  repeatable?: boolean;
  valid?: boolean;
  id?: string;
  modified?: boolean;
  mandatory?: boolean;
  stderrFail?: boolean;
}
