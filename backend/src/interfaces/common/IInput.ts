export interface IInput {
  template?: any;
  controlType: string;
  tooltip: string;
  displayName: string;
  regexValidation?: string;
  allowEmpty?: string
  errorMessage?: string;
  options?: string[];
  value?: any;
  defaultValue?: any;
  required?: boolean;
  serverValue: string;
  id?: string;
  global?: boolean;
}
