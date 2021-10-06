export interface IInput {
  controlType: string;
  tooltip: string;
  displayName: string;
  regexValidation?: string;
  errorMessage?: string;
  options?: string[];
  value?: any;
  defaultValue?: any;
  required?: boolean;
  serverValue: string;
  id?: string;
  global?: boolean;
  sub_group?: string;
  group_enabler_master?: string;
}
