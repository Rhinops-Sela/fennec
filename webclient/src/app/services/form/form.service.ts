import { Injectable } from '@angular/core';
import { FormControl, Validators, FormGroup } from '@angular/forms';
import { IInput } from 'src/app/interfaces/common/IInput';

@Injectable({
  providedIn: 'root',
})
export class FormService {
  constructor() {}
  /* toFormGroup(inputs: IInput[]) {
    const group: any = {};

    for (const input of inputs) {
      if (!this.checkIfEnabled(input, inputs)) {
        console.log('not enabled');
      } else {
        try {
          group[input.id] = input.regexValidation
            ? new FormControl(input.value || '', [
                Validators.pattern(input.regexValidation),
                Validators.required,
              ])
            : new FormControl(input.value || '');
        } catch (error) {
          console.log(error);
        }
      }
    }
    return new FormGroup(group);
  } */

  appendToFormGroup(inputs: IInput[], form?: FormGroup): FormGroup {
    if (!form) {
      form = new FormGroup({});
    }
    for (const input of inputs) {
      if (!this.checkIfEnabled(input, inputs, form)) {
        form.removeControl(input.id);
      } else {
        try {
          if (!form.controls[input.id]) {
            const formControl = input.regexValidation
              ? new FormControl(input.value || '', [
                  Validators.pattern(input.regexValidation),
                  Validators.required,
                ])
              : new FormControl(input.value || '');
            form.addControl(input.id, formControl);
          }
        } catch (error) {
          console.log(error);
        }
      }
    }
    return form;
  }

  checkIfEnabled(input: IInput, inputs: IInput[], form: FormGroup) {
    if (input.group_enabler_master) {
      return true;
    }
    if (input.sub_group) {
      const groupEnabler = inputs.find(
        (enabler) => enabler.group_enabler_master === input.sub_group
      );
      // groupEnabler.value = form.controls[groupEnabler.id].value;
      return groupEnabler?.value || false;
    } else {
      return true;
    }
  }
}
